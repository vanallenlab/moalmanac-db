"""Download the NCBI ESummary record for a RefSeq protein product.

Fetches the document summary for the given versioned RefSeq protein accession from
NCBI ESummary and writes it to datasources/refseq/{accession}.esummary.json.

Usage: python datasources/scripts/download_refseq_protein_esummary.py --accession NP_005219.2
"""

import argparse
import json
import os
import pathlib
import re

import requests

ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

ACCESSION_PATTERN = re.compile(r"^[NXY]P_\d+\.\d+$")
DATASOURCES_PATH = pathlib.Path("datasources") / "refseq"
TIMEOUT = 90


def download_esummary(accession: str) -> dict:
    """
    Downloads the NCBI ESummary record for a RefSeq protein product.

    Args:
        accession (str): Versioned RefSeq protein accession, e.g. "NP_005219.2".

    Raises:
        requests.HTTPError: If NCBI ESummary responds with an error status.
        ValueError: If the accession is not a versioned RefSeq protein accession,
            or if NCBI ESummary returns no summary for it.

    Returns:
        dict: The ESummary response, as parsed JSON.
    """
    if not ACCESSION_PATTERN.match(accession):
        raise ValueError(
            "accession must be a versioned RefSeq protein accession such as "
            f"'NP_005219.2', got {accession!r}",
        )

    params = {
        "db": "protein",
        "id": accession,
        "retmode": "json",
    }
    api_key = os.environ.get("NCBI_API_KEY")
    if api_key:
        params["api_key"] = api_key

    response = requests.get(
        ESUMMARY_URL,
        params=params,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()

    result = data.get("result", {})
    uids = result.get("uids", [])
    if "error" in data or not uids or "error" in result[uids[0]]:
        raise ValueError(f"NCBI ESummary returned no summary for {accession!r}")
    return data


def main(accession: str):
    """
    Downloads a protein's ESummary to datasources/refseq/{accession}.esummary.json.

    Args:
        accession (str): Versioned RefSeq protein accession, e.g. "NP_005219.2".
    """
    data = download_esummary(accession=accession)

    DATASOURCES_PATH.mkdir(parents=True, exist_ok=True)
    output_path = DATASOURCES_PATH / f"{accession}.esummary.json"
    output_path.write_text(
        json.dumps(
            data,
            separators=(",", ":"),
        )
        + "\n",
    )

    print(f"Wrote ESummary for {accession} to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download the NCBI ESummary record for a RefSeq protein product",
    )
    parser.add_argument(
        "-a",
        "--accession",
        required=True,
        help="Versioned RefSeq protein accession, e.g. NP_005219.2",
    )
    args = parser.parse_args()
    main(accession=args.accession)
