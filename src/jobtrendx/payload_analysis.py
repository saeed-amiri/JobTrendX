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

import pandas as pd

__all__ = [
    'split_payload',
    'analysis_job_title',
    'analysis_top_skills'
]


def split_payload(payloads: pd.DataFrame,
                  sections: dict[str, dict[str, str]]
                  ) -> pd.DataFrame:

    """splitting the payload of the emails based on the sections
    titles"""
    # Not implemented yet!
    payloads_uplift = _payload_clean_up(payloads)

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
def _payload_clean_up(payloads: pd.DataFrame) -> pd.DataFrame:
    """To split the payload more accurately"""
    payloads_up: pd.DataFrame = payloads.copy()
    payloads_up.loc[:, "split_payload"] = _split_double_n_line(payloads_up)
    return payloads_up


def _split_double_n_line(payloads: pd.DataFrame) -> pd.DataFrame:
    """Split the text by breaking on \n\n and remove empty items."""
    return payloads["payload"].apply(
        lambda x: [item for item in re.split(r'\n{2,}', x) if item.strip()]
    )


def _get_sections_conditions(payload: list[str],
                             sections: dict[str, str]
                             ) -> dict[str, str]:
    """split the sections"""
    for item in payload:
        if '€' in item:
            print(item)
        if '(m/w/d)' in item or '(f/m/x)' in item:
            print(item)


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
