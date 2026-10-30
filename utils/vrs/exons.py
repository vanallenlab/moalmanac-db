"""Generate per-exon GA4GH VRS SequenceLocations for a RefSeq transcript and its protein.

Parses the transcript's NCBI GenBank flat file (cached at datasources/refseq/{NM}.gb,
fetched and saved if missing) for `exon` and `CDS` features, and builds:
- one SequenceLocation per exon, in transcript coordinates;
- one SequenceLocation per CDS-overlapping exon, in protein coordinates;
- the protein's RefSeq Coding (GI resolved via NCBI ESummary, cached at
  datasources/refseq/{NP}.esummary.json); and
- a Mapping from the transcript's RefSeq coding to the protein's.

Protein coordinates are rounded outward, so a codon split across an exon-exon junction
belongs to both exons' protein locations (they may overlap by up to 2 residues). This
is deliberate and is noted in the affected locations' descriptions.

If the GenBank record has no `exon` features, the script exits non-zero rather than
deriving exon boundaries from the CDS alone, which would miss UTR-only exons.

Usage:
    python -m utils.vrs.exons --transcript NM_005157.6 --gene ABL1
    python -m utils.vrs.exons --transcript NM_005157.6 --gene ABL1 \
        --upsert-dir referenced
"""

import dataclasses
import json
import os
import re

from utils.vrs import common

DATASOURCE_DIR = os.path.join("datasources", "refseq")

FEATURE_PATTERN = re.compile(r"^ {5}(\S+)\s+(\S.*)$")
QUALIFIER_PATTERN = re.compile(r"^ {21}/(\w+)(?:=(.*))?$")
CONTINUATION_PATTERN = re.compile(r"^ {21}(\S.*)$")
SPAN_PATTERN = re.compile(r"<?(\d+)\.\.>?(\d+)")

ONE_SIDED_CAVEAT = (
    " This exon's protein location may share a codon boundary with the adjacent "
    "exon's protein location."
)
TWO_SIDED_CAVEAT = (
    " This exon's protein location shares a codon boundary with the adjacent exons "
    "on both sides."
)


class NoExonFeaturesError(ValueError):
    """Raised when a GenBank record has no `exon` features to take boundaries from."""


@dataclasses.dataclass
class GenBankTranscript:
    """
    Exon and CDS annotation parsed from a RefSeq transcript's GenBank flat file.

    Attributes:
        accession (str): The transcript accession, e.g. "NM_005157.6".
        exons (list[tuple[int, int, int]]): (exon number, start, end) per exon, in
            inter-residue transcript coordinates.
        cds_start (int): Inter-residue CDS start.
        cds_end (int): Inter-residue CDS end, including the stop codon.
        protein_accession (str | None): The CDS `protein_id`, e.g. "NP_005148.2".
        protein_length (int | None): Length of the CDS `translation`, in residues.
    """

    accession: str
    exons: list[tuple[int, int, int]]
    cds_start: int
    cds_end: int
    protein_accession: str | None
    protein_length: int | None


