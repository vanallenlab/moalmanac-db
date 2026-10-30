"""Shared service clients, record builders, and CLI helpers for utils.vrs scripts."""

import argparse
import collections.abc
import json
import os
import sys
import time

import requests
from ga4gh.core import ga4gh_identify
from ga4gh.vrs import models

from utils import read
from utils import write

VARIATION_NORMALIZER_URL = os.environ.get(
    "VARIATION_NORMALIZER_URL",
    "http://localhost:8001/variation",
)
SEQREPO_URL = os.environ.get("SEQREPO_URL", "http://localhost:5001/seqrepo/1")
EUTILS_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UCSC_URL = "https://api.genome.ucsc.edu"

TIMEOUT = 90
RETRIES = 3

EXIT_UNRESOLVED = 1
EXIT_SERVICE = 3
EPILOG = """\
Exit codes:
  0  success
  1  the input could not be resolved (e.g. an unknown accession or protein change)
  2  invalid arguments
  3  a service could not be reached or returned an error"""


def add_output_arguments(parser: argparse.ArgumentParser, tables: str) -> None:
    """
    Adds the `--output` and `--upsert-dir` arguments shared by every script.

    Args:
        parser (argparse.ArgumentParser): The parser to extend.
        tables (str): The referenced/ tables the script upserts into, for the help
            text, e.g. "sequence_references.json".
    """
    parser.add_argument(
        "--output",
        help="write the generated JSON to this file instead of stdout",
    )
    parser.add_argument(
        "--upsert-dir",
        help=(
            f"referenced/ directory to upsert the generated record(s) into, by id "
            f"({tables})"
        ),
    )


def argument_parser(prog: str, doc: str) -> argparse.ArgumentParser:
    """
    Builds a script's argument parser, showing its module docstring and exit codes.

    Args:
        prog (str): The program name, e.g. "python -m utils.vrs.allele".
        doc (str): The script's module docstring, including its Usage section.

    Returns:
        argparse.ArgumentParser: The parser.
    """
    return argparse.ArgumentParser(
        prog=prog,
        description=doc,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )


def efetch(accession: str, rettype: str, **params) -> str:
    """
    Fetches a nucleotide record from NCBI EFetch as text.

    Args:
        accession (str): A RefSeq nucleotide accession, e.g. "NM_005157.6".
        rettype (str): The EFetch return type, e.g. "gb" or "ft".
        **params: Additional EFetch parameters, e.g. `seq_start` and `seq_stop`.

    Returns:
        str: The response body.
    """
    response = get(
        f"{EUTILS_URL}/efetch.fcgi",
        params={
            "db": "nuccore",
            "id": accession,
            "rettype": rettype,
            "retmode": "text",
            **params,
        },
    )
    return response.text


def emit(records: dict | list[dict], output: str | None) -> None:
    """
    Writes generated record(s) to stdout or a file.

    Args:
        records (dict | list[dict]): The generated record or records.
        output (str | None): File to write the JSON to; stdout if None.
    """
    text = json.dumps(records, indent=2)
    if output:
        with open(output, "w") as fp:
            fp.write(text + "\n")
    else:
        print(text)


def esummary_protein(accession: str) -> dict:
    """
    Fetches the NCBI ESummary JSON for a protein accession.

    Args:
        accession (str): A RefSeq protein accession, e.g. "NP_005148.2".

    Returns:
        dict: The parsed ESummary response.
    """
    response = get(
        f"{EUTILS_URL}/esummary.fcgi",
        params={"db": "protein", "id": accession, "retmode": "json"},
    )
    return response.json()


