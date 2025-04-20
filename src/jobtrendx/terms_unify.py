"""
Unify the different terms mentioned in the emails for the
term, also, it could be because of the translation to German
e.g.:
Machine Learning:
  - Machine Learning
  - ML
  - KI
  - KI Forscher
  - Machine Learning Engineer

18 Apr. 2025
S. Amiri
"""

import sys
from pathlib import Path

import yaml
import pandas as pd

from omegaconf import DictConfig


__all__ = [
    'term_unifier'
]


def term_unifier(df_info: pd.DataFrame,
                 cfg: DictConfig
                 ) -> pd.DataFrame:
    """unify the terms in the columns"""
    job_lexcion: dict[str, list[str]] = _fetch_from_yaml(cfg, 'job_titles')
    skill_lexicon: dict[str, list[str]] = _fetch_from_yaml(cfg, 'skills')
    language_lexicon: dict[str, list[str]] = _fetch_from_yaml(cfg, 'languages')

    df_info = _replace_str(job_lexcion, df_info, 'job_title')
    df_info = _replace_list_str(skill_lexicon, df_info, 'skills')
    df_info = _replace_list_str(language_lexicon, df_info, 'language')
    return df_info


def _replace_str(lexicon: dict[str, list[str]],
                 df: pd.DataFrame,
                 column: str
                 ) -> pd.DataFrame:
    """
    Replace the strings in the specified column with the corresponding
    keys from the lexicon dictionary.
    """
    # Create a reverse mapping of all values to their corresponding keys
    value_to_key = _invert_lexicon(lexicon=lexicon)

    # Replace values in the column using the mapping
    df[column] = df[column].apply(
        lambda item: value_to_key.get(item, item) if pd.notna(item) else item
    )
    return df


def _replace_list_str(lexicon: dict[str, list[str]],
                      df: pd.DataFrame,
                      column: str
                      ) -> pd.DataFrame:
    """
    Replace the strings in a list of strings in the specified
    column with the corresponding keys from the lexicon
    dictionary. Deduplicates the resulting list.
    """
    # Create a reverse mapping of all values to their corresponding keys
    value_to_key = _invert_lexicon(lexicon=lexicon)

    # Replace and deduplicate values in the column
    def process_list(item_list):
        if isinstance(item_list, list):
            # Replace items and deduplicate in one step
            return list({value_to_key.get(item, item) for item in item_list})
        return item_list

    df[column] = df[column].apply(process_list)
    df[column] = df[column].apply(lambda x: sorted(x) if
                                  isinstance(x, list) else x)
    return df


def _invert_lexicon(lexicon: dict[str, list[str]]
                    ) -> dict[str, str]:
    """Invert the lexicon to simplify the search"""
    return {value: key for key, values in lexicon.items() for value in values}


def _fetch_from_yaml(cfg: DictConfig,
                     file_type: str
                     ) -> dict[str, list[str]]:
    """
    Reads the YAML file containing location data and returns
    a dictionary of items in the yaml

    Args:
        cfg (DictConfig): Configuration object containing
        paths to lexicon files.

    Returns:
        dict[str, list[str]]: Dictionary of city names grouped
        by states names.

    Raises:
        SystemExit: If the file is not found, has a format
        error, or an unknown error occurs.
    """
    # pylint: disable=broad-exception-caught
    file_path = Path(cfg.lexicon_path) / cfg.lexicon_files[file_type]
    try:
        with file_path.open('r', encoding='utf-8') as f_loc:
            return yaml.safe_load(f_loc)
    except FileNotFoundError:
        sys.exit(f"\nFile Not Found:\n`{file_path}` does not exist!")
    except yaml.YAMLError:
        sys.exit(f"\nFile Format Error:\n`{file_path}` not a valid YAML file!")
    except Exception as err:
        sys.exit(f"Unknown Error in `{file_path}`: {err}")
