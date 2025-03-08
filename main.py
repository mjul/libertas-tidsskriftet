import argparse
import io
import json
import logging
import os
from pathlib import Path
from typing import TypedDict, List, Literal

import requests
from google import genai
from mistralai import Mistral


class IssueSource(TypedDict):
    issue: str
    uri: str


SOURCES: List[IssueSource] = [
    {"issue": "78",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-78-Muhammedtegninger-Marts-2022.pdf"},
    {"issue": "77",
     "uri": "http://www.libertas.dk/wp-content/uploads/2023/10/Libertas-77-Regulering-2-FARVE-November-2021.pdf"},
    {"issue": "76",
     "uri": "http://www.libertas.dk/wp-content/uploads/2023/10/Libertas-76-Thomas-Hobbes-2-Juli-2021.pdf"},
    {"issue": "75",
     "uri": "http://www.libertas.dk/wp-content/uploads/2023/10/Libertas-75-Frihandel-globalisering-og-protektionisme-FARVE-Marts-2021.pdf"},
    {"issue": "74",
     "uri": "http://www.libertas.dk/wp-content/uploads/2023/10/Libertas-74-Har-liberalismen-slaaet-fejl-2-Oktober-2020-1.pdf"},
    {"issue": "73",
     "uri": "http://www.libertas.dk/wp-content/uploads/2023/10/Libertas-73-Liberalisme-og-den-franske-revolution-III-juni-2020-FARVE.pdf"},
    {"issue": "72",
     "uri": "http://www.libertas.dk/wp-content/uploads/2023/10/Libertas-72-Liberalisme-og-den-franske-revolution-II-FARVE-2-Februar-2020.pdf"},
    {"issue": "71",
     "uri": "http://www.libertas.dk/wp-content/uploads/2023/10/Libertas-71-Liberalisme-og-den-franske-revolution-I-FARVE-2-Oktober-2019.pdf"},
    {"issue": "71-tillæg",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Lancien-regime-Tillæg-til-LIBERTAS.pdf"},
    {"issue": "70",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-70-Borgerlige-regeringer-juni-2019.pdf"},
    {"issue": "69",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-69-Indvandring-og-det-åbne-samfund-februar-2019.pdf"},
    {"issue": "68", "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-68-Penge-Oktober-2018.pdf"},
    {"issue": "67", "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-67-Public-choice-Juni-2018.pdf"},
    {"issue": "66", "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-nr-66-2018-De-store-kriser.pdf"},
    {"issue": "65",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-65-Den-østrigske-skole-Okt-2017.pdf"},
    {"issue": "64", "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-nr-64-Okt-2017-Anarkisme.pdf"},
    {"issue": "63",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-nr-63-Ytringsfrihed-og-tolerance-II.pdf"},
    {"issue": "62",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-nr.-62-Ytringsfrihed-og-tolerance-I.pdf"},
    {"issue": "61",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-nr.-61-Ayn-Rand-og-Adam-Smith-prisen-1.pdf"},
    {"issue": "60",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-nr.-60-Konservatisme-Trykning-3.pdf"},
    {"issue": "59",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-nr.-59-25-året-for-Berlinmurens-fald-Trykning-1.pdf"},
    {"issue": "58", "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Lbertas-nr.-58-Nozick-1.pdf"},
    {"issue": "57",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-57-Frihed-før-liberalismen-II-Revideret-1.pdf"},
    {"issue": "56",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-56-Frihedsrevolutionerne-1776-1789-1.pdf"},
    {"issue": "55",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-nr.-55-Liberalisme-Revideret-1.pdf"},
    {"issue": "54", "uri": "http://www.libertas.dk/arkiv/54.pdf"},
    {"issue": "53", "uri": "http://www.libertas.dk/arkiv/53.pdf"},
    {"issue": "52", "uri": "http://www.libertas.dk/arkiv/52.pdf"},
    {"issue": "51", "uri": "http://www.libertas.dk/arkiv/51.pdf"},
    {"issue": "50", "uri": "http://www.libertas.dk/arkiv/50.pdf"},
    {"issue": "49", "uri": "http://www.libertas.dk/arkiv/49.pdf"},
    {"issue": "48", "uri": "http://www.libertas.dk/arkiv/48.pdf"},
    {"issue": "47", "uri": "http://www.libertas.dk/arkiv/47.pdf"},
    {"issue": "45-46", "uri": "http://www.libertas.dk/arkiv/45.pdf"},
    {"issue": "44", "uri": "http://www.libertas.dk/arkiv/44.pdf"},
    {"issue": "43", "uri": "http://www.libertas.dk/arkiv/43.pdf"},
    {"issue": "42", "uri": "http://www.libertas.dk/arkiv/42.pdf"},
    {"issue": "41", "uri": "http://www.libertas.dk/arkiv/41.pdf"},
    {"issue": "40", "uri": "http://www.libertas.dk/arkiv/40.pdf"},
    {"issue": "39", "uri": "http://www.libertas.dk/arkiv/39.pdf"},
    {"issue": "38", "uri": "http://www.libertas.dk/arkiv/38.pdf"},
    {"issue": "37", "uri": "http://www.libertas.dk/arkiv/37.pdf"},
    {"issue": "36", "uri": "http://www.libertas.dk/arkiv/36.pdf"},
    {"issue": "35", "uri": "http://www.libertas.dk/arkiv/35.pdf"},
    {"issue": "34", "uri": "http://www.libertas.dk/arkiv/34.pdf"},
    {"issue": "33", "uri": "http://www.libertas.dk/arkiv/33.pdf"},
    {"issue": "32", "uri": "http://www.libertas.dk/arkiv/32.pdf"},
    {"issue": "31", "uri": "http://www.libertas.dk/arkiv/31.pdf"},
    {"issue": "29-30", "uri": "http://www.libertas.dk/arkiv/29.pdf"},
    {"issue": "27-28", "uri": "http://www.libertas.dk/arkiv/27.pdf"},
    {"issue": "26", "uri": "http://www.libertas.dk/arkiv/26.pdf"},
    {"issue": "25", "uri": "http://www.libertas.dk/arkiv/25.pdf"},
    {"issue": "24", "uri": "http://www.libertas.dk/arkiv/24.pdf"},
    {"issue": "23", "uri": "http://www.libertas.dk/arkiv/23.pdf"},
    {"issue": "22b",
     "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-nr.-22b-Peter-Kurrild-Klitgaard-En-tilfældig-individualists-hændelige-erindringer.pdf"},
    {"issue": "22", "uri": "http://www.libertas.dk/arkiv/22.pdf"},
    {"issue": "21", "uri": "http://www.libertas.dk/arkiv/21.pdf"},
    {"issue": "20", "uri": "http://www.libertas.dk/arkiv/20.pdf"},
    {"issue": "19", "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-19.pdf"},
    {"issue": "18", "uri": "http://www.libertas.dk/arkiv/18.pdf"},
    {"issue": "17", "uri": "http://www.libertas.dk/arkiv/17.pdf"},
    {"issue": "16", "uri": "http://www.libertas.dk/arkiv/16.pdf"},
    {"issue": "15", "uri": "http://www.libertas.dk/arkiv/15.pdf"},
    {"issue": "14", "uri": "http://www.libertas.dk/arkiv/14.pdf"},
    {"issue": "13", "uri": "http://www.libertas.dk/arkiv/13.pdf"},
    {"issue": "12", "uri": "http://www.libertas.dk/arkiv/12.pdf"},
    {"issue": "11", "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-11-1990.pdf"},
    {"issue": "10", "uri": "http://www.libertas.dk/arkiv/10.pdf"},
    {"issue": "9", "uri": "http://www.libertas.dk/arkiv/9.pdf"},
    {"issue": "8", "uri": "http://www.libertas.dk/arkiv/8.pdf"},
    {"issue": "7", "uri": "http://www.libertas.dk/arkiv/7.pdf"},
    {"issue": "6", "uri": "http://www.libertas.dk/arkiv/6.pdf"},
    {"issue": "5", "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-5.pdf"},
    {"issue": "4", "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-4-Friedman-m.m..pdf"},
    {"issue": "3", "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-3-Tocqueville.pdf"},
    {"issue": "1-2", "uri": "http://www.libertas.dk/wp-content/uploads/2016/12/Libertas-1-og-2.pdf"},
    # Særnumre
    {"issue": "64-65-konference",
     "uri": "http://www.libertas.dk/wp-content/uploads/2018/01/Konference-om-anarkisme-og-den-østrigske-skole.pdf"},
]


def issue_dir(issues_dir: Path, issue_source: IssueSource) -> Path:
    """Get the directory for an issue."""
    sub_dir = issue_source["issue"]
    return issues_dir / sub_dir


def issue_pdf_path(issues_dir: Path, source: IssueSource) -> Path:
    """Get the path to the PDF file for an issue."""
    return issue_dir(issues_dir, source) / "tidsskrift.pdf"


def issue_summary_path(issues_dir: Path, source: IssueSource) -> Path:
    """Get the path to the summary of the issue (contents, citations, etc.)"""
    return issue_dir(issues_dir, source) / "resume.md"

ModelName = Literal["gemini", "mistral"]

def issue_summary_model_path(issues_dir: Path, source: IssueSource, model: ModelName) -> Path:
    """Get the path to the summary of the issue (contents, citations, etc.) produced by a specific model."""
    return issue_dir(issues_dir, source) / f"resume-{model}.md"


def issue_ocr_model_path(issues_dir: Path, source: IssueSource, model: ModelName) -> Path:
    """Get the path to the summary of the issue (contents, citations, etc.) produced by a specific model."""
    return issue_dir(issues_dir, source) / f"ocr-{model}.md"


def download_file(url: str, dest_path: Path):
    """Download a file from a URL to the destination path using requests."""
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status
    with open(dest_path, "wb") as f:
        f.write(response.content)


def download_pdfs(issues_dir: Path, sources: List[IssueSource], force: bool):
    for source in sources:
        dir_path = issue_dir(issues_dir, source)
        pdf_path = issue_pdf_path(issues_dir, source)
        if pdf_path.exists() and not force:
            logging.info(f"Issue {source['issue']} already downloaded. Skipping.")
        else:
            dir_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Downloading issue {source['issue']} from {source['uri']}...")
            download_file(source["uri"], issue_pdf_path(issues_dir, source))
            logging.info(f"Downloaded issue {source['issue']} from {source['uri']}.")


class IssueData(TypedDict):
    indhold: str
    citerede: str


def extract_issue_data_gemini(pdf_path: Path, google_api_key: str) -> IssueData:
    client = genai.Client(api_key=google_api_key)

    logging.info(f"Uploading PDF for analysis {pdf_path}...")
    uploaded_pdf = client.files.upload(file=io.BytesIO(pdf_path.read_bytes()),
                                       config=dict(mime_type="application/pdf"))

    logging.info(f"Extracting contents...")
    indhold_response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[
            uploaded_pdf,
            """
            Giv mig indholdsfortegnelse og skribenter og kort resume af emnet for artiklerne i vedhæftede blad.

            Svar med Markdown i følgende format:

            * **Titel på artikel** - *forfatter*. Kort resume af emnet.


            Hvis der er boganmeldelser, så skriv en sektion 

            ### Boganmeldelser

            Skriv for hver anmeldelse bogens titel og bogens forfatter og emne for anmeldelsen.

            Svar med Markdown i følgende format:

            * **Bogtitel** - *bogens forfatter*. Bogens emne.
            """
        ]
    )
    assert indhold_response.text is not None

    logging.info(f"Article cited authors...")
    citerede_response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[
            uploaded_pdf,
            """
            Hvilke forfattere og værker er citeret eller omtalt i de forskellige artikler?

            Svar med Markdown i følgende format:
            ### Titel på artikel
            * Navn - liste over værker
            """
        ]
    )
    assert citerede_response.text is not None

    return {"indhold": indhold_response.text, "citerede": citerede_response.text}


def extract_issue_text_mistral(pdf_path: Path, mistral_api_key: str) -> str:
    client = Mistral(api_key=mistral_api_key)

    logging.info(f"Uploading PDF for analysis {pdf_path}...")
    uploaded_pdf = client.files.upload(
        file={
            "file_name": pdf_path.parent.name + "/" + pdf_path.name,
            #"content": pdf_path.read_bytes(),
            "content": open(pdf_path, "rb").read(),
        },
        purpose="ocr"
    )
    logging.info(f"Signing URL...")
    signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id, expiry=1)

    logging.info(f"Extracting contents with Mistral OCR...")
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url.url,
        },
        include_image_base64 = False,
    )
    logging.debug(f"OCR response. Found {len(ocr_response.pages)} pages.")

    response_dict = json.loads(ocr_response.model_dump_json())
    markdown_contents = [
        page.get("markdown", "") for page in response_dict.get("pages", [])
    ]
    markdown_text = "\n\n".join(markdown_contents)

    return markdown_text


def extract_issue_data(issues_dir: Path, source: IssueSource, google_api_key: str, mistral_api_key: str, force: bool):
    pdf_path = issue_pdf_path(issues_dir, source)
    if not pdf_path.exists():
        logging.warn(f"Issue {source['issue']} not downloaded. Skipping.")
    else:
        model: ModelName= "gemini"
        resume_output_path = issue_summary_model_path(issues_dir, source, model)
        if resume_output_path.exists() and not force:
            logging.debug(f"Resume exists for issue {source['issue']} for model {model}. Skipping.")
        else:
            gemini_data = extract_issue_data_gemini(pdf_path, google_api_key)
            logging.info(f"Saving resume from {model} to {resume_output_path}...")
            with open(resume_output_path, "w", encoding="utf-8") as f:
                f.write(f"# {source['issue']}\n\n")
                f.write(f"PDF udgave: <{source['uri']}>\n\n")
                f.write(f"## Indhold\n\n{gemini_data["indhold"]}\n\n")
                f.write(f"## Citerede forfattere\n\n{gemini_data["citerede"]}\n\n")
        model: ModelName = "mistral"
        ocr_output_path = issue_ocr_model_path(issues_dir, source, model)
        if ocr_output_path.exists() and not force:
            logging.debug(f"OCR results exists for issue {source['issue']} for model {model}. Skipping.")
        else:
            ocr_markdown = extract_issue_text_mistral(pdf_path, mistral_api_key)
            logging.info(f"Saving OCR results from {model} to {ocr_output_path}...")
            with open(ocr_output_path, "w", encoding="utf-8") as f:
                f.write(f"# {source['issue']}\n\n")
                f.write(f"PDF udgave: <{source['uri']}>\n\n")
                f.write(f"{ocr_markdown}\n\n")


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
        help=("Google Gemini API key to use. "
              "If not specified, the key is read from the GOOGLE_API_KEY environment variable.")
    )
    parser.add_argument(
        "--mistral-api-key",
        type=str,
        default=os.environ.get("MISTRAL_API_KEY"),
        help=("Mistral API key to use. "
              "If not specified, the key is read from the MISTRAL_API_KEY environment variable.")
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force re-download of files even if they exist"
    )
    parser.add_argument(
        "--take",
        type=int,
        default=None,
        help="Only process the first N issues from the source list."
    )
    args = parser.parse_args()

    if not args.google_api_key:
        parser.error("Google Gemini API key must be specified.")

    if not args.mistral_api_key:
        parser.error("Mistral API key must be specified.")

    # Configure logging based on command-line arguments
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(process)d] %(levelname)s - %(message)s"
    )

    data_dir = Path("data")
    issues_dir = data_dir / "issues"
    issues_dir.mkdir(parents=True, exist_ok=True)

    sorted_sources = sorted(SOURCES, key=lambda source: source["issue"])
    sources_to_process = sorted_sources[:args.take] if args.take else sorted_sources
    download_pdfs(issues_dir, sources_to_process, args.force)

    for source in sources_to_process:
        logging.info(f"Processing issue {source['issue']}...")
        extract_issue_data(issues_dir, source, args.google_api_key, args.mistral_api_key, args.force)

    logging.info(f"Done.")


if __name__ == "__main__":
    main()
