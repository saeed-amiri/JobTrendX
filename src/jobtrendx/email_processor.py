"""
Reading emails frpm .eml files and extracting the body of the email
"""

import sys
from pathlib import Path

import email

from . import tools
from . import logger
from . import colors_text as ct


class EmailProcessor:
    """
    Class to process emails
    """

    def __init__(self,
                 email_dir: str,
                 log: logger.logging.Logger
                 ) -> None:
        self.email_dir = email_dir
        self.read_email()

    def read_email(self) -> str:
        """
        Read the email file and extract the body of the email
        """
        tools.check_directory(self.email_dir)
        tools.check_dir_not_empty(self.email_dir)
        all_files: list[str] = tools.returns_all_files_in_dir(self.email_dir)
        eml_files: list[str] = tools.returns_eml_files(all_files, 'eml')
        eml_paths: list[Path] = tools.returns_eml_path(self.email_dir,
                                                       eml_files)
        emails_dict: dict[Path, "email.message.EmailMessage"] = \
            tools.returns_email_contant(eml_paths=eml_paths)


if __name__ == "__main__":
    EmailProcessor(email_dir=sys.argv[1],
                   log=logger.setup_logger("email_processor.log"))
