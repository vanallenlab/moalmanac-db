"""Download the GenPept flat file for a RefSeq protein product.

Fetches the GenPept flat file for the given versioned RefSeq protein accession from
NCBI EFetch and writes it to datasources/refseq/{accession}.gp.

Usage: python datasources/scripts/download_refseq_protein_genpept.py --accession NP_005219.2
"""

import argparse
import os
import pathlib
import re

import requests

EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

ACCESSION_PATTERN = re.compile(r"^[NXY]P_\d+\.\d+$")
DATASOURCES_PATH = pathlib.Path("datasources") / "refseq"
TIMEOUT = 90


def download_genpept(accession: str) -> str:
    """
    Downloads the GenPept flat file for a RefSeq protein product.

    Args:
        accession (str): Versioned RefSeq protein accession, e.g. "NP_005219.2".

    Raises:
        requests.HTTPError: If NCBI EFetch responds with an error status.
        ValueError: If the accession is not a versioned RefSeq protein accession,
            or if NCBI EFetch returns no GenPept record for it.

    Returns:
        str: The GenPept flat file, as text.
    """
    if not ACCESSION_PATTERN.match(accession):
        raise ValueError(
            "accession must be a versioned RefSeq protein accession such as "
            f"'NP_005219.2', got {accession!r}",
        )

    params = {
        "db": "protein",
        "id": accession,
        "rettype": "gp",
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
        raise ValueError(f"NCBI EFetch returned no GenPept record for {accession!r}")
    return response.text


def main(accession: str):
    """
    Downloads a protein's GenPept flat file to datasources/refseq/{accession}.gp.

    Args:
        accession (str): Versioned RefSeq protein accession, e.g. "NP_005219.2".
    """
    text = download_genpept(accession=accession)

    DATASOURCES_PATH.mkdir(parents=True, exist_ok=True)
    output_path = DATASOURCES_PATH / f"{accession}.gp"
    output_path.write_text(text)

    print(f"Wrote GenPept flat file for {accession} to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download the GenPept flat file for a RefSeq protein product",
    )
    parser.add_argument(
        "-a",
        "--accession",
        required=True,
        help="Versioned RefSeq protein accession, e.g. NP_005219.2",
    )
    args = parser.parse_args()
    main(accession=args.accession)
