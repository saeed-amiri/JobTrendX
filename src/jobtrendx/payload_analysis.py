"""
Analyzing the "payload" section of the emails.
Emails contains several sections, depends on the language of
the email, these sections have different titles.
This titles are set in cfg/defaults/analysis.yaml:

sections:
  job_title: ["Beliebter Job", "Top Treffer"]
  company_info: ["Wer wir sind.", "Lloyds Bank GmbH and its brands"]
  job_description: ["Das wird dein Job", "Your tasks"]
  requirements: ["Das bringst du mit", "Your knowledge/experience"]
  offer: ["Das bieten wir dir", "We offer"]

This module first separate the "payload" text based on the
sections and than grep the information of each sections and
return them.

26 Feb. 2025
Samiri
"""

import re
import sys
from pathlib import Path

import yaml
import pandas as pd

from omegaconf import DictConfig

__all__ = [
    'split_payload',
    'analysis_job_title',
    'analysis_top_skills'
]


def split_payload(payloads: pd.DataFrame,
                  cfg: DictConfig
                  ) -> pd.DataFrame:

    """splitting the payload of the emails based on the sections
    titles"""
    # Not implemented yet!
    # Get the fixed sections in the Config
    sections: dict[str, dict[str, str]] = cfg.defaults.analysis.sections

    # Get the name of the cities from a yaml file
    locations: dict[str, list[str]] = _fetch_from_yaml(cfg, 'locations')
    job_titles: dict[str, list[str]] = _fetch_from_yaml(cfg, 'job_titles')
    general: dict[str, list[str]] = _fetch_from_yaml(cfg, 'title_tags')

    payloads_uplift = _payload_clean_up(payloads)
    data_set: pd.DataFrame = _get_info(
        payloads_uplift, locations, job_titles, general)

    data = [
        (row.file_path,
         row.eml_lang,
         *_get_sections(row.payload, sections[row.eml_lang]).values())
        for row in payloads.itertuples(index=False)
    ]

    column_names = \
        ["file_path", "eml_lang"] + list(sections[next(iter(sections))].keys())
    return pd.DataFrame(data, columns=column_names).set_index("file_path")


# These two functions are for splitting the sections based on the spaces
# Not functional yet! but i push them to the main
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


def _payload_clean_up(payloads: pd.DataFrame) -> pd.DataFrame:
    """To split the payload more accurately"""
    payloads_up = payloads.copy()

    # Split on double newlines
    payloads_up["clean_payload"] = _split_double_newline(payloads_up)

    payloads_up["clean_payload"] = \
        payloads_up["clean_payload"].apply(_filter_item)

    return payloads_up


def _split_double_newline(payloads: pd.DataFrame) -> pd.Series:
    """Split the text by breaking on \n\n and remove empty items."""
    return payloads["payload"].apply(
        lambda x: [item for item in re.split(r'\n{2,}', x) if item.strip()]
    )


def _filter_item(item: list[str],
                 max_newlines: int = 2,
                 min_dashes: int = 3
                 ) -> list[str]:
    """
    Cleans the payloads by applying specific filtering criteria:
    - Removes items where the number of newlines is less than
      or equal to the number of '[URL]' occurrences.
    - Excludes items with `max_newlines` or fewer newlines
      and more than `min_dashes` dashes.
    - Retains all other items for further processing.

    Args:
        payloads (pd.DataFrame): DataFrame containing payload
        data.
        max_newlines (int): Maximum number of newlines allowed
        for exclusion.
        min_dashes (int): Minimum number of dashes required
        for exclusion.

    Returns:
        Cleaned payloads.
    """
    filtered: list[str] = []
    for i in item:
        new_line_count: int = i.count('\n')
        url_count: int = i.count('[URL]')
        dash_count: int = i.count('-')
        if new_line_count > url_count and not (
            new_line_count <= max_newlines and dash_count > min_dashes
        ):
            filtered.append(i)
    return filtered


