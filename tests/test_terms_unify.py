"""
Testing the term_unify module
"""
# pylint: disable=redefined-outer-name

import unittest

import pandas as pd

from jobtrendx.terms_unify import _replace_str, _invert_lexicon


class TestReplaceStr(unittest.TestCase):
    """test replacing strings"""

    def setUp(self):
        """Set up a sample DataFrame and lexicon for testing."""
        self.df = pd.DataFrame({
            "job_title": [
                "Datenanalyst", "Data Scientist", "Data Engineer",
                "Data Scientist", None, "Data Analyst", "Business Analyst"
            ]
        })
        self.lexicon = {
            "Data Scientist": ["Data Scientist", "Datenwissenschaftler"],
            "Data Analyst": ["Data Analyst", "Datenanalyst"],
            "Data Engineer": ["Data Engineer"]
        }

    def test_replace_str(self):
        """
        Test if _replace_str correctly replaces terms based on the lexicon.
        """
        _replace_str(self.lexicon, self.df, "job_title")
        expected = [
            "Data Analyst", "Data Scientist", "Data Engineer",
            "Data Scientist", None, "Data Analyst", "Business Analyst"
        ]
        self.assertListEqual(self.df["job_title"].tolist(), expected)

    def test_invert_lexicon(self):
        """Test if _invert_lexicon correctly inverts the lexicon."""
        inverted = _invert_lexicon(self.lexicon)
        expected = {
            "Data Scientist": "Data Scientist",
            "Datenwissenschaftler": "Data Scientist",
            "Data Analyst": "Data Analyst",
            "Datenanalyst": "Data Analyst",
            "Data Engineer": "Data Engineer"
        }
        self.assertDictEqual(inverted, expected)


if __name__ == "__main__":
    unittest.main()
