import argparse
import json
import pathlib
import sys

import requests

ONCOTREE_FLAT_URL = "https://oncotree.mskcc.org/api/tumorTypes"
ONCOTREE_TREE_URL = "https://oncotree.mskcc.org/api/tumorTypes/tree"

DATASOURCES_PATH = pathlib.Path("datasources")


def download_oncotree(mode: str, version: str) -> dict:
    """
    Downloads the OncoTree tumor type tree for a given version.

    Args:
        mode (str): OncoTree endpoint to request, "flat" or "tree"
        version (str): OncoTree version to download, e.g. "oncotree_2025_10_03".

    Raises:
        requests.HTTPError: If the OncoTree API responds with an error status.

    Returns:
        dict: OncoTree tumor type data, as parsed JSON.
    """
    if mode == "flat":
        request = ONCOTREE_FLAT_URL
    elif mode == "tree":
        request = ONCOTREE_TREE_URL
    else:
        sys.exit(f"{mode} is not either 'flat' or 'tree'")

    response = requests.get(
        request,
        params={"version": version},
    )
    response.raise_for_status()
    return response.json()


def main(mode:str, version: str):
    """
    Downloads an OncoTree version and writes it to datasources/{version}_{mode}.json.

    Args:
        version (str): OncoTree version to download, e.g. "oncotree_2025_10_03".
    """
    data = download_oncotree(
        mode=mode,
        version=version,
    )

    output_path = DATASOURCES_PATH / f"{version}_{mode}.json"
    output_path.write_text(
        json.dumps(
            data,
            indent=2,
        ),
    )

    print(f"Wrote OncoTree {version} {mode} to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download a versioned OncoTree data",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=[
            "flat",
            "tree"
        ],
        help="OncoTree endpoint to use. Choices: flat or tree",
        required=True,
    )
    parser.add_argument(
        "-v",
        "--version",
        required=True,
        help="OncoTree version to download, e.g. oncotree_2025_10_03",
    )
    args = parser.parse_args()
    main(
        mode=args.mode,
        version=args.version
    )
