"""
tools for analysis
"""

import re
import typing
from pathlib import Path
import email
from email.message import EmailMessage
from langdetect import detect

import pandas as pd


__all__ = [
    "extract_email_detail",
    "eml_to_dataframe",
    "detect_language",
]

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
