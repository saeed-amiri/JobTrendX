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
import typing
from pathlib import Path

import yaml
import pandas as pd

from omegaconf import DictConfig

__all__ = [
    'split_payload',
]


def split_payload(payloads: pd.DataFrame,
                  cfg: DictConfig
                  ) -> pd.DataFrame:

    """splitting the payload of the emails and extract the
    data from it and return a pd DataFrame"""

    skills: dict[str, list[str]] = _fetch_from_yaml(cfg, 'skills')
    tags: dict[str, list[str]] = _fetch_from_yaml(cfg, 'title_tags')
    salaries: dict[str, list[str]] = _fetch_from_yaml(cfg, 'salaries')
    locations: dict[str, list[str]] = _fetch_from_yaml(cfg, 'locations')
    languages: dict[str, list[str]] = _fetch_from_yaml(cfg, 'languages')
    job_titles: dict[str, list[str]] = _fetch_from_yaml(cfg, 'job_titles')

    payloads_uplift = _payload_clean_up(payloads)
    data_set: dict[str, typing.Any] = _get_info(payloads_uplift,
                                                locations,
                                                job_titles,
                                                tags,
                                                skills,
                                                languages,
                                                salaries,
                                                )
    file_path = payloads['file_path']
    eml_lang = payloads['eml_lang']
    # Combine the extracted data into a DataFrame
    df_info = pd.DataFrame({
        'file_path': file_path,
        'eml_lang': eml_lang,
        **data_set
    })
    return df_info


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

    - Remove the extra job ads in the email
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

    # Find the first index where "Diesen Job melden" appears
    cut_index: int = next(
        (i for i, x in enumerate(item) if "Diesen Job melden" in x), len(item))
    item = item[:cut_index]

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
              tag_dict: dict[str, list[str]],
              skill_dict: dict[str, list[str]],
              languages_dict: dict[str, list[str]],
              salaries_dict: dict[str, list[str]],
              ) -> dict[str, typing.Any]:
    """Extract information from the payloads."""
    # pylint: disable="too-many-arguments"
    # pylint: disable="too-many-positional-arguments"
    # pylint: disable="too-many-locals"

    # Flatten dictionaries into lists
    cities = [city for cities in locations.values() for city in cities]
    job_names = [name for names in job_title.values() for name in names]
    tags = tag_dict.get('tags', [])
    all_skills = [
        skill for skills in skill_dict.values() for skill in skills]
    all_languages = [
        lang for langs in languages_dict.values() for lang in langs]
    salaries = [
        salary for salary_list in salaries_dict.values()
        for salary in salary_list]

    # Initialize result lists
    results: dict[str, typing.Any] = {
        'job_title': [],
        'location': [],
        'skills': [],
        'salary_min': [],
        'salary_max': [],
        'salary_unit': [],
        'language': []
    }

    for _, row in payload.iterrows():
        title = _extract_title(row, tags)
        results['job_title'].append(_extract_matching_item(title, job_names))
        results['location'].append(_extract_all_items(row, cities))
        results['skills'].append(_extract_all_items(row, all_skills))
        results['language'].append(_extract_all_items(row, all_languages))
        salary_min, salary_max, salary_unit = _extract_salary(row, salaries)
        results['salary_min'].append(salary_min)
        results['salary_max'].append(salary_max)
        results['salary_unit'].append(salary_unit)

    return results


def _extract_title(row: pd.Series,
                   tags: list[str]
                   ) -> str:
    """Extract the title of the job."""
    title: str = 'Nan'
    for item in row['clean_payload']:
        if any(tag in item for tag in tags):
            title = next((
                        line for line in item.split('\n')
                        if any(tag in line for tag in tags)
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


def _extract_all_items(row: pd.Series,
                       items: list[str],
                       column: str = "clean_payload"
                       ) -> list[str]:
    """
    Extract all matching items from the specified column of
    a row.

    Args:
        row (pd.Series): A row of the DataFrame containing
        the payload data.
        items (list[str]): A list of items to search for in
        the payload.
        column (str): The column name in the row to search
        within.

    Returns:
        list[str]: A list of matched items.
        Returns ["nan"] if no matches are found.
    """
    matched: set[str] = set()
    for item in items:
        # Compile a case-insensitive regex pattern for the item.
        pattern = re.compile(rf"\b{re.escape(item)}\b", re.IGNORECASE)

        # Check if the pattern matches any line in the specified column.
        if any(pattern.search(line) for line in row[column]):
            matched.add(item)

    return list(matched) if matched else ["nan"]


def _extract_salary(row: pd.Series,
                    items: list[str],
                    column: str = "clean_payload"
                    ) -> tuple[float | str, float | str, str]:
    """find the line which contains the item and return it"""
    for item in items:
        # Compile a case-insensitive regex pattern for the item.
        pattern = re.compile(rf"\b{re.escape(item)}\b", re.IGNORECASE)

        # Check if the pattern matches any line in the specified column.
        for line in row[column]:
            if pattern.search(line):
                return _get_salary_amount(line)
    return "Nan", "Nan", "Nan"


def _get_salary_amount(line: str) -> tuple[float | str,
                                           float | str,
                                           str]:
    """return salary amount with unit"""
    min_salary: float = 0.0
    max_salary: float = 0.0
    unit: str = "Nan"
    for l_i in line.split('\n'):
        if "€" in l_i:
            salary_pattern = r"(\d{1,3}\.\d{3})\s*-\s*(\d{1,3}\.\d{3})\s*€/*"
            match = re.search(salary_pattern, l_i)
            if match:
                min_salary = float(match.group(1).replace(".", ""))
                max_salary = float(match.group(2).replace(".", ""))
            if "€/Monat" in l_i:
                min_salary *= 12
                max_salary *= 12
            unit = "€/Jahr"
            return min_salary, max_salary, unit

    return "Nan", "Nan", "Nan"
