"""Do the statistics for analyzing the ads"""

from itertools import chain

import pandas as pd


__all__ = [
    'anlz_string_cols',
    'anlz_list_cols'
]


def anlz_string_cols(col: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    """
    Analyze the col of the strings (e.g., jobs), count them,
    and return statistics.

    Args:
        col (pd.Series): A pandas Series containing job
        col.

    Returns:
        tuple[pd.DataFrame, pd.Series]: A summary DataFrame
        with statistics and a Series with the top counts.
    """
    col = col.astype(str).str.strip()
    col = col.replace(['nan', 'Nan', 'None', '', None], pd.NA)

    total: int = len(col)
    missing: int = col.isna().sum()
    valids: int = total - missing

    unique: int = col.nunique(dropna=True)
    counts = col.value_counts(dropna=True)

    summary = pd.DataFrame({
        'Total': [total],
        'Valid': [valids],
        'Missing': [missing],
        'Unique col': [unique]
    })
    return summary, counts


def anlz_list_cols(col: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    """
    Analyze columns containing lists, count their elements,
    and return statistics.

    Args:
        col (pd.Series): A pandas Series where each entry is
        expected to be a list or NaN.

    Returns:
        tuple[pd.DataFrame, pd.Series]: A summary DataFrame
        with statistics and a Series with the top counts of
        flattened list elements.
    """
    # Ensure all non-list entries are replaced with empty lists
    clean_col: pd.Series = col.dropna().apply(
        lambda x: x if isinstance(x, list) else []
    )

    # Calculate basic statistics
    total: int = len(col)
    missing: int = col.isna().sum()
    valids: int = total - missing

    # Flatten the list elements and count occurrences
    flat_items = list(chain.from_iterable(clean_col))
    counts = pd.Series(flat_items).value_counts()

    # Create a summary DataFrame
    summary = pd.DataFrame({
        "Total": [total],
        "Valid": [valids],
        "Missing": [missing],
        "Unique Items": [counts.size]
    })

    return summary, counts


def anlz_numerical_cols(col: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    """
    Analyze columns containing numerical data, calculate
    statistics,
    and return a summary DataFrame and a Series with
    descriptive statistics.

    Args:
        col (pd.Series): A pandas Series containing numerical
        data.

    Returns:
        tuple[pd.DataFrame, pd.Series]: A summary DataFrame
        with statistics and a Series with descriptive
        statistics.
    """
    col = col.replace(['nan', 'Nan', 'None', '', None], pd.NA)
    clean_col: pd.Series = col.dropna().astype(float)

    total: int = len(col)
    missing: int = col.isna().sum()
    valids: int = total - missing

    # Calculate descriptive statistics
    descriptive_stats = clean_col.describe()

    # Create a summary DataFrame
    summary = pd.DataFrame({
        "Total": [total],
        "Valid": [valids],
        "Missing": [missing],
        "Mean": [descriptive_stats["mean"]],
        "Std Dev": [descriptive_stats["std"]],
        "Min": [descriptive_stats["min"]],
        "Max": [descriptive_stats["max"]]
    })

    return summary, descriptive_stats
