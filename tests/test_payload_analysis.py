"""
Testing the payload_analysis module
"""
# pylint: disable=redefined-outer-name

import unittest
from unittest.mock import patch, mock_open

import yaml
import pandas as pd
from omegaconf import DictConfig

from jobtrendx.payload_analysis import _get_sections, _split_by_lang, \
    _split_double_newline, _filter_item, _extract_title, _fetch_from_yaml, \
    _extract_matching_item


def test_get_sections_de() -> None:
    """test if detect de sections correctly"""
    sections_de = {
        "job_title": "Beliebter Job",
        "company": "Wer wir sind.",
        "requirements": "Das bringst du mit",
        "benefits": "Das bieten wir dir"
        }

    payload_text = """Beliebter Job
        Data Scientist (m/w/d) Schwerpunkt KI

        PreZero Service Deutschland GmbH & Co. KG
        Wesseling bei Köln 
        10,001+ Mitarbeiter
        Feste Anstellung
        Vollzeit, Homeoffice möglich
        66.000 - 90.000 €/Jahr (geschätzt für Vollzeit)

        Wer wir sind.
        PreZero ist ein innovatives Unternehmen...

        Das bringst du mit
        Du bringst ein abgeschlossenes Studium im Bereich Informatik...

        Das bieten wir dir
        Als Teil der Schwarz Gruppe...
        """
    sections: dict[str, str] = _get_sections(payload_text, sections_de)
    assert sections["job_title"] == (
        'Data Scientist (m/w/d) Schwerpunkt KI\n\n        PreZero Service '
        'Deutschland GmbH & Co. KG\n        Wesseling bei Köln \n        '
        '10,001+ Mitarbeiter\n        Feste Anstellung\n        Vollzeit, '
        'Homeoffice möglich\n        66.000 - 90.000 €/Jahr (geschätzt für '
        'Vollzeit)\n')
    assert sections["company"] == \
        'PreZero ist ein innovatives Unternehmen...\n'
    assert sections["requirements"] == \
        'Du bringst ein abgeschlossenes Studium im Bereich Informatik...\n'
    assert sections["benefits"] == 'Als Teil der Schwarz Gruppe...\n'


def test_get_sections_en() -> None:
    """
    Test if the function correctly detects and extracts sections in English.
    """
    sections_en = {
        "job_title": "Top Match",
        "company": "Who we are",
        "requirements": "Your knowledge/experience",
        "benefits": "We offer"
    }

    payload_text = """Top Match
        Data Scientist (m/f/d) AI Specialist

        Lloyds Bank - Bank of Scotland
        Berlin
        251-500 employees
        Permanent position
        Full-time, Part-time, Remote possible
        Estimated Salary: $80,000 - $110,000 per year

        Who we are
        Lloyds Bank GmbH and its brands Bank of Scotland and Lloyds Bank
        have won over 1 million satisfied customers in recent years...

        Your knowledge/experience
        Educated to a degree level in Computer Science, Data Science...

        We offer
        An inclusive and diverse work environment...
    """

    sections: dict[str, str] = _get_sections(payload_text, sections_en)

    assert sections['job_title'] == (
        'Data Scientist (m/f/d) AI Specialist\n\n        Lloyds Bank - '
        'Bank of Scotland\n        Berlin\n        251-500 '
        'employees\n        Permanent position\n        Full-time, '
        'Part-time, Remote possible\n        Estimated Salary: '
        '$80,000 - $110,000 per year\n')
    assert sections['company'] == (
        'Lloyds Bank GmbH and its brands Bank of Scotland and Lloyds '
        'Bank\n        have won over 1 million satisfied customers in '
        'recent years...\n')
    assert sections['requirements'] == \
        'Educated to a degree level in Computer Science, Data Science...\n'
    assert sections['benefits'] == \
        'An inclusive and diverse work environment...\n'


