"""Generate a GA4GH VRS SequenceReference record for a RefSeq accession.

Resolves the accession's refget identifier and Ensembl alias with a locally running
variation-normalizer. `moleculeType` and `residueAlphabet` are inferred from the
accession prefix (NM_ -> mRNA/na, NP_ -> protein/aa, NC_ -> genomic/na).

Usage:
    python -m utils.vrs.sequence_reference NM_005157.6 --gene ABL1
    python -m utils.vrs.sequence_reference NP_005148.2 --gene ABL1 \
        --transcript NM_005157.6
    python -m utils.vrs.sequence_reference NC_000005.10 --build GRCh38 --chromosome 5 \
        --upsert-dir referenced
"""

from utils.vrs import common

MOLECULE_TYPES = {
    "NC_": ("genomic", "na"),
    "NM_": ("mRNA", "na"),
    "NP_": ("protein", "aa"),
}


def build(
    accession: str,
    gene: str | None = None,
    transcript: str | None = None,
    genome_build: str | None = None,
    chromosome: str | None = None,
    description: str | None = None,
) -> dict:
    """
    Builds a referenced/sequence_references.json record for a RefSeq accession.

    Args:
        accession (str): A RefSeq accession (NM_, NP_, or NC_), e.g. "NP_005219.2".
        gene (str | None): Gene symbol, used in NM_/NP_ descriptions.
        transcript (str | None): The MANE Select transcript accession, used in NP_
            descriptions.
        genome_build (str | None): Genome build (GRCh38 or GRCh37), used in NC_ descriptions.
        chromosome (str | None): Chromosome name, used in NC_ descriptions.
        description (str | None): Overrides the generated description.

    Returns:
        dict: The sequence reference record.
    """
    molecule_type, residue_alphabet = molecule_type_of(accession)
    refget_accession, aliases = common.resolve_sequence(accession)
    ga4gh_id = f"ga4gh:{refget_accession}"
    record_aliases = [ga4gh_id, f"refseq:{accession}"]
    ensembl = ensembl_alias(aliases)
    if ensembl:
        record_aliases.append(ensembl)

    if description is None:
        description = default_description(
            accession=accession,
            gene=gene,
            transcript=transcript,
            genome_build=genome_build,
            chromosome=chromosome,
        )

    return {
        "id": ga4gh_id,
        "type": "SequenceReference",
        "name": accession,
        "aliases": sorted(record_aliases),
        "description": description,
        "moleculeType": molecule_type,
        "refgetAccession": refget_accession,
        "residueAlphabet": residue_alphabet,
    }


def default_description(
    accession: str,
    gene: str | None = None,
    transcript: str | None = None,
    genome_build: str | None = None,
    chromosome: str | None = None,
) -> str | None:
    """
    Builds the conventional description for a sequence reference.

    Args:
        accession (str): A RefSeq accession (NM_, NP_, or NC_).
        gene (str | None): Gene symbol, required for NM_/NP_ descriptions.
        transcript (str | None): MANE Select transcript, required for NP_ descriptions.
        genome_build (str | None): Genome build, required for NC_ descriptions.
        chromosome (str | None): Chromosome name, required for NC_ descriptions.

    Returns:
        str | None: The description, or None if the required arguments are missing.
    """
    if accession.startswith("NM_") and gene:
        return (
            f"The MANE Select coding transcript for {gene}, corresponding to the "
            f"Refseq transcript accession {accession}."
        )
    if accession.startswith("NP_") and gene and transcript:
        return (
            f"The protein product of the MANE Select coding transcript for {gene} "
            f"(refseq:{transcript}), corresponding to the Refseq protein accession "
            f"{accession}."
        )
    if accession.startswith("NC_") and genome_build and chromosome:
        return f"{genome_build} chromosome {chromosome} (RefSeq {accession})."
    return None


def ensembl_alias(aliases: list[str]) -> str | None:
    """
    Finds the lowercase-prefixed Ensembl alias, if any.

    Not every RefSeq sequence is cross-referenced to Ensembl in SeqRepo; when absent,
    the alias is omitted rather than fabricated.

    Args:
        aliases (list[str]): Aliases from the variation-normalizer.

    Returns:
        str | None: The alias beginning with "ensembl:", or None.
    """
    return next((alias for alias in aliases if alias.startswith("ensembl:")), None)


def molecule_type_of(accession: str) -> tuple[str, str]:
    """
    Infers `moleculeType` and `residueAlphabet` from a RefSeq accession prefix.

    Args:
        accession (str): A RefSeq accession, e.g. "NP_005219.2".

    Returns:
        tuple[str, str]: The molecule type and residue alphabet.

    Raises:
        ValueError: If the accession prefix is not NC_, NM_, or NP_.
    """
    for prefix, values in MOLECULE_TYPES.items():
        if accession.startswith(prefix):
            return values
    raise ValueError(
        f"Unsupported accession {accession}; expected one of {list(MOLECULE_TYPES)}",
    )


def main(argv: list[str] | None = None) -> None:
    """
    Command line entry point.

    Args:
        argv (list[str] | None): Arguments; defaults to sys.argv.
    """
    parser = common.argument_parser(
        prog="python -m utils.vrs.sequence_reference",
        doc=__doc__,
    )
    parser.add_argument("accession", help="RefSeq accession (NM_, NP_, or NC_)")
    parser.add_argument("--gene", help="gene symbol, for NM_/NP_ descriptions")
    parser.add_argument(
        "--transcript",
        help="MANE Select transcript accession, for NP_ descriptions",
    )
    parser.add_argument(
        "--build",
        choices=["GRCh38", "GRCh37"],
        help="genome build, for NC_ descriptions",
    )
    parser.add_argument("--chromosome", help="chromosome, for NC_ descriptions")
    parser.add_argument("--description", help="override the generated description")
    common.add_output_arguments(parser, tables="sequence_references.json")
    args = parser.parse_args(argv)

    record = build(
        accession=args.accession,
        gene=args.gene,
        transcript=args.transcript,
        genome_build=args.build,
        chromosome=args.chromosome,
        description=args.description,
    )
    common.emit(records=record, output=args.output)
    if args.upsert_dir:
        common.upsert_tables(
            tables={"sequence_references.json": [record]},
            directory=args.upsert_dir,
        )


if __name__ == "__main__":
    common.run_cli(main)
