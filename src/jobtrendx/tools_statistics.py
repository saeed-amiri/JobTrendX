"""Do the statistics for analyzing the ads"""

import pandas as pd


__all__ = [
    'anlz_string_cols'
]


def anlz_string_cols(col: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    """
    Analyze the col of the jobs, count them, and return
    statistics.

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
    top = col.value_counts(dropna=True)

    summary = pd.DataFrame({
        'Total': [total],
        'Valid': [valids],
        'Missing': [missing],
        'Unique col': [unique]
    })
    return summary, top
