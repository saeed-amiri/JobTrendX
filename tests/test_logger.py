"""
Testing the logger module
"""
# pylint: disable=redefined-outer-name


from unittest.mock import patch
import pytest


from jobtrendx.logger import setup_logger, check_log_file, write_header

@pytest.fixture
def test_log_file() -> str:
    "To provide a clean log filename for testing"
    return 'test_log'


def test_check_log_file_name_updated():
    "Test if the check_log_file function creates a new log file"
    log_file_name = check_log_file("new_log")
    assert log_file_name == "new_log.1"


def test_check_log_file_name_is_correct(test_log_file) -> None:
    "Test if the check_log_file function creates a new log file"
    log_file = check_log_file(test_log_file)
    assert log_file.startswith(test_log_file)
    assert log_file.endswith(".1")


def test_check_log_file_multiple_existing() -> None:
    "Test if the check_log_file function creates a new log file"
    with patch('os.listdir', return_value=['test_log.1', 'test_log.2']):
        log_file = check_log_file('test_log')
        assert log_file == 'test_log.3'
