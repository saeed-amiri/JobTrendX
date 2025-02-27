"""
Analyzing the "body" section of the emails.
Emails contains several sections, depends on the language of
the email, this sections have different titles.
This titles are set in cfg/defaults/analysis.yaml:

sections:
  job_title: ["Beliebter Job", "Top Treffer"]
  company_info: ["Wer wir sind.", "Lloyds Bank GmbH and its brands"]
  job_description: ["Das wird dein Job", "Your tasks"]
  requirements: ["Das bringst du mit", "Your knowledge/experience"]
  offer: ["Das bieten wir dir", "We offer"]

This module here, first must separate the "body" text, based
on the sections and than grep the information of each sections
and return them.

26 Feb. 2025
Samiri
"""

import re

import pandas as pd

__all__ = [
    'split_body'
]


def split_body(bodies: pd.DataFrame,
               sections: dict[str, dict[str, str]]
               ) -> None:
    """splitting the body of the emails based on the sections
    titles"""
    for _, row in bodies.iterrows():
        lang: str = row['eml_lang']
        body: str = row['body']
        print(_get_sections(body, sections[lang]))

def _get_sections(body: str,
                  sections: dict[str, str]
                  ) -> dict[str, str]:
    """
    Splits the email body into sections based on predefined
    section titles, mapping them to standardized keys.

    Args:
        body (str): The email body text.
        sections (dict[str, str]): Dictionary mapping
        standardized keys to language-specific section titles.

    Returns:
        dict[str, str]: Dictionary with standardized section
        keys and extracted text.
    """
    section_data: dict[str, str] = {key: "" for key in sections.keys()}
    pattern: str = "|".join([re.escape(title) for title in sections.values()])

    # Split body into sections using regex
    parts = re.split(f"({pattern})", body)

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
