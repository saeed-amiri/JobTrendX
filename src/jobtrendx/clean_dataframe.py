"""
Remove duplicate rows from possible multiple similar email

20 Apr. 2025
S. Amiri
"""

import pandas as pd


__all__ = [
    'remove_duplicate'
]


def remove_duplicate(df_info: pd.DataFrame,
                     ) -> pd.DataFrame:
    """
    Remove duplicated rows (emails) from the DataFrame.
    Handles columns with list-type elements by converting
    them to strings for comparison and then back to lists.
    """
    list_cols: list[str] = _get_list_columns(df_info)
    df_info = _convert_list_to_string(df_info, list_cols)
    df_info = _drop_duplicates(df_info)
    df_info = _convert_strings_to_lists(df_info, list_cols)
    df_info = _order_dataframe(df_info, 'file_path')
    return df_info


def _get_list_columns(df: pd.DataFrame) -> list[str]:
    """
    Identify columns in the DataFrame that contain list-type
    elements.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        list[str]: List of column names containing list-type
        elements.
    """
    return [col for col in df.columns if
            df[col].apply(lambda x: isinstance(x, list)).any()]


def _convert_list_to_string(df: pd.DataFrame,
                            cols: list[str]
                            ) -> pd.DataFrame:
    """
    Convert list-type elements in specified columns to strings
    for comparison.

    Args:
        df (pd.DataFrame): The input DataFrame.
        cols (list[str]): List of column names to process.

    Returns:
        pd.DataFrame: DataFrame with lists converted to strings.
    """
    for col in cols:
        df.loc[:, col] = df[col].apply(lambda x: '-'.join(x)
                                       if isinstance(x, list) else x)
    return df


def _drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop duplicate rows from the DataFrame, ignoring the
    'file_path' column.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with duplicates removed.
    """
    df = df.drop_duplicates(subset=df.columns.difference(['file_path']),
                            keep='first',
                            ignore_index=True)
    return df


def _convert_strings_to_lists(df: pd.DataFrame,
                              cols: list[str]
                              ) -> pd.DataFrame:
    """
    Convert string-type elements in specified columns back
    to lists.

    Args:
        df (pd.DataFrame): The input DataFrame.
        cols (list[str]): List of column names to process.

    Returns:
        pd.DataFrame: DataFrame with strings converted back
        to lists.
    """
    for col in cols:
        df.loc[:, col] = df[col].apply(lambda x: x.split('-'))
    return df


def _order_dataframe(df: pd.DataFrame,
                     col: str
                     ) -> pd.DataFrame:
    """
    Order the dataframe by the specified column.

    Args:
        df (pd.DataFrame): The input DataFrame.
        col (str): The column name to sort by.

    Returns:
        pd.DataFrame: The sorted DataFrame.
    """
    if col in df.columns:
        df = df.sort_values(by=col, ascending=True, ignore_index=True)
    return df
