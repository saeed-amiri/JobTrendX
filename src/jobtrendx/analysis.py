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
from . import tools
from . import payload_analysis


class AnalysisEmails:
    """Analysing the emails"""

    __slots__: list[str] = ['cfg', 'eml_dict']

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
        self.analyze_email_payload(eml_df, log)

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
                              ) -> None:
        """call the sub-class to analysis the payload"""
        payload_analyzer = PayloadAnalayzer(eml_df=eml_df, cfg=self.cfg)
        payload_analyzer.analyze_sections(log=log)


class PayloadAnalayzer:
    """analysing the emails' payload
    "payload" sections are:
        job_title
        company_info
        job_description
        requirements
        offer
    are in both 'en' and 'de' languages.
    Each section will be analysis separately.
    """

    __slots__: list[str] = [
        "bodies",
        "cfg",
    ]

    def __init__(self,
                 eml_df: pd.DataFrame,
                 cfg: DictConfig,
                 ) -> None:
        self.bodies = eml_df[['file_path', 'payload', 'eml_lang']]
        self.cfg = cfg

    def analyze_sections(self,
                         log: logger.logging.Logger
                         ) -> pd.DataFrame:
        """spliting the payload and extracting the info from it"""
        log.info("Processing email bodies...")

        df_info: pd.DataFrame = self.split_bodies()
        return df_info

    def split_bodies(self) -> pd.DataFrame:
        """split the payload sections and return them
        returns the output as DataFrame. FilePaths are the index
        """
        return payload_analysis.split_payload(
            self.bodies, self.cfg)

