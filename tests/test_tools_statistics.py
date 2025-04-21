"""
Tests for the statistics tools
"""

import unittest
import pandas as pd
from jobtrendx.tools_statistics import anlz_titles


class TestAnlzTitles(unittest.TestCase):
    """Test the titles analysis"""

    def setUp(self):
        """Set up sample data for testing."""
        self.titles = pd.Series([
            "Data Scientist", "Data Engineer", "Data Scientist",
            "Machine Learning Engineer", None, "nan", "Nan", ""
        ])

    def test_anlz_titles_summary(self):
        """
        Test if anlz_titles correctly calculates the summary
        statistics.
        """
        summary, _ = anlz_titles(self.titles)
        expected_summary = pd.DataFrame({
            'Total': [8],
            'Valid': [4],
            'Missing': [4],
            'Unique Titles': [3]
        })
        pd.testing.assert_frame_equal(summary, expected_summary)

    def test_anlz_titles_top_counts(self):
        """
        Test if anlz_titles correctly calculates the top
        counts.
        """
        _, top = anlz_titles(self.titles)
        expected_top = pd.Series({
            "Data Scientist": 2,
            "Data Engineer": 1,
            "Machine Learning Engineer": 1
        }, name='count')
        pd.testing.assert_series_equal(top, expected_top)


if __name__ == "__main__":
    unittest.main()
