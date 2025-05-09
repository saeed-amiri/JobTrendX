"""
plot and diagrams for the analysis of the job ads
25 Apr. 2025
S.Amiri
"""

from collections import defaultdict
import pandas as pd

from . import logger
from . import statistics
from . import tools_visualization as tools


class Visualizer:
    """
    Visualize the statistics
    """
    # pylint: disable=broad-exception-caught
    # pylint: disable=too-few-public-methods

    __slots__ = ['stats']

    stats: statistics.StatisticsManager

    def __init__(self,
                 stats: statistics.StatisticsManager
                 ) -> None:
        self.stats = stats

    def primary_plots(self,
                      log: logger.logging.Logger
                      ) -> None:
        """plot the main plots for the data"""
        self._job_titles(log)
        self._skills(log)
        self._skills_category(log)
        self._skills_detail(log)
        self._skills_job_needed(log)

    def _job_titles(self,
                    log: logger.logging.Logger
                    ) -> None:
        """plot the job titles"""
        try:
            plot = tools.PlotCountsSeries(threshold=0.03,
                                          angle_threshold=10.0)
            plot.plot_series(counts=self.stats.job_title_top,
                             data_name='job titles')
        except Exception as err:
            log.info(f'\nNot posssible to plot `Job titles`!\n{err}')

    def _skills(self,
                log: logger.logging.Logger
                ) -> None:
        """plot the job skills"""
        try:
            plot = tools.PlotCountsSeries(threshold=0.015,
                                          angle_threshold=10.0)
            plot.plot_series(counts=self.stats.skills_count,
                             data_name='skills')
        except Exception as err:
            log.info(f'\nNot posssible to plot `Skills`!\n{err}')

    def _language(self,
                  log: logger.logging.Logger
                  ) -> None:
        """plot the languages"""
        try:
            plot = tools.PlotCountsSeries(threshold=0.1,
                                          angle_threshold=10.0)
            plot.plot_series(counts=self.stats.lang_count,
                             data_name='language')
        except Exception as err:
            log.info(f'\nNot posssible to plot `Language`!\n{err}')

    def _skills_category(self,
                         log: logger.logging.Logger
                         ) -> None:
        """plot the job skills"""
        try:
            plot = tools.PlotCountsSeries(threshold=0.03,
                                          angle_threshold=10.0)

            plot.plot_series(counts=self.stats.skills_category,
                             data_name='skills Category')
        except Exception as err:
            log.info(f'\nNot posssible to plot `Skills Category`!\n{err}')

    def _skills_detail(self,
                       log: logger.logging.Logger
                       ) -> None:
        """plot the details of each skill"""
        try:
            girds_plot = tools.GridPlot(row_nr=4, col_nr=2)
            normalized_data: defaultdict[str, pd.Series] = \
                girds_plot.normalize_data(self.stats.skills_detail, log=log)

            girds_plot.mk_grids(normalized_data)
        except Exception as err:
                log.info(f'\nNot posssible to plot `Skills Detail`!\n{err}')

    def _skills_job_needed(self,
                           log: logger.logging.Logger
                           ) -> None:
        """plot the skills based on the job title"""
        try:
            girds_plot = tools.GridPlot(row_nr=4, col_nr=2)
            normalized_data: defaultdict[str, pd.Series] = \
                girds_plot.normalize_data(self.stats.skills_per_job, log=log)

            girds_plot.mk_grids(normalized_data,
                                threshold=0.035,
                                angle_threshold=15,
                                fout='skill_per_job')
        except Exception as err:
                log.info(f'\nNot posssible to plot `Skills per job`!\n{err}')