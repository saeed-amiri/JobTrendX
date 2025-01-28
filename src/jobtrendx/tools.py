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
