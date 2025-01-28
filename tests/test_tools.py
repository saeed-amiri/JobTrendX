"""
Testing the tools module
"""
# pylint: disable=redefined-outer-name


from pathlib import Path
from unittest.mock import patch

import pytest

from jobtrendx.tools import check_directory


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
