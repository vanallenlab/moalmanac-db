"""Download the GenBank flat file for a RefSeq transcript.

Fetches the GenBank flat file for the given versioned RefSeq transcript accession
from NCBI EFetch and writes it to datasources/refseq/{accession}.gb.

Usage: python datasources/scripts/download_refseq_transcript_genbank.py --accession NM_005228.5
"""

import argparse
import os
import pathlib
import re

import requests

EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

ACCESSION_PATTERN = re.compile(r"^[NX][MR]_\d+\.\d+$")
DATASOURCES_PATH = pathlib.Path("datasources") / "refseq"
TIMEOUT = 90


def download_genbank(accession: str) -> str:
    """
    Downloads the GenBank flat file for a RefSeq transcript.

    Args:
        accession (str): Versioned RefSeq transcript accession, e.g. "NM_005228.5".

    Raises:
        requests.HTTPError: If NCBI EFetch responds with an error status.
        ValueError: If the accession is not a versioned RefSeq transcript accession,
            or if NCBI EFetch returns no GenBank record for it.

    Returns:
        str: The GenBank flat file, as text.
    """
    if not ACCESSION_PATTERN.match(accession):
        raise ValueError(
            "accession must be a versioned RefSeq transcript accession such as "
            f"'NM_005228.5', got {accession!r}",
        )

    params = {
        "db": "nuccore",
        "id": accession,
        "rettype": "gb",
        "retmode": "text",
    }
    api_key = os.environ.get("NCBI_API_KEY")
    if api_key:
        params["api_key"] = api_key

    response = requests.get(
        EFETCH_URL,
        params=params,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    if not response.text.startswith("LOCUS"):
        raise ValueError(f"NCBI EFetch returned no GenBank record for {accession!r}")
    return response.text


def main(accession: str):
    """
    Downloads a transcript's GenBank flat file to datasources/refseq/{accession}.gb.

    Args:
        accession (str): Versioned RefSeq transcript accession, e.g. "NM_005228.5".
    """
    text = download_genbank(accession=accession)

    DATASOURCES_PATH.mkdir(parents=True, exist_ok=True)
    output_path = DATASOURCES_PATH / f"{accession}.gb"
    output_path.write_text(text)

    print(f"Wrote GenBank flat file for {accession} to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download the GenBank flat file for a RefSeq transcript",
    )
    parser.add_argument(
        "-a",
        "--accession",
        required=True,
        help="Versioned RefSeq transcript accession, e.g. NM_005228.5",
    )
    args = parser.parse_args()
    main(accession=args.accession)
