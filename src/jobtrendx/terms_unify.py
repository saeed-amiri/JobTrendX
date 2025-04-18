"""
Unify the different terms mentioned in the emails for the
term, also, it could be because of the translation to German
e.g.:
Machine Learning:
  - Machine Learning
  - ML
  - KI
  - KI Forscher
  - Machine Learning Engineer

18 Apr. 2025
S. Amiri
"""

import re
import sys
import typing
from pathlib import Path

import yaml
import pandas as pd

from omegaconf import DictConfig


__all__ = [
    'term_unifier'
]


def term_unifier(df_info: pd.DataFrame,
                 cfg: DictConfig
                 ) -> pd.DataFrame:
    """unify the terms in the columns"""
