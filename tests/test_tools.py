"""
Testing the tools module
"""
# pylint: disable=redefined-outer-name


from pathlib import Path
from unittest.mock import patch

import pytest

from jobtrendx.tools import check_directory, check_dir_not_empty


def test_check_directory_exists() -> None:
    "Test if the check_directory returns True correctly"
    with patch.object(Path, 'exists', return_value=True):
        assert check_directory('test_dir') is True


def test_check_directory_not_exists() -> None:
    "Test if the check_directory exit correctly"
    with patch.object(Path, 'exists', return_value=False):
        with pytest.raises(SystemExit) as exit_info:
            check_directory('test_dir')
        assert exit_info.type == SystemExit
        assert exit_info.value.code == 1


def test_check_dir_not_empty_contains() -> None:
    """Test if the check_dir_not_empty knows dir is not empty"""
    with patch.object(Path, 'iterdir', return_value=[1, 2, 3]):
        assert check_dir_not_empty('test_dir')


def test_check_dir_not_empty_not_contains() -> None:
    """Test if the check_dir_not_empty knows dir is empty"""
    with patch.object(Path, 'iterdir', return_value=[]):
        with pytest.raises(SystemExit) as exit_info:
            check_dir_not_empty('test_dir')
        assert exit_info.type == SystemExit
        assert exit_info.value.code == 1
