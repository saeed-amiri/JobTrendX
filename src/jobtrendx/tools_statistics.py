"""Do the statistics for analyzing the ads"""

import pandas as pd


__all__ = [
    'anlz_titles'
]


def anlz_titles(titles: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    """
    Analyze the titles of the jobs, count them, and return
    statistics.

    Args:
        titles (pd.Series): A pandas Series containing job
        titles.

    Returns:
        tuple[pd.DataFrame, pd.Series]: A summary DataFrame
        with statistics and a Series with the top counts.
    """
    titles = titles.astype(str).str.strip()
    titles = titles.replace(['nan', 'Nan', ''], pd.NA)

    total: int = len(titles)
    missing: int = titles.isna().sum()
    valids: int = total - missing

    unique: int = titles.nunique(dropna=True)
    top = titles.value_counts(dropna=True)

    summary = pd.DataFrame({
        'Total': [total],
        'Valid': [valids],
        'Missing': [missing],
        'Unique Titles': [unique]
    })
    return summary, top