def build(
    transcript: str,
    gene: str | None = None,
    protein: str | None = None,
    transcript_refget_accession: str | None = None,
    protein_refget_accession: str | None = None,
    protein_gi: str | None = None,
    refetch: bool = False,
) -> dict:
    """
    Builds exon sequence locations, the protein Coding, and the NM-to-NP Mapping.

    Args:
        transcript (str): The MANE Select transcript accession, e.g. "NM_005157.6".
        gene (str | None): Gene symbol, used in descriptions.
        protein (str | None): The protein accession; taken from the CDS `protein_id`
            if None, and checked against it otherwise.
        transcript_refget_accession (str | None): The transcript's refget accession;
            resolved with the variation-normalizer if None.
        protein_refget_accession (str | None): The protein's refget accession;
            resolved with the variation-normalizer if None.
        protein_gi (str | None): The protein's NCBI GI; resolved with ESummary if None.
        refetch (bool): Re-download cached NCBI files even if present.

    Returns:
        dict: `cds_start`, `transcript_exons`, `protein_product_exons`, `coding`, and
            `mapping`.

    Raises:
        ValueError: If `protein` does not match the GenBank CDS `protein_id`.
    """
    parsed = parse_genbank(text=genbank_text(accession=transcript, refetch=refetch))
    if protein is None:
        protein = parsed.protein_accession
    elif parsed.protein_accession and protein != parsed.protein_accession:
        raise ValueError(
            f"{transcript} CDS protein_id is {parsed.protein_accession}, not {protein}",
        )
    if transcript_refget_accession is None:
        transcript_refget_accession, _ = common.resolve_sequence(transcript)
    if protein_refget_accession is None:
        protein_refget_accession, _ = common.resolve_sequence(protein)
    protein_length = parsed.protein_length or common.sequence_length(protein)
    if protein_gi is None:
        protein_gi = esummary_gi(accession=protein, refetch=refetch)

    gene_label = gene or transcript
    transcript_exons = [
        common.sequence_location_record(
            refget_accession=transcript_refget_accession,
            start=start,
            end=end,
            description=(
                f"Sequence within refseq:{transcript}, the MANE Select coding "
                f"transcript for {gene_label}, corresponding to Exon {number}."
            ),
        )
        for number, start, end in parsed.exons
    ]

    protein_spans = protein_exon_spans(
        exons=parsed.exons,
        cds_start=parsed.cds_start,
        protein_length=protein_length,
    )
    protein_product_exons = []
    for i, (number, start, end) in enumerate(protein_spans):
        overlaps_previous = i > 0 and protein_spans[i - 1][2] > start
        overlaps_next = i < len(protein_spans) - 1 and protein_spans[i + 1][1] < end
        if overlaps_previous and overlaps_next:
            caveat = TWO_SIDED_CAVEAT
        elif overlaps_previous or overlaps_next:
            caveat = ONE_SIDED_CAVEAT
        else:
            caveat = ""
        protein_product_exons.append(
            common.sequence_location_record(
                refget_accession=protein_refget_accession,
                start=start,
                end=end,
                description=(
                    f"Sequence within refseq:{protein}, the protein product of the "
                    f"MANE Select coding transcript for {gene_label} "
                    f"(refseq:{transcript}), corresponding to Exon {number}.{caveat}"
                ),
            ),
        )

    return {
        "cds_start": parsed.cds_start,
        "transcript_exons": transcript_exons,
        "protein_product_exons": protein_product_exons,
        "coding": {
            "id": f"coding:refseq:{protein}",
            "code": protein,
            "system": "https://www.ncbi.nlm.nih.gov/protein",
            "iris": [f"https://www.ncbi.nlm.nih.gov/protein/{protein_gi}"],
        },
        "mapping": {
            "id": f"map:refseq:{transcript}::refseq:{protein}",
            "primary_coding_id": f"coding:refseq:{transcript}",
            "coding_id": f"coding:refseq:{protein}",
            "relation": "relatedMatch",
        },
    }


def esummary_gi(accession: str, refetch: bool = False) -> str:
    """
    Gets a protein's NCBI GI, caching the raw ESummary JSON in datasources/refseq/.

    Args:
        accession (str): A RefSeq protein accession, e.g. "NP_005148.2".
        refetch (bool): Re-download even if a cached file exists.

    Returns:
        str: The GI number.
    """
    path = os.path.join(DATASOURCE_DIR, f"{accession}.esummary.json")
    if refetch or not os.path.exists(path):
        body = common.esummary_protein(accession)
        with open(path, "w") as fp:
            json.dump(body, fp, separators=(",", ":"))
            fp.write("\n")
    with open(path) as fp:
        body = json.load(fp)
    return body["result"]["uids"][0]


def genbank_text(accession: str, refetch: bool = False) -> str:
    """
    Reads a transcript's GenBank flat file, fetching and caching it if needed.

    Args:
        accession (str): A RefSeq transcript accession, e.g. "NM_005157.6".
        refetch (bool): Re-download even if a cached file exists.

    Returns:
        str: The GenBank flat file text.
    """
    path = os.path.join(DATASOURCE_DIR, f"{accession}.gb")
    if refetch or not os.path.exists(path):
        text = common.efetch(accession=accession, rettype="gb")
        with open(path, "w") as fp:
            fp.write(text)
    with open(path) as fp:
        return fp.read()


