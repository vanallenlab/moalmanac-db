"""Download a versioned snapshot of the NCI Thesaurus flat file.

Fetches the flat file archive for the given NCI Thesaurus version from the
public NCI EVS FTP archive and writes the extracted file to
datasources/{version}_Thesaurus.txt.

Usage: python datasources/scripts/download_nci_thesaurus.py --version 26.08e
"""

import argparse
import io
import pathlib
import zipfile

import requests

NCIT_ARCHIVE_URL_TEMPLATE = (
    "https://evs.nci.nih.gov/ftp1/NCI_Thesaurus/archive/"
    "{version}_Release/Thesaurus_{version}.FLAT.zip"
)

DATASOURCES_PATH = pathlib.Path("datasources")


def download_nci_thesaurus(version: str) -> bytes:
    """
    Downloads the NCI Thesaurus flat file archive for a given version.

    Args:
        version (str): NCI Thesaurus version to download, e.g. "26.08e".

    Raises:
        requests.HTTPError: If the NCI EVS FTP server responds with an error status.

    Returns:
        bytes: Contents of the archive's Thesaurus.txt flat file.
    """
    response = requests.get(NCIT_ARCHIVE_URL_TEMPLATE.format(version=version))
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        return archive.read("Thesaurus.txt")


def main(version: str):
    """
    Downloads an NCI Thesaurus version and writes it to
    datasources/{version}_Thesaurus.txt.

    Args:
        version (str): NCI Thesaurus version to download, e.g. "26.08e".
    """
    data = download_nci_thesaurus(version=version)

    output_path = DATASOURCES_PATH / f"Thesaurus_{version}.txt"
    output_path.write_bytes(data)

    print(f"Wrote NCI Thesaurus {version} to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download a versioned NCI Thesaurus flat file",
    )
    parser.add_argument(
        "-v",
        "--version",
        required=True,
        help="NCI Thesaurus version to download, e.g. 26.08e",
    )
    args = parser.parse_args()
    main(version=args.version)
