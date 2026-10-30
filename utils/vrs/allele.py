"""Generate a GA4GH VRS Allele, and its SequenceLocation, for a protein change.

Resolves `{protein}:{change}` (e.g. "NP_005219.2:p.L858R") with a locally running
variation-normalizer and emits `{"allele": ..., "sequence_location": ...}` shaped as
referenced/alleles.json and referenced/sequence_locations.json records. The allele's
`location` is a foreign key to the emitted sequence location. The protein's
SequenceReference must exist in referenced/sequence_references.json separately (see
utils.vrs.sequence_reference).

Usage:
    python -m utils.vrs.allele --protein NP_005219.2 --change p.L858R --gene EGFR \
        --transcript NM_005228.5
    python -m utils.vrs.allele --protein NP_005219.2 --change p.L858R --gene EGFR \
        --transcript NM_005228.5 --upsert-dir referenced
"""

import re

from utils.vrs import common

# Standard IUPAC 1-letter -> 3-letter amino acid codes.
AMINO_ACID_CODES = {
    "A": "Ala",
    "R": "Arg",
    "N": "Asn",
    "D": "Asp",
    "C": "Cys",
    "Q": "Gln",
    "E": "Glu",
    "G": "Gly",
    "H": "His",
    "I": "Ile",
    "L": "Leu",
    "K": "Lys",
    "M": "Met",
    "F": "Phe",
    "P": "Pro",
    "S": "Ser",
    "T": "Thr",
    "W": "Trp",
    "Y": "Tyr",
    "V": "Val",
}
SUBSTITUTION_PATTERN = re.compile(r"^p\.([A-Z])(\d+)([A-Z])$")


def allele_record(
    variation: dict,
    protein: str,
    change: str,
    gene: str | None = None,
    description: str | None = None,
) -> dict:
    """
    Builds a referenced/alleles.json record from a variation-normalizer variation.

    Args:
        variation (dict): A VRS Allele from the variation-normalizer's /to_vrs.
        protein (str): The RefSeq protein accession, e.g. "NP_005219.2".
        change (str): The short protein change, e.g. "p.L858R".
        gene (str | None): Gene symbol; adds a "{gene} {change}" alias when given.
        description (str | None): Overrides the generated description.

    Returns:
        dict: The allele record.
    """
    query = f"{protein}:{change}"
    three_letter_change = to_three_letter_hgvs_p(change)
    hgvs_p = f"{protein}:{three_letter_change}" if three_letter_change else None
    name = hgvs_p or query
    aliases = [query]
    if gene:
        aliases.append(f"{gene} {change}")
    if description is None:
        description = (
            f"VRS variation of {name}, generated with the VICC Variation Normalizer"
        )
    state = variation["state"]
    return {
        "id": variation["id"],
        "type": variation["type"],
        "name": name,
        "aliases": aliases,
        "description": description,
        "digest": variation["digest"],
        "hgvs.g": None,
        "hgvs.c": None,
        "hgvs.c_short": None,
        "hgvs.p": hgvs_p,
        "hgvs.p_short": change,
        "location": variation["location"]["id"],
        "state_type": state["type"],
        "state_sequence": state.get("sequence"),
        "state_length": state.get("length"),
        "state_repeat_subunit_length": state.get("repeatSubunitLength"),
    }


def build(
    protein: str,
    change: str,
    gene: str | None = None,
    transcript: str | None = None,
    description: str | None = None,
) -> dict:
    """
    Builds allele and sequence location records for a protein change.

    Args:
        protein (str): The RefSeq protein accession, e.g. "NP_005219.2".
        change (str): The short protein change, e.g. "p.L858R".
        gene (str | None): Gene symbol, used in aliases and descriptions.
        transcript (str | None): MANE Select transcript, used in the location
            description.
        description (str | None): Overrides the generated allele description.

    Returns:
        dict: `allele` and `sequence_location` records.
    """
    variation = common.to_vrs(f"{protein}:{change}")
    return {
        "allele": allele_record(
            variation=variation,
            protein=protein,
            change=change,
            gene=gene,
            description=description,
        ),
        "sequence_location": sequence_location_record(
            location=variation["location"],
            protein=protein,
            gene=gene,
            transcript=transcript,
        ),
    }


def sequence_location_record(
    location: dict,
    protein: str,
    gene: str | None = None,
    transcript: str | None = None,
) -> dict:
    """
    Builds a referenced/sequence_locations.json record from a variation's location.

    Args:
        location (dict): The `location` of a VRS Allele from the variation-normalizer.
        protein (str): The RefSeq protein accession, e.g. "NP_005219.2".
        gene (str | None): Gene symbol, used in the description.
        transcript (str | None): MANE Select transcript, used in the description.

    Returns:
        dict: The sequence location record.
    """
    description = (
        f"Amino acid position {location['end']} of the Refseq protein {protein}"
    )
    if gene and transcript:
        description += (
            f", which is the protein product of the MANE Select coding transcript for "
            f"{gene} (refseq:{transcript})"
        )
    refget_accession = location["sequenceReference"]["refgetAccession"]
    return {
        "id": location["id"],
        "type": location["type"],
        "name": None,
        "aliases": [],
        "description": f"{description}.",
        "digest": location["digest"],
        "sequenceReference": f"ga4gh:{refget_accession}",
        "start": location["start"],
        "end": location["end"],
        "sequence": location.get("sequence"),
    }


def to_three_letter_hgvs_p(change: str) -> str | None:
    """
    Converts a short protein substitution (e.g. "p.L858R") to 3-letter HGVS p. form
    (e.g. "p.Leu858Arg").

    Only simple substitutions (`p.<ref><pos><alt>`) are supported; deletions,
    insertions, and frameshifts (e.g. "p.I836del", "p.W288Cfs*12") return None.

    Args:
        change (str): A short protein change, e.g. "p.L858R".

    Returns:
        str | None: The 3-letter HGVS p. form, or None if not a simple substitution.
    """
    match = SUBSTITUTION_PATTERN.match(change)
    if not match:
        return None
    reference, position, alternate = match.groups()
    return f"p.{AMINO_ACID_CODES[reference]}{position}{AMINO_ACID_CODES[alternate]}"


def main(argv: list[str] | None = None) -> None:
    """
    Command line entry point.

    Args:
        argv (list[str] | None): Arguments; defaults to sys.argv.
    """
    parser = common.argument_parser(
        prog="python -m utils.vrs.allele",
        doc=__doc__,
    )
    parser.add_argument(
        "--protein",
        required=True,
        help="RefSeq protein accession, e.g. NP_005219.2",
    )
    parser.add_argument(
        "--change",
        required=True,
        help="short protein change, e.g. p.L858R",
    )
    parser.add_argument("--gene", help="gene symbol, for aliases and descriptions")
    parser.add_argument(
        "--transcript",
        help="MANE Select transcript accession, for the location description",
    )
    parser.add_argument(
        "--description",
        help="override the generated allele description",
    )
    common.add_output_arguments(
        parser,
        tables="alleles.json and sequence_locations.json",
    )
    args = parser.parse_args(argv)

    result = build(
        protein=args.protein,
        change=args.change,
        gene=args.gene,
        transcript=args.transcript,
        description=args.description,
    )
    common.emit(records=result, output=args.output)
    if args.upsert_dir:
        common.upsert_tables(
            tables={
                "alleles.json": [result["allele"]],
                "sequence_locations.json": [result["sequence_location"]],
            },
            directory=args.upsert_dir,
        )


if __name__ == "__main__":
    common.run_cli(main)
