"""Analysis the email contents and order them in tabels

BodyEmailAnalayer:
Analyzing the "body" section of the emails.
Emails contains several sections, depends on the language of
the email, these sections have different titles.
This titles are set in cfg/defaults/analysis.yaml:

sections:
  job_title: ["Beliebter Job", "Top Treffer"]
  company_info: ["Wer wir sind.", "Lloyds Bank GmbH and its brands"]
  job_description: ["Das wird dein Job", "Your tasks"]
  requirements: ["Das bringst du mit", "Your knowledge/experience"]
  offer: ["Das bieten wir dir", "We offer"]

This module first separate the "body" text based on the
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
from . import body_analysis


class AnalysisEmails:
    """Analysing the emails"""

    __slots__: list[str] = []

    def __init__(self,
                 eml_dict: dict[Path, "email.message.EmailMesagge"],
                 cfg: DictConfig,
                 log: logger.logging.Logger
                 ) -> None:
        eml_df: pd.DataFrame = self.process_emails(eml_dict, cfg)
        self.process_body(eml_df, cfg, log)

    def process_emails(self,
                       eml_dict: dict[Path, "email.message.EmailMesagge"],
                       cfg: DictConfig
                       ) -> pd.DataFrame:
        """initiate the analysis"""
        attchments: dict[Path, dict[str, typing.Any]] = \
            tools.extract_email_detail(eml_dict)
        eml_df: pd.DataFrame = tools.eml_to_dataframe(attchments)
        eml_df.loc[:, 'eml_lang'] = tools.detect_language(eml_df['body'])

        return eml_df

    def process_body(self,
                     eml_df: pd.DataFrame,
                     cfg: DictConfig,
                     log: logger.logging.Logger
                     ) -> None:
        """call the sub-class to analysis the body"""
        body_analyzer = BodyEmailAnalayer(eml_df=eml_df, cfg=cfg)
        body_analyzer.process(log=log)


class BodyEmailAnalayer:
    """analysing the emails' body
    "body" sections are:
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
        "cfg_anlz",
    ]

    def __init__(self,
                 eml_df: pd.DataFrame,
                 cfg: DictConfig,
                 ) -> None:
        self.bodies = eml_df[['file_path', 'body', 'eml_lang']]
        self.cfg_anlz = cfg.defaults.analysis

    def process(self,
                log: logger.logging.Logger
                ) -> None:
        """spliting the body and extracting the info from it"""
        log.info("Processing email bodies...")
        sections: pd.DataFrame = self.split_bodies()
        self.anlz_top_skills(sections[['eml_lang', 'top_skills']])
        self.anlz_job_title(sections[['eml_lang', 'job_title']])

    def split_bodies(self) -> pd.DataFrame:
        """split the body sections and return them
        returns the output as DataFrame. FilePaths are the index
        """
        return body_analysis.split_body(self.bodies, self.cfg_anlz.sections)

    def anlz_top_skills(self,
                        top_skills: pd.DataFrame
                        ) -> pd.DataFrame:
        """Analyzing top skills of the jobs"""
        body_analysis.analysis_top_skills(top_skills)

    def anlz_job_title(self,
                       job_title: pd.DataFrame
                       ) -> pd.DataFrame:
        """Analysing the job titles"""
        body_analysis.analysis_job_title(job_title)
