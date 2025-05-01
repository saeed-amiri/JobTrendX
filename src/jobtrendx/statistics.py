"""applying statistics on the info from the job ads
21 Apr. 2025
S.Amiri
"""


import pandas as pd

from . import logger
from . import tools_statistics as tools

from omegaconf import DictConfig

class StatisticsManager:
    """do the math"""

    __slots__: list[str] = [
        'df_info',
        'job_title_top',
        'skills_count',
        'skills_category',
        'nested',
        'lang_count',
        'salary_min',
        'salary_max',
        'log'
    ]

    df_info: pd.DataFrame
    job_title_top: pd.Series
    skills_count: pd.Series
    lang_count: pd.Series
    salary_min: pd.Series
    salary_max: pd.Series
    log: logger.logging.Logger

    def __init__(self,
                 df_info: pd.DataFrame,
                 log: logger.logging.Logger
                 ) -> None:
        self.df_info = df_info
        self.log = log

    def statistics(self) -> None:
        """call the methods and set the objects"""
        self._analyze_job_titles()
        self._analyze_skills()
        self._analyze_languages()
        self._analyze_salaries()

    def statistics_by_category(self,
                               cfg: DictConfig
                               ) -> None:
        """Look at the data by the catogory each belong to"""
        summary, self.skills_category = \
            tools.anlz_by_category(self.df_info['skills'], cfg, 'skills')
        self.nested = tools.anlz_for_nested_pie(self.df_info['skills'], cfg, 'skills')

    def _analyze_job_titles(self) -> None:
        """analyzing the job titles"""
        summary: pd.DataFrame
        summary, self.job_title_top = \
            tools.anlz_string_cols(self.df_info['job_title'])

        self.log.info(f'\n\nJob title summary:\n{summary}'
                 f'\n\n{self.job_title_top}\n')

    def _analyze_skills(self) -> None:
        """analysis the skills"""
        summary: pd.DataFrame
        summary, self.skills_count = tools.anlz_list_cols(self.df_info.skills)

        self.log.info(f'\n\nSkills summary:\n{summary}'
                 f'\n\n{self.skills_count.head(8)}\n')

    def _analyze_languages(self) -> None:
        """analysis the skills"""
        summary: pd.DataFrame
        summary, self.lang_count = tools.anlz_list_cols(self.df_info.language)

        self.log.info(f'\n\nLanguages summary:\n{summary}'
                 f'\n\n{self.lang_count.head(8)}\n')

    def _analyze_salaries(self) -> None:
        """analyze salary columns"""
        for col_name in ['salary_min', 'salary_max']:
            summary, attr_value = \
                tools.anlz_numerical_cols(self.df_info[col_name])
            setattr(self, col_name, attr_value)
            self.log.info(f'\n\n{col_name.capitalize()} Summary:\n{summary}')
