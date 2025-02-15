"""
tools for the main modules
"""

import sys
import typing
from pathlib import Path
import email
from email import policy
from email.message import EmailMessage


from . import colors_text as ct


__all__ = [
    "check_directory",
    "check_dir_not_empty",
    "returns_all_files_in_dir",
    "returns_eml_files",
    "returns_eml_path",
    "returns_email_contant",
    "extract_email_detail",
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
            "body": _extract_email_body(email_obj),
            "attachments": _extract_attachments(email_obj)
        }
        extracted_data[file_path] = details
    return extracted_data


def _extract_email_body(email_obj: EmailMessage) -> str:
    """Get the plain text body of the email."""
    if email_obj.is_multipart():
        return _extract_body_from_multipart(email_obj)
    return _extract_body_from_singlepart(email_obj)


def _extract_body_from_multipart(email_obj: EmailMessage) -> str:
    """Extract body from a multipart email."""
    for part in email_obj.walk():
        payload = part.get_payload(decode=True)
        if payload is not None:
            return _decode_payload(part, payload)
    return ""


def _extract_body_from_singlepart(email_obj: EmailMessage) -> str:
    """Extract body from a singlepart email."""
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
