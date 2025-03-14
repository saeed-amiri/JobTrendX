"""
tools for the main modules
"""

import re
import sys
import typing
from pathlib import Path
import email
from email import policy
from email.message import EmailMessage
from langdetect import detect

import pandas as pd

from . import colors_text as ct


__all__ = [
    "check_directory",
    "check_dir_not_empty",
    "returns_all_files_in_dir",
    "returns_eml_files",
    "returns_eml_path",
    "returns_email_contant",
    "extract_email_detail",
    "eml_to_dataframe",
    "detect_language",
]


# Functions in used inside email_processor.py:

def check_directory(directory: str) -> None | bool:
    "Check if the directory exists"
    if not Path.exists(Path(directory)):
        print(f"{ct.FAIL}Directory `{directory}` does not "
              f"exists, exit!{ct.ENDC}\n")
        sys.exit(1)
    return True


def check_dir_not_empty(directory: str) -> None | bool:
    "Check if the directory is not empty"
    if not any(Path(directory).iterdir()):
        print(f"{ct.FAIL}Directory `{directory}` is empty, exit!{ct.ENDC}\n")
        sys.exit(1)
    return True


def returns_all_files_in_dir(directory: str) -> list[str]:
    """Return all files in the directory"""
    return [
        file.name
        for file in Path(directory).iterdir()
        if file.is_file()
        ]


def returns_eml_files(eml_name_list: list[str],
                      extension: str = 'eml'
                      ) -> list[str]:
    """Filter and return the file names that match the
    specified extension."""
    # Ensure the extension has a leading dot and convert it to lower case.
    ext = f".{extension.lstrip('.')}".lower()

    # Filter files using pathlib to check file extension.
    return [
        file
        for file in eml_name_list
        if Path(file).suffix.lower() == ext
        ]


def returns_eml_path(parent_path: str,
                     eml_list: list[str]
                     ) -> list[Path]:
    """make a real path of the files"""
    return [Path(parent_path) / file for file in eml_list]


def returns_email_contant(eml_paths: list[Path]
                          ) -> dict[Path, "email.message.EmailMessage"]:
    """Read the emails and return the contents in a DataFrame"""
    eml_dict: dict[Path, "email.message.EmailMessage"] = {}
    for file_path in eml_paths:
        with open(file_path, "r", encoding="utf-8") as eml:
            msg = email.message_from_file(eml, policy=policy.default)
        eml_dict[file_path] = msg
        del msg
    return eml_dict


# Function used inside analysis.py:

def extract_email_detail(eml_dict: dict[Path, EmailMessage]
                         ) -> dict[Path, dict[str, typing.Any]]:
    """extract and return the metadata"""
    extracted_data: dict[Path, dict[str, typing.Any]] = {}

    for file_path, email_obj in eml_dict.items():
        details = {
            "subject": email_obj["subject"],
            "from": email_obj["from"],
            "to": email_obj["to"],
            "date": email_obj["date"],
            "message_id": email_obj["message-id"],
            "payload": _extract_email_payload(email_obj),
            "attachments": _extract_attachments(email_obj)
        }
        extracted_data[file_path] = details
    return extracted_data


def _extract_email_payload(email_obj: EmailMessage) -> str:
    """Get the plain text payload of the email."""
    if email_obj.is_multipart():
        return _extract_payload_from_multipart(email_obj)
    return _extract_payload_from_singlepart(email_obj)


def _extract_payload_from_multipart(email_obj: EmailMessage) -> str:
    """Extract payload from a multipart email."""
    for part in email_obj.walk():
        payload = part.get_payload(decode=True)
        if payload is not None:
            return _decode_payload(part, payload)
    return ""


def _extract_payload_from_singlepart(email_obj: EmailMessage) -> str:
    """Extract payload from a singlepart email."""
    payload = email_obj.get_payload(decode=True)
    if payload is not None:
        return _decode_payload(email_obj, payload)
    return ""


def _decode_payload(part: email.message.Message,
                    payload: typing.Any
                    ) -> str:
    """Decode the payload to a string."""
    if isinstance(payload, bytes):
        return payload.decode(
            part.get_content_charset() or "utf-8", errors="ignore")
    return str(payload)


def _extract_attachments(email_obj: EmailMessage) -> list[str | None]:
    """Extracts the attachment file names from an email"""
    attchments: list[str | None] = []

    for part in email_obj.walk():
        if part.get_content_disposition() == "attachment":
            attchments.append(part.get_filename())

    return attchments


def eml_to_dataframe(eml_data: dict[Path, dict[str, typing.Any]]
                     ) -> pd.DataFrame:
    """Flatten the dict of dict and convert to df"""
    flat_data: list[dict[str, typing.Any]] = [
        {"file_path": str(path), **detail}
        for path, detail in eml_data.items()
    ]
    df: pd.DataFrame = pd.DataFrame(flat_data)
    try:
        df["payload"] = df["payload"].apply(_clean_eml_payload)
    except KeyError:
        pass

    return df


def _clean_eml_payload(text: str) -> str:
    """
    Remove the extra spaces, new lines, and the encoding
    artifcats
    """
    if not text:
        return ""
    text = text.strip()
    text = text.replace("\xa0", " ")  # Replace non-breaking spaces
    text = re.sub(r"http\S+", "[URL]", text)  # Replace links
    return text


def detect_language(bodies: pd.Series) -> pd.Series:
    """Get emails languages"""
    return bodies.apply(_detect_single_language)


def _detect_single_language(text: str) -> str:
    """
    Detect the language of the given text,
    If it failed to detect it will return unknown,
    For now only En and De is considered
    """
    try:
        lang: str = detect(text)
        return _check_language(lang)
    except Exception as err:
        print(f'Warning: Language detection faild! error: `{err}`\n')
        return "unknown"


def _check_language(lang: str) -> str:
    """
    Check if the detected language is one of English (en)
    or German (de), otherwise return "unknown"
    """
    allowed_languages: set[str] = {"en", "de"}
    return lang if lang in allowed_languages else "unknown"