def test_split_by_lang() -> None:
    """Test the _split_by_lang function. (Copilt)"""
    data = {
        "file_path": ["file1", "file2", "file3", "file4"],
        "eml_lang": ["en", "de", "en", "de"],
        "payload": ["payload1", "payload2", "payload3", "payload4"]
    }
    df = pd.DataFrame(data)

    expected_en = pd.DataFrame({
        "file_path": ["file1", "file3"],
        "eml_lang": ["en", "en"],
        "payload": ["payload1", "payload3"]
    })

    expected_de = pd.DataFrame({
        "file_path": ["file2", "file4"],
        "eml_lang": ["de", "de"],
        "payload": ["payload2", "payload4"]
    })

    result = _split_by_lang(df)

    assert "en" in result
    assert "de" in result
    pd.testing.assert_frame_equal(
        result["en"].reset_index(drop=True), expected_en)
    pd.testing.assert_frame_equal(
        result["de"].reset_index(drop=True), expected_de)


def test_split_double_newline() -> None:
    """Test the _split_double_newline function."""
    data = {
        "payload": [
            "Hello\n\nWorld",              # Simple case
            "Hello\n\n\n\nWorld",          # Multiple newlines
            "Only one line",               # No double newlines
            "\n\n\n\n",                    # Only newlines
            "Line1\n\nLine2\n\n\n\nLine3"  # Mixed spacing
        ]
    }
    df = pd.DataFrame(data)

    result = _split_double_newline(df)

    # Check resulting splits
    # 1) "Hello\n\nWorld" -> ["Hello", "World"]
    assert result.iloc[0] == ["Hello", "World"]

    # 2) "Hello\n\n\n\nWorld" -> ["Hello", "World"]
    #    Extra newlines in the middle should still split into just two items
    assert result.iloc[1] == ["Hello", "World"]

    # 3) "Only one line" -> ["Only one line"]
    #    No double newline => only one item
    assert result.iloc[2] == ["Only one line"]

    # 4) "\n\n\n\n" -> []
    #    Empty (only newlines), everything should be filtered out
    assert result.iloc[3] == []

    # 5) "Line1\n\nLine2\n\n\n\nLine3" -> ["Line1", "Line2", "Line3"]
    assert result.iloc[4] == ["Line1", "Line2", "Line3"]


def test_filter_item():
    """
    Test the _filter_item function with different newline,
    [URL], and dash counts.
    """
    items = [
        "No newlines, no URL",
        "One newline\nNo URL",
        "One newline\nHas [URL]",
        "Three newlines\n\n\nAnd four----dashes",
        "Two newlines\n\nAnd four----dashes",
    ]

    result = _filter_item(items, max_newlines=2, min_dashes=3)

    expected = [
        "One newline\nNo URL",
        "Three newlines\n\n\nAnd four----dashes"
    ]

    assert result == expected, f"Expected {expected}, got {result}"


def test_extract_title_none_found():
    """
    Test that _extract_title returns 'Nan' if neither '(m/w/d)' nor '(f/m/x)'
    is found in any item of row['clean_payload'].
    """
    row = pd.Series({
        "clean_payload": [
            "Just some random text.\nNothing special here.",
            "Another block of text without any markers."
        ]
    })
    assert _extract_title(row) == "Nan"


def test_extract_title_mwd_found():
    """
    Test that _extract_title returns the line with '(m/w/d)' if it appears.
    """
    row = pd.Series({
        "clean_payload": [
            "We have a lot of content here.",
            "Job Title (m/w/d)\nAnd some extra lines here."
        ]
    })
    expected = "Job Title (m/w/d)"
    result = _extract_title(row)
    assert result == expected, f"Expected '{expected}', but got '{result}'"


def test_extract_title_fmx_found():
    """
    Test that _extract_title returns the line with '(f/m/x)' if it appears.
    """
    row = pd.Series({
        "clean_payload": [
            "Some text\nstill no marker.",
            "Another block\nJob Family Title (f/m/x)\nEven more lines."
        ]
    })
    expected = "Job Family Title (f/m/x)"
    result = _extract_title(row)
    assert result == expected, f"Expected '{expected}', but got '{result}'"


def test_extract_title_multiple_matches():
    """
    Test that _extract_title returns the FIRST matching line
    if multiple matches are present in row['clean_payload'].
    """
    row = pd.Series({
        "clean_payload": [
            "Something else (m/w/d)\nInside first block.\nAnother line.",
            "Second block with (f/m/x)\nShould not be returned."
        ]
    })
    # Should return the line from the first block it encounters
    expected = "Something else (m/w/d)"
    result = _extract_title(row)
    assert result == expected, f"Expected '{expected}', but got '{result}'"


