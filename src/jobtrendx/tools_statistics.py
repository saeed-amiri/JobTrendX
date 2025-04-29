"""Do the statistics for analyzing the ads"""

import sys
from itertools import chain
import yaml
from pathlib import Path

import pandas as pd

from omegaconf import DictConfig


__all__ = [
    'anlz_string_cols',
    'anlz_list_cols',
    'anlz_numerical_cols',
    'anlz_by_category'
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
    # Drop rows with zero values
    clean_col = clean_col[clean_col != 0]

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


def anlz_by_category(col: pd.Series,
                     cfg: DictConfig,
                     subject: str
                     ) -> tuple[pd.DataFrame, pd.Series]:
    """
    Analyze each sub-category by checking the skills in the
    column (a series of lists) and finding which key of the
    taxonomy they belong to. Then, get the statistics for
    each key.

    Args:
        col (pd.Series): A pandas Series where each entry is
        expected to be a list of skills or NaN.
        cfg (DictConfig): Configuration object containing
        paths to taxonomy files.
        subject (str): The subject to analyze (e.g., 'skills').

    Returns:
        tuple[pd.DataFrame, pd.Series]: A summary DataFrame
        with statistics and a Series with counts for each
        category.
    """
    taxonomy: dict[str, list[str]] = _fetch_from_yaml(cfg, subject)

    # Ensure all non-list entries are replaced with empty lists
    clean_col: pd.Series = col.dropna().apply(
        lambda x: x if isinstance(x, list) else []
    )

    # Flatten the list elements
    flat_items = list(chain.from_iterable(clean_col))

    # Initialize a dictionary to store counts for each key
    category_counts = {key: 0 for key in taxonomy.keys()}

    # Count occurrences of each item in the taxonomy keys
    for key, items in taxonomy.items():
        category_counts[key] = sum(item in items for item in flat_items)

    # Calculate basic statistics
    total: int = len(col)
    missing: int = col.isna().sum()
    valids: int = total - missing
    unique_categories: int = \
        sum(1 for count in category_counts.values() if count > 0)

    # Create a summary DataFrame
    summary = pd.DataFrame({
        "Total": [total],
        "Valid": [valids],
        "Missing": [missing],
        "Unique Categories": [unique_categories]
    })

    # Convert the counts dictionary to a Series
    counts = pd.Series(category_counts, name="Count")
    # Sort the counts in descending order^
    counts = counts.sort_values(ascending=False)

    return summary, counts


def _fetch_from_yaml(cfg: DictConfig,
                     file_type: str
                     ) -> dict[str, list[str]]:
    """
    Reads the YAML file containing location data and returns
    a dictionary of items in the yaml

    Args:
        cfg (DictConfig): Configuration object containing
        paths to taxonomy files.

    Returns:
        dict[str, list[str]]: Dictionary of city names grouped
        by states names.

    Raises:
        SystemExit: If the file is not found, has a format
        error, or an unknown error occurs.
    """
    # pylint: disable=broad-exception-caught
    file_path = Path(cfg.taxonomy_path) / cfg.taxonomy_files[file_type]
    try:
        with file_path.open('r', encoding='utf-8') as f_loc:
            return yaml.safe_load(f_loc)
    except FileNotFoundError:
        sys.exit(f"\nFile Not Found:\n`{file_path}` does not exist!")
    except yaml.YAMLError:
        sys.exit(f"\nFile Format Error:\n`{file_path}` not a valid YAML file!")
    except Exception as err:
        sys.exit(f"Unknown Error in `{file_path}`: {err}")
