"""Analysis the email contents and order them in tabels"""

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
        BodyEmailAnalayer(eml_df=eml_df,
                          cfg=cfg,
                          log=log)


class BodyEmailAnalayer:
    """analysing the emails' body"""

    __slots__: list[str] = [
        "bodies",
        "cfg_anlz",
    ]

    def __init__(self,
                 eml_df: pd.DataFrame,
                 cfg: DictConfig,
                 log: logger.logging.Logger
                 ) -> None:
        self.bodies = eml_df[['file_path', 'body', 'eml_lang']]
        self.cfg_anlz = cfg.defaults.analysis
        self.process(log)

    def process(self,
                log: logger.logging.Logger
                ) -> None:
        """spliting the body and extracting the info from it"""
        sections: dict[str, dict[str, str]] = self.split_bodies()

    def split_bodies(self) -> dict[str, dict[str, str]]:
        """split the body sections and return them"""

        return body_analysis.split_body(self.bodies, self.cfg_anlz.sections)
