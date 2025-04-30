"""Analysis the email contents and order them in tabels

PayloadAnalayzer:
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

import typing
from pathlib import Path
import email

import pandas as pd

from omegaconf import DictConfig

from . import logger
from . import tools_analysis as tools
from . import payload_analysis
from . import terms_unify


class AnalysisEmails:
    """Analysing the emails"""

    __slots__: list[str] = ['cfg', 'eml_dict', 'df_info']

    eml_dict: dict[Path, "email.message.EmailMesagge"]
    cfg: DictConfig
    df_info: pd.DataFrame

    def __init__(self,
                 eml_dict: dict[Path, "email.message.EmailMesagge"],
                 cfg: DictConfig,
                 ) -> None:
        self.cfg = cfg
        self.eml_dict = eml_dict

    def analyzing(self,
                  log: logger.logging.Logger
                  ) -> None:
        """Initiate analyzing"""
        eml_df: pd.DataFrame = self.extract_email_data()
        self.df_info = self.analyze_email_payload(eml_df, log)

    def extract_email_data(self) -> pd.DataFrame:
        """initiate the analysis"""
        attchments: dict[Path, dict[str, typing.Any]] = \
            tools.extract_email_detail(self.eml_dict)
        eml_df: pd.DataFrame = tools.eml_to_dataframe(attchments)
        eml_df.loc[:, 'eml_lang'] = tools.detect_language(eml_df['payload'])

        return eml_df

    def analyze_email_payload(self,
                              eml_df: pd.DataFrame,
                              log: logger.logging.Logger
                              ) -> pd.DataFrame:
        """call the sub-class to analysis the payload"""
        bodies = eml_df[['file_path', 'payload', 'eml_lang']]
        df_info: pd.DataFrame = \
            payload_analysis.split_payload(bodies, self.cfg)
        log.info('\nThe DataFrame from the emails extrcted, with column:\n'
                 f'\t{df_info.columns.to_list()}\n')

        return df_info

    def unify_terms(self,
                    log: logger.logging.Logger
                    ) -> pd.DataFrame:
        """unfiy the terms in the titles and skills
        The terms could be in english or many different
        German translation of them, for example:
        Data Scientist could be named as:
            - Data Scientist
            - Datascientist
            - Datenwissenschaftler
            - Wissenschaftler Daten
        """
        log.info('\nThe DataFrame columns terms are unified\n')

        return terms_unify.term_unifier(self.df_info, self.cfg)