def get(url: str, params: dict | None = None) -> requests.Response:
    """
    Sends a GET request, retrying on connection errors and 5xx responses.

    NCBI eutils in particular intermittently returns 500 for large requests that
    succeed on retry.

    Args:
        url (str): The URL to request.
        params (dict | None): Query parameters.

    Returns:
        requests.Response: The successful response.

    Raises:
        requests.HTTPError: If the final attempt returns an error status.
        requests.ConnectionError: If the final attempt cannot connect.
    """
    for attempt in range(1, RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=TIMEOUT)
        except (requests.ConnectionError, requests.Timeout):
            if attempt == RETRIES:
                raise
        else:
            if response.status_code < 500 or attempt == RETRIES:
                response.raise_for_status()
                return response
        time.sleep(2**attempt)
    raise AssertionError("unreachable")


def identify_sequence_location(
    refget_accession: str,
    start: int,
    end: int,
) -> tuple[str, str]:
    """
    Computes the GA4GH identifier and digest of a SequenceLocation.

    The identifier is a pure function of `start`, `end`, and the sequence reference's
    `refgetAccession`, so no data proxy is needed.

    Args:
        refget_accession (str): The sequence's refget accession, e.g. "SQ.w8Qg...".
        start (int): Inter-residue start coordinate.
        end (int): Inter-residue end coordinate.

    Returns:
        tuple[str, str]: The `ga4gh:SL.` identifier and its digest.
    """
    location = models.SequenceLocation(
        start=start,
        end=end,
        sequenceReference={
            "refgetAccession": refget_accession,
            "type": "SequenceReference",
        },
        type="SequenceLocation",
    )
    location_id = ga4gh_identify(location)
    return location_id, location_id.removeprefix("ga4gh:SL.")


def resolve_sequence(accession: str) -> tuple[str, list[str]]:
    """
    Resolves a RefSeq accession to its refget accession and aliases.

    Args:
        accession (str): A RefSeq accession, e.g. "NP_005219.2".

    Returns:
        tuple[str, list[str]]: The refget accession (e.g. "SQ.vyo5...") and the
            aliases returned by the variation-normalizer.

    Raises:
        ValueError: If no `ga4gh:` alias is returned.
    """
    aliases = translate_identifier(f"refseq:{accession}")
    ga4gh_id = next((alias for alias in aliases if alias.startswith("ga4gh:")), None)
    if ga4gh_id is None:
        raise ValueError(f"No ga4gh identifier found for refseq:{accession}")
    return ga4gh_id.removeprefix("ga4gh:"), aliases


def run_cli(main: collections.abc.Callable[[], None]) -> None:
    """
    Runs a script's entry point, turning expected failures into one-line errors.

    Agents and people read stderr to decide what to do next, so an unreachable service
    or an unresolvable input exits with a short `error:` line and a distinct exit code
    (see EPILOG) rather than a traceback.

    Args:
        main (collections.abc.Callable[[], None]): The script's entry point.
    """
    try:
        main()
    except (requests.ConnectionError, requests.Timeout) as e:
        url = e.request.url if e.request is not None else "a service"
        print(
            f"error: could not reach {url} ({type(e).__name__}). Start the service, "
            f"or set VARIATION_NORMALIZER_URL (now {VARIATION_NORMALIZER_URL}) or "
            f"SEQREPO_URL (now {SEQREPO_URL}) to where it runs.",
            file=sys.stderr,
        )
        sys.exit(EXIT_SERVICE)
    except requests.HTTPError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(EXIT_SERVICE)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(EXIT_UNRESOLVED)


def sequence_length(accession: str) -> int:
    """
    Gets a sequence's length from a locally running seqrepo REST service.

    Args:
        accession (str): A RefSeq accession, e.g. "NM_005157.6".

    Returns:
        int: The sequence length, in residues.
    """
    response = get(
        f"{SEQREPO_URL}/metadata/refseq:{accession}",
    )
    return response.json()["length"]


