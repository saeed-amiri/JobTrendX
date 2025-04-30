"""
Testing the payload_analysis module
"""
# pylint: disable=redefined-outer-name

import unittest
from unittest.mock import patch, mock_open

import yaml
import pandas as pd
from omegaconf import DictConfig

from jobtrendx.payload_analysis import \
    _split_double_newline, _filter_item, _extract_title, \
    _extract_matching_item, _extract_all_items, _extract_salary, \
    _get_salary_amount
from jobtrendx.sub_tools import fetch_from_yaml

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
        "Diesen Job melden",
        "Extra newline\nHas [URL]",
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
    tags: list[str] = ['m/w/d', 'f/m/x']
    assert _extract_title(row, tags) == "Nan"


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
    tags: list[str] = ['m/w/d', 'f/m/x']
    expected = "Job Title (m/w/d)"
    result = _extract_title(row, tags)
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
    tags: list[str] = ['m/w/d', 'f/m/x']
    result = _extract_title(row, tags)
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
    tags: list[str] = ['m/w/d', 'f/m/x']
    result = _extract_title(row, tags)
    assert result == expected, f"Expected '{expected}', but got '{result}'"


class TestFetchFromYaml(unittest.TestCase):
    """Test the YAML reader function `fetch_from_yaml`."""

    def testfetch_from_yaml_success(self):
        """
        Test fetch_from_yaml successfully reads and parses a YAML file.
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
            result = fetch_from_yaml(
                cfg.taxonomy_path, cfg.taxonomy_files['locations'])
        self.assertEqual(
            result, {"cities": ["Berlin", "Munich"]},
            "Should parse YAML data correctly."
        )

    def testfetch_from_yaml_file_not_found(self):
        """
        Test fetch_from_yaml raises SystemExit when the file is missing.
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
            fetch_from_yaml(cfg.taxonomy_path, cfg.taxonomy_files['locations'])
        self.assertIn("does not exist!", str(context.exception))

    def testfetch_from_yaml_format_error(self):
        """
        Test fetch_from_yaml raises SystemExit when the YAML is invalid.
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
            fetch_from_yaml(cfg.taxonomy_path, cfg.taxonomy_files['locations'])
        self.assertIn("not a valid YAML file!", str(context.exception))

    def testfetch_from_yaml_unknown_error(self):
        """
        Test fetch_from_yaml raises SystemExit for any other exception.
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
           fetch_from_yaml(cfg.taxonomy_path, cfg.taxonomy_files['locations'])
        self.assertIn("Unknown Error", str(context.exception))


class TestExtractMatchingItem(unittest.TestCase):
    """test if we a single item work"""
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


class TestExtractAllItems(unittest.TestCase):
    """test if gettinge all the skills from the emails work"""

    def test_extract_all_items_single_match(self):
        """
        Ensures a single item that appears in the payload is
        matched.
        """
        row = pd.Series({
            "clean_payload": [
                "Python is a popular language for data science."
            ]
        })
        items = ["Python", "R"]
        found = _extract_all_items(row, items)
        self.assertEqual(found, ["Python"])

    def test_extract_all_items_multiple_matches(self):
        """
        Ensures multiple items are matched when they appear.
        """
        row = pd.Series({
            "clean_payload": [
                "We use TensorFlow and Spark for big data processing."
            ]
        })
        items = ["TensorFlow", "Spark", "PyTorch"]
        found = _extract_all_items(row, items)
        self.assertCountEqual(found, ["TensorFlow", "Spark"])

    def test_extract_all_items_no_match(self):
        """
        Ensures ["nan"] is returned when no items match.
        """
        row = pd.Series({
            "clean_payload": [
                "No recognized skill is mentioned here."
            ]
        })
        items = ["Python", "TensorFlow"]
        found = _extract_all_items(row, items)
        self.assertEqual(found, ["nan"])


class TestExtractSalaryFunctions(unittest.TestCase):
    """Test extracing salaries"""

    def test_extract_salary_monat(self):
        """
        Checks if a line mentioning salary per month is converted
        to annual values.
        """
        row = pd.Series({
            "clean_payload": [
                "This is some text.",
                "The estimated salary range is 5.500 - 7.500 €/Monat"
            ]
        })
        items = ["salary", "€"]  # "€" will trigger the check.
        min_salary, max_salary, unit = _extract_salary(row, items)
        self.assertEqual(min_salary, 66000.0,
                         "Should convert min monthly salary to annual.")
        self.assertEqual(max_salary, 90000.0,
                         "Should convert max monthly salary to annual.")
        self.assertEqual(unit, "€/Jahr",
                         "Uses '€/Jahr' when monthly data is found.")

    def test_extract_salary_jahr(self):
        """
        Checks if a line with an annual salary remains unchanged.
        """
        row = pd.Series({
            "clean_payload": [
                "This is some text.",
                "The estimated salary range is 66.000 - 90.000 €/Jahr"
            ]
        })
        items = ["salary", "€"]
        min_salary, max_salary, unit = _extract_salary(row, items)
        self.assertEqual(min_salary, 66000.0)
        self.assertEqual(max_salary, 90000.0)
        self.assertEqual(unit, "€/Jahr")

    def test_extract_salary_no_match(self):
        """
        Ensures "Nan", "Nan", "Nan" are returned when no salary keywords match.
        """
        row = pd.Series({
            "clean_payload": [
                "No salary provided here."
            ]
        })
        items = ["€", "salary"]
        min_salary, max_salary, unit = _extract_salary(row, items)
        self.assertEqual(min_salary, "Nan")
        self.assertEqual(max_salary, "Nan")
        self.assertEqual(unit, "Nan")

    def test_get_salary_amount_monat_direct(self):
        """
        Tests _get_salary_amount directly for a monthly range line.
        """
        line = "5.500 - 7.500 €/Monat"
        min_sal, max_sal, unit = _get_salary_amount(line)
        self.assertEqual(min_sal, 66000.0)
        self.assertEqual(max_sal, 90000.0)
        self.assertEqual(unit, "€/Jahr")

    def test_get_salary_amount_no_euro(self):
        """
        Tests _get_salary_amount returns Nan if '€' is missing.
        """
        line = "66.000 - 90.000 per year"
        min_sal, max_sal, unit = _get_salary_amount(line)
        self.assertEqual(min_sal, "Nan")
        self.assertEqual(max_sal, "Nan")
        self.assertEqual(unit, "Nan")


if __name__ == "__main__":
    unittest.main()