def _get_info(payload: pd.DataFrame,
              locations: dict[str, list[str]],
              job_title: dict[str, list[str]],
              tags: dict[str, list[str]]
              ) -> pd.DataFrame:
    """get the info from the payloads
    columns: list[str] = ['job', 'salary', 'city', 'state']
    """
    cities: list[str] = [
        city for _, item in locations.items() for city in item]
    job_names: list[str] = [
        j_t for _, item in job_title.items() for j_t in item]
    tags: list[str] = tags['tags']

    for _, row in payload.iterrows():
        title_i: str = _extract_title(row, tags)
        city: str = _extract_matching_item(title_i, cities)
        job_name: str = _extract_matching_item(title_i, job_names)


def _extract_title(row: pd.Series,
                   tags: list[str]
                   ) -> str:
    """extract the title of the job"""
    title: str = 'Nan'
    for item in row['clean_payload']:
        if any(tag in item for tag in tags):
            title = next((
                        line for line in item.split('\n')
                        if '(m/w/d)' in line or '(f/m/x)' in line
                        ), "")
            break
    return title


def _extract_matching_item(title: str,
                           items: list[str]
                           ) -> str:
    """
    Checks if the name of the item is mentioned in the title
    as a separate word.
    """
    for item in items:
        # Build a regex that looks for 'item' as a whole word,
        # case-insensitive.
        pattern = rf"\b{re.escape(item)}\b"
        if re.search(pattern, title, re.IGNORECASE):
            return item
    return "nan"


def _get_sections(payload: str,
                  sections: dict[str, str]
                  ) -> dict[str, str]:
    """
    Splits the email payload into sections based on predefined
    section titles, mapping them to standardized keys.

    Args:
        payload (str): The email payload text.
        sections (dict[str, str]): Dictionary mapping
        standardized keys to language-specific section titles.

    Returns:
        dict[str, str]: Dictionary with standardized section
        keys and extracted text.
    """
    section_data: dict[str, str] = {key: "" for key in sections.keys()}
    pattern: str = "|".join([re.escape(title) for title in sections.values()])

    # Split payload into sections using regex
    parts = re.split(f"({pattern})", payload)

    # Iterate over parts and map them to standardized section keys
    current_key = None
    for part in parts:
        part = part.strip()
        if part in sections.values():
            current_key = next(
                key for key, title in sections.items() if title == part)
        elif current_key:
            section_data[current_key] += part + "\n"

    return section_data


def analysis_top_skills(job_skills: pd.DataFrame) -> pd.DataFrame:
    """Get the job top required skills as mentioned directly
    in the emails
    This section usually started with a sentence:
    "Bei diesem Job kannst du mit folgenden Fähigkeiten punkten:"
    """


def analysis_job_title(job_title: pd.DataFrame
                       ) -> dict[str, pd.DataFrame]:
    """Analyze job titles based on language and return results."""

    # Map language codes to their processing functions
    lang_processors = {
        "en": _anlz_job_titles_en,
        "de": _anlz_job_titles_de,
        # Add more languages here if needed
    }

    splited_df = _split_by_lang(job_title)  # Split job titles by language
    results = {}

    for lang, df in splited_df.items():
        if lang in lang_processors:
            results[lang] = lang_processors[lang](df)
        else:
            print(f"Warning: No processor for language '{lang}'")

    return results


def _split_by_lang(df_in: pd.DataFrame
                   ) -> dict[str, pd.DataFrame]:
    """split the dataframes based on the numbers of the langs"""
    return {
        lang: df_in[df_in["eml_lang"] == lang] for
        lang in df_in["eml_lang"].unique()
        }


def _anlz_job_titles_en(job_title_en: pd.DataFrame
                        ) -> pd.DataFrame:
    """analyzing the job titles in English"""


def _anlz_job_titles_de(job_title_de: pd.DataFrame
                        ) -> pd.DataFrame:
    """analyzing the job titles in German"""
