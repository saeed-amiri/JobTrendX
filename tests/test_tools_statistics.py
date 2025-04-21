"""
Tests for the statistics tools
"""

import unittest
import pandas as pd
from jobtrendx.tools_statistics import anlz_string_cols, anlz_list_cols


class TestAnlzTitles(unittest.TestCase):
    """Test the titles analysis"""

    def setUp(self):
        """Set up sample data for testing."""
        self.titles = pd.Series([
            "Data Scientist", "Data Engineer", "Data Scientist",
            "Machine Learning Engineer", None, "nan", "Nan", ""
        ])

    def test_anlz_string_cols_summary(self):
        """
        Test if anlz_string_cols correctly calculates the summary
        statistics.
        """
        summary, _ = anlz_string_cols(self.titles)
        expected_summary = pd.DataFrame({
            'Total': [8],
            'Valid': [4],
            'Missing': [4],
            'Unique col': [3]
        })
        pd.testing.assert_frame_equal(summary, expected_summary)

    def test_anlz_string_cols_top_counts(self):
        """
        Test if anlz_string_cols correctly calculates the top
        counts.
        """
        _, top = anlz_string_cols(self.titles)
        expected_top = pd.Series({
            "Data Scientist": 2,
            "Data Engineer": 1,
            "Machine Learning Engineer": 1
        }, name='count')
        pd.testing.assert_series_equal(top, expected_top)



class TestAnlzListCols(unittest.TestCase):
    """test analyzing the columns with series in them"""

    def setUp(self):
        """Set up sample data for testing."""
        self.data = pd.Series([
            ["Python", "SQL", "Python"],
            ["Java", "C++"],
            None,
            [],
            ["Python", "Java"],
            ["SQL"],
            None
        ])

    def test_anlz_list_cols_summary(self):
        """
        Test if anlz_list_cols correctly calculates the
        summary statistics.
        """
        summary, _ = anlz_list_cols(self.data)
        expected_summary = pd.DataFrame({
            "Total": [7],
            "Valid": [5],
            "Missing": [2],
            "Unique Items": [4]
        })
        pd.testing.assert_frame_equal(summary, expected_summary)

    def test_anlz_list_cols_counts(self):
        """
        Test if anlz_list_cols correctly calculates the top
        counts."""
        _, counts = anlz_list_cols(self.data)
        expected_counts = pd.Series({
            "Python": 3,
            "SQL": 2,
            "Java": 2,
            "C++": 1
        }, name='count')
        pd.testing.assert_series_equal(counts, expected_counts)



if __name__ == "__main__":
    unittest.main()
