"""
Reading emails frpm .eml files and extracting the body of the email
"""

import sys
from pathlib import Path

import email

from . import tools
from . import logger


class EmailProcessor:
    """
    Class to process emails
    """
    __slots__ = ['email_dir', 'emails_dict']

    emails_dict: dict[Path, "email.message.EmailMessage"]

    def __init__(self,
                 email_dir: str,
                 log: logger.logging.Logger
                 ) -> None:
        self.email_dir = email_dir
        self.read_email()
        self.log_info(log)

    def read_email(self) -> None:
        """
        Read the email file and extract the body of the email
        """
        tools.check_directory(self.email_dir)
        tools.check_dir_not_empty(self.email_dir)
        all_files: list[str] = tools.returns_all_files_in_dir(self.email_dir)
        eml_files: list[str] = tools.returns_eml_files(all_files, 'eml')
        eml_paths: list[Path] = tools.returns_eml_path(self.email_dir,
                                                       eml_files)
        self.emails_dict = tools.returns_email_contant(eml_paths=eml_paths)

    def log_info(self,
                 log: logger.logging.Logger
                 ) -> None:
        """log the info into log file"""
        log.info(f'The numeber of emails are: `{len(self.emails_dict)}`')


if __name__ == "__main__":
    EmailProcessor(email_dir=sys.argv[1],
                   log=logger.setup_logger("email_processor.log"))
