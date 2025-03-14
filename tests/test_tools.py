"""
Testing the tools module
"""
# pylint: disable=redefined-outer-name


from pathlib import Path
from unittest.mock import patch

from email.message import EmailMessage
import pytest

import pandas as pd

from jobtrendx.tools import check_directory, check_dir_not_empty, \
    returns_all_files_in_dir, returns_eml_files, returns_eml_path, \
    _extract_attachments, _clean_eml_payload, eml_to_dataframe, \
    detect_language, _detect_single_language, _check_language


def test_check_directory_exists() -> None:
    "Test if the check_directory returns True correctly"
    with patch.object(Path, 'exists', return_value=True):
        assert check_directory('test_dir') is True


def test_check_directory_not_exists() -> None:
    "Test if the check_directory exit correctly"
    with patch.object(Path, 'exists', return_value=False):
        with pytest.raises(SystemExit) as exit_info:
            check_directory('test_dir')
        assert exit_info.type == SystemExit
        assert exit_info.value.code == 1


def test_check_dir_not_empty_contains() -> None:
    """Test if the check_dir_not_empty knows dir is not empty"""
    with patch.object(Path, 'iterdir', return_value=[1, 2, 3]):
        assert check_dir_not_empty('test_dir')


def test_check_dir_not_empty_not_contains() -> None:
    """Test if the check_dir_not_empty knows dir is empty"""
    with patch.object(Path, 'iterdir', return_value=[]):
        with pytest.raises(SystemExit) as exit_info:
            check_dir_not_empty('test_dir')
        assert exit_info.type == SystemExit
        assert exit_info.value.code == 1


def test_returns_all_files_in_dir() -> None:
    """Test if it returns the files."""
    fake_file = Path('email1.eml')
    with patch.object(Path, 'iterdir', return_value=[fake_file]):
        # Patch is_file on the Path class so that f.is_file()
        # returns True for fake_file.
        with patch.object(Path, 'is_file', return_value=True):
            # Adjust expected value to a list of strings because the
            # function returns file names.
            assert returns_all_files_in_dir('test_dir') == ['email1.eml']


def test_returns_eml_files() -> None:
    """
    Test that returns_eml_files correctly filters file names by extension.
    """
    fake_files = ['email1.eml', 'not_email.txt']
    fake_extension = 'eml'
    expected = ['email1.eml']

    assert returns_eml_files(fake_files, fake_extension) == expected


def test_returns_eml_path() -> None:
    """Test returns_eml_path can returns correct file path"""
    fake_files = ['email1.eml', 'email2.eml']
    parent_path = 'emails'
    expected = [Path('emails/email1.eml'), Path('emails/email2.eml')]
    result = returns_eml_path(parent_path=parent_path, eml_list=fake_files)

    assert result == expected, f"Expected {expected}, but got {result}"


def test_returns_eml_path_output_type():
    """Ensure that the function returns a list of Path objects."""
    parent = "emails"
    eml_files = ["file1.eml", "file2.eml"]
    result = returns_eml_path(parent, eml_files)

    assert all(isinstance(path, Path) for path in result), \
        "Not all elements are Path objects"


def test_extract_attachments_no_attachments() -> None:
    """Test _extract_attachments with no attachments in the email."""
    email_obj = EmailMessage()
    email_obj.set_content("This is a test email with no attachments.")

    assert not _extract_attachments(email_obj)


def test_extract_attachments_with_attachments() -> None:
    """Test _extract_attachments with attachments in the email."""
    email_obj = EmailMessage()

    # Directly define the email as multipart/mixed
    email_obj.set_type("multipart/mixed")

    # Create a mock attachment part
    attachment_part = EmailMessage()
    attachment_part.add_attachment(b"dummy content",
                                   maintype="application",
                                   subtype="octet-stream",
                                   filename="test.txt")

    # Attach, email_obj is multipart
    email_obj.attach(attachment_part)

    assert _extract_attachments(email_obj) == ["test.txt"]


def test_extract_attachments_mixed_content() -> None:
    """Test _extract_attachments with mixed content in the email."""

    email_obj = EmailMessage()
    email_obj["Subject"] = "Test Email with Mixed Content"
    email_obj["From"] = "test@example.com"
    email_obj["To"] = "receiver@example.com"

    email_obj.set_type("multipart/mixed")

    # Create a mock text part
    text_part = EmailMessage()
    text_part.set_content("This is a text part.")

    # Create a mock attachment part
    attachment_part = EmailMessage()
    attachment_part.add_attachment(b"dummy content",
                                   maintype="application",
                                   subtype="octet-stream",
                                   filename="test.txt")

    email_obj.attach(text_part)
    email_obj.attach(attachment_part)

    assert _extract_attachments(email_obj) == ["test.txt"]


def test_clean_eml_payload() -> None:
    """Test if the input text cleand correctly"""
    text: str = \
        " Hello\xa0world! Visit https://example.com for more info.  "
    assert _clean_eml_payload(text) == \
        "Hello world! Visit [URL] for more info."


def test_eml_to_dataframe_valid_data() -> None:
    """Test eml_to_dataframe with valid email dictionary."""
    eml_data = {
        Path("emails/email1.eml"): {
            "subject": "Job Offer",
            "from": "hr@company.com",
            "to": "you@example.com",
            "date": "Tue, 13 Feb 2024",
            "payload": "We are pleased to offer you a position.",
            "attachments": ["contract.pdf"]
        },
        Path("emails/email2.eml"): {
            "subject": "Project Update",
            "from": "manager@example.com",
            "to": "team@example.com",
            "date": "Wed, 14 Feb 2024",
            "payload": "Here is the latest project update.",
            "attachments": []
        }
    }

    df: pd.DataFrame = eml_to_dataframe(eml_data)

    # Check DataFrame shape
    assert df.shape == (2, 7)

    # Ensure correct columns exist
    expected_columns: set[str] = {
        "file_path", "subject", "from", "to", "date", "payload", "attachments"}
    assert set(df.columns) == expected_columns

    # Ensure payload text was processed
    assert isinstance(df.at[0, "payload"], str)
    assert "offer you a position" in df.at[0, "payload"]

    # Ensure attachments are stored correctly
    assert isinstance(df.at[0, "attachments"], list)
    assert df.at[0, "attachments"] == ["contract.pdf"]


def test_eml_to_dataframe_empty_dict() -> None:
    """Test eml_to_dataframe with an empty dictionary (edge case)."""
    df = eml_to_dataframe({})

    # Should return an empty DataFrame with correct columns
    assert df.empty


def test_detect_language() -> None:
    """test it with a pd.Series"""
    bodies = pd.Series(
        ["Hallo, wie geht's?", "Hello, how are you?", "Bonjour!", ""])
    expected = pd.Series(["de", "en", "unknown", "unknown"])

    assert detect_language(bodies).equals(expected)


def test_detect_single_language() -> None:
    """test with valid and invalid text"""
    assert _detect_single_language("Das ist ein Test.") == "de"
    assert _detect_single_language("This is a test.") == "en"
    assert _detect_single_language("Bonjour tout le monde!") == "unknown"
    assert _detect_single_language("") == "unknown"


def test_check_language() -> None:
    """check to the language is valid"""
    assert _check_language("en") == "en"
    assert _check_language("de") == "de"
    assert _check_language("fr") == "unknown"
    assert _check_language("es") == "unknown"
