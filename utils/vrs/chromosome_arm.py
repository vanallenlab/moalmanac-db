"""Generate a GA4GH VRS SequenceLocation spanning a chromosome arm.

The p arm spans [0, centromere start) and the q arm spans [centromere end, chromosome
length), in inter-residue coordinates on the chromosome's RefSeq (NC_) accession.

Centromere boundaries:
- GRCh38: a rough window from UCSC's hg38 `centromeres` track, confirmed against the
  `centromere` feature of NCBI's live RefSeq annotation (efetch feature table). NCBI is
  authoritative; a disagreement of more than 50 kb is reported on stderr.
- GRCh37: the `centromere` entry of UCSC's hg19 `gap` track (no NCBI cross-check).

Requires internet access (NCBI eutils, UCSC API), a locally running seqrepo REST service
for the chromosome length, and a locally running variation-normalizer for the refget
accession.

Usage:
    python -m utils.vrs.chromosome_arm --chromosome 5 --arm q --build GRCh38
    python -m utils.vrs.chromosome_arm --chromosome 5 --arm q --build GRCh38 \
        --upsert-dir referenced
"""

import sys

from utils.vrs import common
from utils.vrs import sequence_location

# RefSeq chromosome accessions: {chromosome: (GRCh38, GRCh37)}
CHROMOSOME_ACCESSIONS = {
    "1": ("NC_000001.11", "NC_000001.10"),
    "2": ("NC_000002.12", "NC_000002.11"),
    "3": ("NC_000003.12", "NC_000003.11"),
    "4": ("NC_000004.12", "NC_000004.11"),
    "5": ("NC_000005.10", "NC_000005.9"),
    "6": ("NC_000006.12", "NC_000006.11"),
    "7": ("NC_000007.14", "NC_000007.13"),
    "8": ("NC_000008.11", "NC_000008.10"),
    "9": ("NC_000009.12", "NC_000009.11"),
    "10": ("NC_000010.11", "NC_000010.10"),
    "11": ("NC_000011.10", "NC_000011.9"),
    "12": ("NC_000012.12", "NC_000012.11"),
    "13": ("NC_000013.11", "NC_000013.10"),
    "14": ("NC_000014.9", "NC_000014.8"),
    "15": ("NC_000015.10", "NC_000015.9"),
    "16": ("NC_000016.10", "NC_000016.9"),
    "17": ("NC_000017.11", "NC_000017.10"),
    "18": ("NC_000018.10", "NC_000018.9"),
    "19": ("NC_000019.10", "NC_000019.9"),
    "20": ("NC_000020.11", "NC_000020.10"),
    "21": ("NC_000021.9", "NC_000021.8"),
    "22": ("NC_000022.11", "NC_000022.10"),
    "X": ("NC_000023.11", "NC_000023.10"),
    "Y": ("NC_000024.10", "NC_000024.9"),
}
BUILDS = ("GRCh38", "GRCh37")
NCBI_WINDOW_PADDING = 500_000
DISAGREEMENT_THRESHOLD = 50_000


def accession_for(chromosome: str, genome_build: str) -> str:
    """
    Looks up a chromosome's RefSeq accession on a genome build.

    Args:
        chromosome (str): Chromosome name, e.g. "5" or "X".
        genome_build (str): "GRCh38" or "GRCh37".

    Returns:
        str: The RefSeq accession, e.g. "NC_000005.10".
    """
    return CHROMOSOME_ACCESSIONS[chromosome][BUILDS.index(genome_build)]


def arm_description(
    chromosome: str,
    arm: str,
    genome_build: str,
    accession: str,
) -> str:
    """
    Builds the conventional description for a chromosome arm sequence location.

    Args:
        chromosome (str): Chromosome name, e.g. "5".
        arm (str): "p" or "q".
        genome_build (str): "GRCh38" or "GRCh37".
        accession (str): The chromosome's RefSeq accession.

    Returns:
        str: The description.
    """
    extent = (
        "from the start of the chromosome to the start of the centromere"
        if arm == "p"
        else "from the end of the centromere to the end of the chromosome"
    )
    return f"The {arm} arm of {genome_build} chromosome {chromosome} ({accession}), {extent}."


def arm_span(
    arm: str,
    centromere: tuple[int, int],
    chromosome_length: int,
) -> tuple[int, int]:
    """
    Computes an arm's inter-residue span from the centromere boundaries.

    Args:
        arm (str): "p" or "q".
        centromere (tuple[int, int]): Inter-residue centromere [start, end).
        chromosome_length (int): Length of the chromosome.

    Returns:
        tuple[int, int]: The arm's [start, end).
    """
    if arm == "p":
        return 0, centromere[0]
    return centromere[1], chromosome_length