def parse_genbank(text: str) -> GenBankTranscript:
    """
    Parses exon and CDS features from a GenBank flat file.

    GenBank's 1-based inclusive `start..end` becomes inter-residue `[start - 1, end)`.
    Exons are numbered by their `/number` qualifier when present, else by order.

    Args:
        text (str): GenBank flat file text.

    Returns:
        GenBankTranscript: The parsed annotation.

    Raises:
        NoExonFeaturesError: If the record has no `exon` features.
        ValueError: If the record has no CDS feature.
    """
    accession = re.search(r"^VERSION\s+(\S+)", text, re.MULTILINE).group(1)
    features = []
    in_features = False
    for line in text.splitlines():
        if line.startswith("FEATURES"):
            in_features = True
            continue
        if not in_features:
            continue
        if line.startswith("ORIGIN") or (line and not line.startswith(" ")):
            break
        match = FEATURE_PATTERN.match(line)
        if match:
            features.append({"key": match.group(1), "location": match.group(2)})
            continue
        qualifier = QUALIFIER_PATTERN.match(line)
        if qualifier:
            value = (qualifier.group(2) or "").strip('"')
            features[-1][qualifier.group(1)] = value
            features[-1]["_last"] = qualifier.group(1)
            continue
        continuation = CONTINUATION_PATTERN.match(line)
        if continuation and features:
            last = features[-1].get("_last", "location")
            separator = "" if last in ("location", "translation") else " "
            features[-1][last] += separator + continuation.group(1).strip('"')

    exon_features = [feature for feature in features if feature["key"] == "exon"]
    if not exon_features:
        raise NoExonFeaturesError(
            f"{accession} has no exon features; review manually rather than deriving "
            "exon boundaries from the CDS alone",
        )
    exons = []
    for i, feature in enumerate(exon_features, start=1):
        start, end = span_of(feature["location"])
        exons.append((int(feature.get("number") or i), start, end))

    cds = next((feature for feature in features if feature["key"] == "CDS"), None)
    if cds is None:
        raise ValueError(f"{accession} has no CDS feature")
    cds_start, cds_end = span_of(cds["location"])
    translation = cds.get("translation")

    return GenBankTranscript(
        accession=accession,
        exons=exons,
        cds_start=cds_start,
        cds_end=cds_end,
        protein_accession=cds.get("protein_id"),
        protein_length=len(translation) if translation else None,
    )


def protein_exon_spans(
    exons: list[tuple[int, int, int]],
    cds_start: int,
    protein_length: int,
) -> list[tuple[int, int, int]]:
    """
    Projects transcript exons onto protein coordinates.

    Exons entirely in the 5' UTR, or in the 3' UTR/stop codon, are dropped. Coordinates
    are rounded outward, so exons sharing a split codon overlap.

    Args:
        exons (list[tuple[int, int, int]]): (number, start, end) in transcript
            inter-residue coordinates.
        cds_start (int): Inter-residue CDS start.
        protein_length (int): Protein length, in residues.

    Returns:
        list[tuple[int, int, int]]: (number, start, end) in protein inter-residue
            coordinates.

    Raises:
        ValueError: If the projected exons don't span exactly [0, protein_length).
    """
    coding_end = cds_start + 3 * protein_length
    spans = []
    for number, start, end in exons:
        if end <= cds_start or start >= coding_end:
            continue
        relative_start = max(start, cds_start) - cds_start
        relative_end = min(end, coding_end) - cds_start
        spans.append((number, relative_start // 3, -(-relative_end // 3)))
    if not spans or spans[0][1] != 0 or spans[-1][2] != protein_length:
        raise ValueError(
            f"Protein exons do not span [0, {protein_length}): {spans}",
        )
    return spans


def span_of(location: str) -> tuple[int, int]:
    """
    Converts a GenBank location (e.g. "194..3586" or "join(1..5,9..20)") to an
    inter-residue span covering it.

    Args:
        location (str): A GenBank feature location on the forward strand.

    Returns:
        tuple[int, int]: The inter-residue [start, end).

    Raises:
        ValueError: If the location is complemented or has no ranges.
    """
    if "complement" in location:
        raise ValueError(f"Unsupported complement location: {location}")
    ranges = [(int(a), int(b)) for a, b in SPAN_PATTERN.findall(location)]
    if not ranges:
        raise ValueError(f"Unsupported location: {location}")
    return ranges[0][0] - 1, ranges[-1][1]


def main(argv: list[str] | None = None) -> None:
    """
    Command line entry point.

    Args:
        argv (list[str] | None): Arguments; defaults to sys.argv.
    """
    parser = common.argument_parser(
        prog="python -m utils.vrs.exons",
        doc=__doc__,
    )
    parser.add_argument(
        "--transcript",
        required=True,
        help="MANE Select transcript accession, e.g. NM_005157.6",
    )
    parser.add_argument(
        "--protein",
        help="protein accession; defaults to the GenBank CDS protein_id",
    )
    parser.add_argument("--gene", help="gene symbol, for descriptions")
    parser.add_argument(
        "--refetch",
        action="store_true",
        help="re-download cached NCBI files in datasources/refseq/",
    )
    common.add_output_arguments(
        parser,
        tables="sequence_locations.json, codings.json, and mappings.json",
    )
    args = parser.parse_args(argv)

    result = build(
        transcript=args.transcript,
        gene=args.gene,
        protein=args.protein,
        refetch=args.refetch,
    )
    common.emit(records=result, output=args.output)
    if args.upsert_dir:
        common.upsert_tables(
            tables={
                "sequence_locations.json": result["transcript_exons"]
                + result["protein_product_exons"],
                "codings.json": [result["coding"]],
                "mappings.json": [result["mapping"]],
            },
            directory=args.upsert_dir,
        )


if __name__ == "__main__":
    common.run_cli(main)
