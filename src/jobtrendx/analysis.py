"""Analysis the email contents and order them in tabels"""

import typing
from pathlib import Path

import pandas as pd
import email
from email.message import EmailMessage

from omegaconf import DictConfig

from . import logger
from . import tools


class AnalysisEmails:
    """Analysing the emails"""

    __slots__ = []

    def __init__(self,
                 eml_dict: dict[Path, "email.message.EmailMesagge"],
                 cfg: DictConfig,
                 log: logger.logging.Logger
                 ) -> None:
        self.analysing_object(eml_dict, cfg)

    def analysing_object(self,
                         eml_dict: dict[Path, "email.message.EmailMesagge"],
                         cfg: DictConfig
                         ) -> None:
        """initiate the analysis"""
        attchments: dict[Path, dict[str, typing.Any]] = \
            tools.extract_email_detail(eml_dict)
        eml_df: pd.DataFrame = tools.eml_to_dataframe(attchments)
        eml_df.loc[:, 'eml_lang'] = tools.detect_language(eml_df['body'])
