"""
Test the module of cleaning up the dataframe
"""

import unittest
import pandas as pd
from jobtrendx.clean_dataframe import (
    remove_duplicate,
    _get_list_columns,
    _convert_list_to_string,
    _drop_duplicates,
    _convert_strings_to_lists
)


class TestRemoveDuplicate(unittest.TestCase):
    """test the drop duplicates"""

    def setUp(self):
        """Set up a sample DataFrame for testing."""
        self.df = pd.DataFrame({
            "file_path": ["file1", "file2", "file3", "file4"],
            "skills": [["Python", "SQL"], ["Python", "SQL"], ["Java"],
                       ["Python"]],
            "job_title": ["Data Scientist", "Data Scientist", "Engineer",
                          "Data Scientist"]
        })

    def test_get_list_columns(self):
        """Test if _get_list_columns correctly identifies
        list-type columns."""
        list_cols = _get_list_columns(self.df)
        self.assertListEqual(list_cols, ["skills"])

    def test_convert_list_to_string(self):
        """Test if _convert_list_to_string correctly converts
        lists to strings."""
        list_cols = ["skills"]
        df_converted = _convert_list_to_string(self.df.copy(), list_cols)
        expected = ["Python-SQL", "Python-SQL", "Java", "Python"]
        self.assertListEqual(df_converted["skills"].tolist(), expected)

    def test_drop_duplicates(self):
        """Test if _drop_duplicates correctly removes duplicate
        rows."""
        df_converted = _convert_list_to_string(self.df.copy(), ["skills"])
        df_deduplicated = _drop_duplicates(df_converted)
        self.assertEqual(len(df_deduplicated), 3)

    def test_convert_strings_to_lists(self):
        """Test if _convert_strings_to_lists correctly
        converts strings back to lists."""
        list_cols = ["skills"]
        df_converted = _convert_list_to_string(self.df.copy(), list_cols)
        df_reverted = _convert_strings_to_lists(df_converted, list_cols)
        expected = [["Python", "SQL"], ["Python", "SQL"], ["Java"], ["Python"]]
        self.assertListEqual(df_reverted["skills"].tolist(), expected)

    def test_remove_duplicate(self):
        """Test the full remove_duplicate function."""
        df_cleaned = remove_duplicate(self.df.copy())
        expected_skills = [["Python", "SQL"], ["Java"], ["Python"]]
        expected_job_titles = ["Data Scientist", "Engineer", "Data Scientist"]
        self.assertEqual(len(df_cleaned), 3)
        self.assertListEqual(df_cleaned["skills"].tolist(), expected_skills)
        self.assertListEqual(df_cleaned["job_title"].tolist(),
                             expected_job_titles)


if __name__ == "__main__":
    unittest.main()
