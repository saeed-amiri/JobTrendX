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
    __slots__ = ['eml_dir', 'eml_dict']

    eml_dict: dict[Path, "email.message.EmailMessage"]

    def __init__(self,
                 eml_dir: str,
                 log: logger.logging.Logger
                 ) -> None:
        self.eml_dir = eml_dir
        self.eml_dict = {}  # Initialize empty dictionary
        self.read_eml()
        self.log_info(log)

    def read_eml(self) -> None:
        """
        Read the email file and extract the body of the email
        """
        # Validate directory
        tools.check_directory(self.eml_dir)
        tools.check_dir_not_empty(self.eml_dir)

        # Get list of all .eml files
        all_files: list[str] = tools.returns_all_files_in_dir(self.eml_dir)
        eml_files: list[str] = tools.returns_eml_files(all_files, 'eml')
        eml_paths: list[Path] = tools.returns_eml_path(self.eml_dir, eml_files)

        # Get email content
        self.eml_dict = tools.returns_email_contant(eml_paths=eml_paths)

    def log_info(self,
                 log: logger.logging.Logger
                 ) -> None:
        """log the info into log file"""
        log.info(f'Processed {len(self.eml_dict)} emails successfully.')


if __name__ == "__main__":
    EmailProcessor(eml_dir=sys.argv[1],
                   log=logger.setup_logger("email_processor.log"))
