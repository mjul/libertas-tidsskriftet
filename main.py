import argparse
import logging
import os
from pathlib import Path

import requests
from google import genai
from typing import TypedDict, List


class IssueSource(TypedDict):
    issue: str
    uri: str


SOURCES: List[IssueSource] = [
    {"issue": "1-2", "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-1-og-2.pdf"},
    {"issue": "3", "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-3-Tocqueville.pdf"},
]


def issue_dir(issues_dir: Path, issue_source: IssueSource) -> Path:
    """Get the directory for an issue."""
    sub_dir = issue_source["issue"].split("-")[0]
    return issues_dir / sub_dir


def issue_pdf_path(issues_dir: Path, source: IssueSource) -> Path:
    """Get the path to the PDF file for an issue."""
    return issue_dir(issues_dir, source) / "tidsskrift.pdf"


def download_file(url: str, dest_path: Path):
    """Download a file from a URL to the destination path using requests."""
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status
    with open(dest_path, "wb") as f:
        f.write(response.content)


def download_pdfs(issues_dir: Path, sources: List[IssueSource], force):
    for source in sources:
        dir_path = issue_dir(issues_dir, source)
        pdf_path = issue_pdf_path(issues_dir, source)
        logging.debug(f"Processing {pdf_path}...")
        if pdf_path.exists() and not force:
            logging.debug(f"Issue {source['issue']} already downloaded. Skipping.")
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Downloading issue {source['issue']} from {source['uri']}...")
            download_file(source["uri"], issue_pdf_path(issues_dir, source))
            logging.info(f"Downloaded issue {source['issue']} from {source['uri']}.")


def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Extract articles and metadata from the Libertas archive.")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity"
    )
    parser.add_argument(
        "--google-api-key",
        type=str,
        default=os.environ.get("GOOGLE_API_KEY"),
        help=("Google API key to use. "
              "If not specified, the key is read from the GOOGLE_API_KEY environment variable.")
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force re-download of files even if they exist"
    )
    args = parser.parse_args()

    # Configure logging based on command-line arguments
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(process)d] %(levelname)s - %(message)s"
    )

    data_dir = Path("data")
    issues_dir = data_dir / "issues"
    issues_dir.mkdir(parents=True, exist_ok=True)

    download_pdfs(issues_dir, SOURCES, args.force)


if __name__ == "__main__":
    main()