class TestFetchFromYaml(unittest.TestCase):
    """Test the YAML reader function `_fetch_from_yaml`."""

    def test_fetch_from_yaml_success(self):
        """
        Test _fetch_from_yaml successfully reads and parses a YAML file.
        """
        cfg = DictConfig({
            "taxonomy_path": "/some/dir",
            "taxonomy_files": {
                "locations": "locations.yaml"
            }
        })
        fake_yaml = """
        cities:
          - Berlin
          - Munich
        """
        mocked_open = mock_open(read_data=fake_yaml)
        with patch("pathlib.Path.open", mocked_open):
            result = _fetch_from_yaml(cfg, 'locations')
        self.assertEqual(
            result, {"cities": ["Berlin", "Munich"]},
            "Should parse YAML data correctly."
        )

    def test_fetch_from_yaml_file_not_found(self):
        """
        Test _fetch_from_yaml raises SystemExit when the file is missing.
        """
        cfg = DictConfig({
            "taxonomy_path": "/some/dir",
            "taxonomy_files": {
                "locations": "missing.yaml"
            }
        })
        mocked_open = mock_open()
        mocked_open.side_effect = FileNotFoundError
        with patch("pathlib.Path.open", mocked_open), \
             self.assertRaises(SystemExit) as context:
            _fetch_from_yaml(cfg, 'locations')
        self.assertIn("does not exist!", str(context.exception))

    def test_fetch_from_yaml_format_error(self):
        """
        Test _fetch_from_yaml raises SystemExit when the YAML is invalid.
        """
        cfg = DictConfig({
            "taxonomy_path": "/some/dir",
            "taxonomy_files": {
                "locations": "invalid.yaml"
            }
        })
        mocked_open = mock_open(read_data=": invalid: yaml")
        # Force yaml.safe_load to raise YAMLError
        with patch("pathlib.Path.open", mocked_open), \
             patch("yaml.safe_load", side_effect=yaml.YAMLError), \
             self.assertRaises(SystemExit) as context:
            _fetch_from_yaml(cfg, 'locations')
        self.assertIn("not a valid YAML file!", str(context.exception))

    def test_fetch_from_yaml_unknown_error(self):
        """
        Test _fetch_from_yaml raises SystemExit for any other exception.
        """
        cfg = DictConfig({
            "taxonomy_path": "/some/dir",
            "taxonomy_files": {
                "locations": "error.yaml"
            }
        })
        mocked_open = mock_open()
        mocked_open.side_effect = ValueError("Some unknown error")
        with patch("pathlib.Path.open", mocked_open), \
             self.assertRaises(SystemExit) as context:
            _fetch_from_yaml(cfg, 'locations')
        self.assertIn("Unknown Error", str(context.exception))



class TestExtractMatchingItem(unittest.TestCase):
    def test_match_single_item(self):
        """Checks that a simple match returns the expected item."""
        items = ["Data Scientist", "Machine Learning"]
        title = "We need a Data Scientist who can handle advanced analytics."
        result = _extract_matching_item(title, items)
        self.assertEqual(result, "Data Scientist")

    def test_match_is_case_insensitive(self):
        """Ensures matching is case-insensitive."""
        items = ["datascientist", "engineer"]
        title = "We are hiring a Senior DATAScientist to join our team."
        result = _extract_matching_item(title, items)
        self.assertEqual(result, "datascientist")

    def test_partial_word_no_match(self):
        """
        Ensures partial words are not matched and "nan" is returned
        if no full match is found.
        """
        items = ["Data"]
        title = "We need a Database developer."
        result = _extract_matching_item(title, items)
        self.assertEqual(result, "nan")

    def test_returns_first_of_multiple_items(self):
        """
        Checks that if multiple items can match, the function
        returns the first match it finds in 'items'.
        """
        items = ["Data Scientist", "Data Engineer", "Data Analyst"]
        title = "We need a Data Engineer, but we also need an Analyst."
        # Because "Data Engineer" appears first in the list, and
        # it matches the title text first, "Data Engineer" is returned.
        # If the function checks them in order, that's what we'll get.
        result = _extract_matching_item(title, items)
        self.assertEqual(result, "Data Engineer")


if __name__ == "__main__":
    unittest.main()
