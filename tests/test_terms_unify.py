"""
Testing the term_unify module
"""
# pylint: disable=redefined-outer-name

import unittest

import pandas as pd

from jobtrendx.terms_unify import _replace_str, _invert_lexicon, \
    _replace_list_str


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


class TestReplaceListStr(unittest.TestCase):
    """test if the replace in the list works"""

    def setUp(self):
        """Set up a sample DataFrame and lexicon for testing."""
        self.df = pd.DataFrame({
            "skills": [
                ["Python", "ML", "KI", "Python"],
                ["Data Science", "AI", "KI"],
                ["SQL", "Python", "SQL"],
                None
            ]
        })
        self.lexicon = {
            "Machine Learning": ["ML", "KI"],
            "Programming Language": ["Python", "R"],
            "Data Science": ["Data Science", "AI"]
        }

    def test_replace_list_str(self):
        """
        Test if _replace_list_str correctly replaces and
        deduplicates terms.
        """
        _replace_list_str(self.lexicon, self.df, "skills")
        expected = [
            ["Machine Learning", "Programming Language"],
            ["Data Science", "Machine Learning"],
            ["Programming Language"],
            None
        ]
        expected = [item.sort() for item in expected if item]
        results = [item.sort() for item in self.df["skills"].tolist() if item]
        self.assertListEqual(results, expected)


if __name__ == "__main__":
    unittest.main()
