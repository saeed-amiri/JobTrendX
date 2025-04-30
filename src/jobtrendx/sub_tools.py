"""
Tools used in other tools!
"""

import sys
from pathlib import Path
import yaml
import sys


def fetch_from_yaml(file_path: str,
                    file_type: str
                    ) -> dict[str, list[str]]:
    """
    Reads the YAML file containing location data and returns
    a dictionary of items in the yaml

    Args:
        file_path (str): Path to the directory containing
        the lexicon/taxonomy files.
        file_type (str): Name of the lexicon file.

    Returns:
        dict[str, list[str]]: Dictionary of city names grouped
        by states names.

    Raises:
        SystemExit: If the file is not found, has a format
        error, or an unknown error occurs.
    """
    # pylint: disable=broad-exception-caught
    file_path = Path(file_path) / file_type
    try:
        with file_path.open('r', encoding='utf-8') as f_loc:
            return yaml.safe_load(f_loc)
    except FileNotFoundError:
        sys.exit(f"\nFile Not Found:\n`{file_path}` does not exist!")
    except yaml.YAMLError:
        sys.exit(f"\nFile Format Error:\n`{file_path}` not a valid YAML file!")
    except Exception as err:
        sys.exit(f"Unknown Error in `{file_path}`: {err}")