def sequence_location_record(
    refget_accession: str,
    start: int,
    end: int,
    description: str | None,
    sequence: str | None = None,
) -> dict:
    """
    Builds a referenced/sequence_locations.json record.

    Args:
        refget_accession (str): The sequence's refget accession, e.g. "SQ.w8Qg...".
        start (int): Inter-residue start coordinate.
        end (int): Inter-residue end coordinate.
        description (str | None): The record's description.
        sequence (str | None): The reference sequence at the location, if known.

    Returns:
        dict: The sequence location record.
    """
    location_id, digest = identify_sequence_location(
        refget_accession=refget_accession,
        start=start,
        end=end,
    )
    return {
        "id": location_id,
        "type": "SequenceLocation",
        "name": None,
        "aliases": [],
        "description": description,
        "digest": digest,
        "sequenceReference": f"ga4gh:{refget_accession}",
        "start": start,
        "end": end,
        "sequence": sequence,
    }


def to_vrs(query: str) -> dict:
    """
    Queries the variation-normalizer's /to_vrs endpoint.

    Args:
        query (str): A variation query, e.g. "NP_005219.2:p.L858R".

    Returns:
        dict: The first resolved VRS variation.

    Raises:
        ValueError: If the query resolves to no variation.
    """
    response = get(
        f"{VARIATION_NORMALIZER_URL}/to_vrs",
        params={"q": query},
    )
    variations = response.json().get("variations") or []
    if not variations:
        raise ValueError(f"variation-normalizer could not resolve {query}")
    return variations[0]


def translate_identifier(identifier: str) -> list[str]:
    """
    Queries the variation-normalizer's /translate_identifier endpoint.

    Args:
        identifier (str): A sequence identifier, e.g. "refseq:NM_005157.6".

    Returns:
        list[str]: Aliases of the identified sequence.
    """
    response = get(
        f"{VARIATION_NORMALIZER_URL}/translate_identifier",
        params={"identifier": identifier},
    )
    return response.json()["aliases"]


def ucsc_track(genome: str, track: str, chrom: str) -> list[dict]:
    """
    Fetches the records of a UCSC Genome Browser track for one chromosome.

    Args:
        genome (str): The UCSC genome, e.g. "hg38".
        track (str): The track name, e.g. "centromeres".
        chrom (str): The UCSC chromosome name, e.g. "chr5".

    Returns:
        list[dict]: The track's records on that chromosome.
    """
    response = get(
        f"{UCSC_URL}/getData/track",
        params={"genome": genome, "track": track, "chrom": chrom},
    )
    body = response.json()
    records = body[track]
    return records[chrom] if isinstance(records, dict) else records


def upsert_tables(tables: dict[str, list[dict]], directory: str) -> None:
    """
    Upserts records into several referenced/ tables, reporting outcomes on stderr.

    Args:
        tables (dict[str, list[dict]]): Table filename (e.g. "alleles.json") mapped
            to the records to upsert into it.
        directory (str): The referenced/ directory.
    """
    for filename, records in tables.items():
        path = os.path.join(directory, filename)
        for record_id, outcome in upsert_records(records=records, file=path).items():
            print(f"{outcome}: {record_id} -> {path}", file=sys.stderr)


def upsert_records(records: list[dict], file: str) -> dict[str, str]:
    """
    Upserts records into a referenced/ table by id, overwriting in place.

    Args:
        records (list[dict]): Records to upsert.
        file (str): Path to the referenced/ JSON table.

    Returns:
        dict[str, str]: Each record id mapped to "created", "updated", or "unchanged".
    """
    table = read.json_records(file=file)
    index = {record["id"]: i for i, record in enumerate(table)}
    status = {}
    for record in records:
        position = index.get(record["id"])
        if position is None:
            index[record["id"]] = len(table)
            table.append(record)
            status[record["id"]] = "created"
        elif table[position] == record:
            status[record["id"]] = "unchanged"
        else:
            table[position] = record
            status[record["id"]] = "updated"
    if any(outcome != "unchanged" for outcome in status.values()):
        write.records(data=table, file=file, quiet=True)
    return status
