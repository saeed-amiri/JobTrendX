"""applying statistics on the info from the job ads
21 Apr. 2025
S.Amiri
"""


import pandas as pd

from . import logger
from . import tools_statistics as tools


class StatisticsManager:
    """do the math"""

    __slots__: list[str] = [
        'df_info',
        'job_title_top',
        'skills_count'
    ]

    df_info: pd.DataFrame
    job_title_top: pd.Series
    skills_count: pd.Series

    def __init__(self,
                 df_info: pd.DataFrame,
                 ) -> None:
        self.df_info = df_info

    def statistics(self,
                   log: logger.logging.Logger
                   ) -> None:
        """call the methods and set the objects"""
        self._analyze_job_titles(log)
        self._analyze_skills(log)

    def _analyze_job_titles(self,
                            log: logger.logging.Logger
                            ) -> None:
        """analyzing the job titles"""
        summary: pd.DataFrame
        summary, self.job_title_top = \
            tools.anlz_string_cols(self.df_info['job_title'])

        log.info(f'\n\nJob title summary:\n{summary}'
                 f'\n\n{self.job_title_top}\n')