def build(
    chromosome: str,
    arm: str,
    genome_build: str,
    description: str | None = None,
) -> dict:
    """
    Builds a referenced/sequence_locations.json record spanning a chromosome arm.

    Args:
        chromosome (str): Chromosome name, e.g. "5".
        arm (str): "p" or "q".
        genome_build (str): "GRCh38" or "GRCh37".
        description (str | None): Overrides the generated description.

    Returns:
        dict: The sequence location record.
    """
    accession = accession_for(chromosome=chromosome, genome_build=genome_build)
    centromere = (
        centromere_grch38(chromosome=chromosome, accession=accession)
        if genome_build == "GRCh38"
        else centromere_grch37(chromosome=chromosome)
    )
    start, end = arm_span(
        arm=arm,
        centromere=centromere,
        chromosome_length=common.sequence_length(accession),
    )
    if description is None:
        description = arm_description(
            chromosome=chromosome,
            arm=arm,
            genome_build=genome_build,
            accession=accession,
        )
    return sequence_location.build(
        accession=accession,
        start=start,
        end=end,
        description=description,
    )


def centromere_grch37(chromosome: str) -> tuple[int, int]:
    """
    Gets a GRCh37 centromere span from UCSC's hg19 gap track.

    Args:
        chromosome (str): Chromosome name, e.g. "5".

    Returns:
        tuple[int, int]: Inter-residue centromere [start, end).

    Raises:
        ValueError: If the track has no centromere gap on this chromosome.
    """
    gaps = common.ucsc_track(genome="hg19", track="gap", chrom=f"chr{chromosome}")
    centromeres = [gap for gap in gaps if gap.get("type") == "centromere"]
    if len(centromeres) != 1:
        raise ValueError(
            f"Expected 1 centromere gap on hg19 chr{chromosome}, "
            f"found {len(centromeres)}",
        )
    return centromeres[0]["chromStart"], centromeres[0]["chromEnd"]


def centromere_grch38(chromosome: str, accession: str) -> tuple[int, int]:
    """
    Gets a GRCh38 centromere span, confirmed against NCBI's RefSeq annotation.

    UCSC's hg38 centromeres track only provides a rough window (it has been observed
    stale); the NCBI feature table fetched over that window is authoritative.

    Args:
        chromosome (str): Chromosome name, e.g. "5".
        accession (str): The chromosome's GRCh38 RefSeq accession.

    Returns:
        tuple[int, int]: Inter-residue centromere [start, end).
    """
    segments = common.ucsc_track(
        genome="hg38",
        track="centromeres",
        chrom=f"chr{chromosome}",
    )
    rough_start = min(segment["chromStart"] for segment in segments)
    rough_end = max(segment["chromEnd"] for segment in segments)

    seq_start = max(1, rough_start - NCBI_WINDOW_PADDING)
    feature_table = common.efetch(
        accession=accession,
        rettype="ft",
        seq_start=seq_start,
        seq_stop=rough_end + NCBI_WINDOW_PADDING,
    )
    start, end = parse_centromere_feature(
        feature_table=feature_table,
        seq_start=seq_start,
    )

    if (
        abs(start - rough_start) > DISAGREEMENT_THRESHOLD
        or abs(end - rough_end) > DISAGREEMENT_THRESHOLD
    ):
        print(
            f"warning: UCSC hg38 centromere window [{rough_start}, {rough_end}) for "
            f"chr{chromosome} differs from NCBI [{start}, {end}) by more than "
            f"{DISAGREEMENT_THRESHOLD} bp; using NCBI.",
            file=sys.stderr,
        )
    return start, end


def parse_centromere_feature(feature_table: str, seq_start: int) -> tuple[int, int]:
    """
    Parses the centromere feature from an NCBI feature table fetched over a window.

    Feature table coordinates are 1-based, inclusive, and relative to `seq_start`.

    Args:
        feature_table (str): NCBI efetch `rettype=ft` text.
        seq_start (int): The 1-based `seq_start` the feature table was fetched with.

    Returns:
        tuple[int, int]: Absolute inter-residue centromere [start, end).

    Raises:
        ValueError: If no centromere feature is present.
    """
    positions = []
    in_centromere = False
    for line in feature_table.splitlines():
        if not line or line.startswith(">") or line.startswith("\t"):
            continue
        columns = line.split("\t")
        if len(columns) >= 3 and columns[2]:
            in_centromere = columns[2] == "centromere"
        if in_centromere:
            positions.extend(
                int(value.strip("<>")) for value in columns[:2] if value.strip()
            )
    if not positions:
        raise ValueError("No centromere feature found in NCBI feature table")
    first = seq_start + min(positions) - 1
    last = seq_start + max(positions) - 1
    return first - 1, last


def main(argv: list[str] | None = None) -> None:
    """
    Command line entry point.

    Args:
        argv (list[str] | None): Arguments; defaults to sys.argv.
    """
    parser = common.argument_parser(
        prog="python -m utils.vrs.chromosome_arm",
        doc=__doc__,
    )
    parser.add_argument(
        "--chromosome",
        required=True,
        choices=list(CHROMOSOME_ACCESSIONS),
    )
    parser.add_argument("--arm", required=True, choices=["p", "q"])
    parser.add_argument("--build", required=True, choices=BUILDS)
    parser.add_argument("--description", help="override the generated description")
    common.add_output_arguments(parser, tables="sequence_locations.json")
    args = parser.parse_args(argv)

    record = build(
        chromosome=args.chromosome,
        arm=args.arm,
        genome_build=args.build,
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
