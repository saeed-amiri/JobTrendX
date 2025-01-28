"""making logging for all the scripts, the script is started by
chat.openai
example:
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is a error message")
        logger.critical("This is a critical message")
"""

import os
import re
import logging
import datetime
from . import colors_text as ct


def check_log_file(log_name: str) -> str:
    """
    Check if the log file exists and rename the new file.
    """
    log_files: list[str] = [
        file for file in os.listdir('.') if re.match(fr'{log_name}\.\d+', file)
        ]
    if log_files:
        pattern: str = fr'{log_name}\.(\d+)'
        counts: list[int] = [
            int(match.group(1)) for file in log_files if (
                match := re.search(pattern, file))]
        count = max(counts) + 1
    else:
        count = 1

    new_log_file: str = fr'{log_name}.{count}'
    print(f'{ct.OKBLUE}{__name__}: The log file `{new_log_file}` '
          f'is prepared{ct.ENDC}')
    return new_log_file


def write_header(log_file: str) -> None:
    """Write the header of the log file."""
    try:
        with open(log_file, 'w', encoding='utf-8') as f_w:
            current_datetime = \
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f_w.write(f'{current_datetime}\n')
            f_w.write(f'{os.getcwd()}\n\n')
        print(f'\nLogger: {current_datetime}\n')
    except IOError as e:
        print(f"Error writing log file: {e}")


def setup_logger(log_name: str) -> logging.Logger:
    """
    Set up and configure the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(__name__)
    if not logger.hasHandlers():  # Prevent duplicate handlers
        logger.setLevel(logging.DEBUG)
        log_file: str = check_log_file(log_name)
        write_header(log_file)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(levelname)s: [%(module)s in %(filename)s]\n\t- %(message)s\n')
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    return logger
