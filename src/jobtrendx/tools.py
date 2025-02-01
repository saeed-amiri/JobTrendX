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


def returns_all_files_in_dir(directory: str) -> list[str]:
    """Return all files in the directory"""
    return [
        file.name
        for file in Path(directory).iterdir()
        if file.is_file()
        ]


def returns_eml_files(eml_name_list: list[str],
                      extension: str = 'eml'
                      ) -> list[str]:
    """Filter and return the file names that match the
    specified extension."""
    # Ensure the extension has a leading dot and convert it to lower case.
    ext = f".{extension.lstrip('.')}".lower()

    # Filter files using pathlib to check file extension.
    return [
        file
        for file in eml_name_list
        if Path(file).suffix.lower() == ext
        ]
