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
               sections: dict[str, list[str]]
               ) -> None:
    """splitting the body of the emails based on the sections
    titles"""
