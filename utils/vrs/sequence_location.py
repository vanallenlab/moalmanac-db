"""Generate a GA4GH VRS SequenceLocation record on a RefSeq sequence.

The location's identifier is computed locally with ga4gh.vrs; the accession is resolved
to its refget accession with a locally running variation-normalizer, and `--full-length`
reads the sequence length from a locally running seqrepo REST service.

Usage:
    python -m utils.vrs.sequence_location NM_005157.6 --full-length --gene ABL1
    python -m utils.vrs.sequence_location NP_005148.2 --full-length --gene ABL1 \
        --transcript NM_005157.6 --upsert-dir referenced
    python -m utils.vrs.sequence_location NP_005219.2 --start 857 --end 858 \
        --description "..."
"""

from utils.vrs import common


def build(
    accession: str,
    start: int,
    end: int,
    description: str | None = None,
    refget_accession: str | None = None,
    sequence: str | None = None,
) -> dict:
    """
    Builds a referenced/sequence_locations.json record for a span of a sequence.

    Args:
        accession (str): A RefSeq accession, e.g. "NM_005157.6".
        start (int): Inter-residue start coordinate.
        end (int): Inter-residue end coordinate.
        description (str | None): The record's description.
        refget_accession (str | None): The accession's refget accession; resolved with
            the variation-normalizer if None.
        sequence (str | None): The reference sequence at the location, if known.

    Returns:
        dict: The sequence location record.

    Raises:
        ValueError: If `start` is negative or not less than `end`.
    """
    if start < 0 or start >= end:
        raise ValueError(f"Invalid span [{start}, {end}) on {accession}")
    if refget_accession is None:
        refget_accession, _ = common.resolve_sequence(accession)
    return common.sequence_location_record(
        refget_accession=refget_accession,
        start=start,
        end=end,
        description=description,
        sequence=sequence,
    )


def build_full_length(
    accession: str,
    gene: str | None = None,
    transcript: str | None = None,
    description: str | None = None,
) -> dict:
    """
    Builds a sequence location spanning the full length of a sequence.

    Args:
        accession (str): A RefSeq accession, e.g. "NM_005157.6".
        gene (str | None): Gene symbol, used in NM_/NP_ descriptions.
        transcript (str | None): MANE Select transcript, used in NP_ descriptions.
        description (str | None): Overrides the generated description.

    Returns:
        dict: The sequence location record.
    """
    if description is None:
        description = full_length_description(
            accession=accession,
            gene=gene,
            transcript=transcript,
        )
    return build(
        accession=accession,
        start=0,
        end=common.sequence_length(accession),
        description=description,
    )


def full_length_description(
    accession: str,
    gene: str | None = None,
    transcript: str | None = None,
) -> str | None:
    """
    Builds the conventional description for a full-length gene sequence location.

    Args:
        accession (str): A RefSeq accession (NM_ or NP_).
        gene (str | None): Gene symbol.
        transcript (str | None): MANE Select transcript, required for NP_ descriptions.

    Returns:
        str | None: The description, or None if the required arguments are missing.
    """
    if accession.startswith("NM_") and gene:
        return (
            f"Sequence spanning the length of refseq:{accession}, the MANE Select "
            f"coding transcript for {gene}."
        )
    if accession.startswith("NP_") and gene and transcript:
        return (
            f"Sequence spanning the length of refseq:{accession}, the protein product "
            f"of the MANE Select coding transcript for {gene} (refseq:{transcript})."
        )
    return None


def main(argv: list[str] | None = None) -> None:
    """
    Command line entry point.

    Args:
        argv (list[str] | None): Arguments; defaults to sys.argv.
    """
    parser = common.argument_parser(
        prog="python -m utils.vrs.sequence_location",
        doc=__doc__,
    )
    parser.add_argument("accession", help="RefSeq accession, e.g. NM_005157.6")
    span = parser.add_mutually_exclusive_group(required=True)
    span.add_argument(
        "--full-length",
        action="store_true",
        help="span the full sequence, [0, length)",
    )
    span.add_argument("--start", type=int, help="inter-residue start coordinate")
    parser.add_argument("--end", type=int, help="inter-residue end coordinate")
    parser.add_argument("--gene", help="gene symbol, for full-length descriptions")
    parser.add_argument(
        "--transcript",
        help="MANE Select transcript accession, for NP_ full-length descriptions",
    )
    parser.add_argument("--description", help="override the generated description")
    common.add_output_arguments(parser, tables="sequence_locations.json")
    args = parser.parse_args(argv)

    if args.full_length:
        record = build_full_length(
            accession=args.accession,
            gene=args.gene,
            transcript=args.transcript,
            description=args.description,
        )
    else:
        if args.end is None:
            parser.error("--end is required with --start")
        record = build(
            accession=args.accession,
            start=args.start,
            end=args.end,
            description=args.description,
        )
    common.emit(records=record, output=args.output)
    if args.upsert_dir:
        common.upsert_tables(
            tables={"sequence_locations.json": [record]},
            directory=args.upsert_dir,
        )


if __name__ == "__main__":
    common.run_cli(main)
