"""Analysis the email contents and order them in tabels"""

import typing
from pathlib import Path

import email
from email.message import EmailMessage

from . import logger
from . import tools


class AnalysisEmails:
    """Analysing the emails"""

    __slots__ = []

    def __init__(self,
                 eml_dict: dict[Path, "email.message.EmailMesagge"],
                 log: logger.logging.Logger
                 ) -> None:
        self.analysing_object(eml_dict)

    def analysing_object(self,
                         eml_dict: dict[Path, "email.message.EmailMesagge"],
                         ) -> None:
        """initiate the analysis"""
        attchments: dict[Path, dict[str, typing.Any]] = \
            tools.extract_email_detail(eml_dict)
