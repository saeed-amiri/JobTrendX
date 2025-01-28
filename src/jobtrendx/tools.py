"""
tools for the main modules
"""

import sys
from pathlib import Path
from . import colors_text as ct


def check_directory(directory: str) -> None | bool:
    "Check if the directory exists"
    if not Path.exists(Path(directory)):
        print(f"{ct.FAIL}Directory `{directory}` does not "
              f"exists, exit!{ct.ENDC}\n")
        sys.exit(1)
    return True


def check_dir_not_empty(directory: str) -> None | bool:
    "Check if the directory is not empty"
    if not any(Path(directory).iterdir()):
        print(f"{ct.FAIL}Directory `{directory}` is empty, exit!{ct.ENDC}\n")
        sys.exit(1)
    return True
