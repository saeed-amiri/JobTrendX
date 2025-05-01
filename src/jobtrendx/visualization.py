"""
plot and diagrams for the analysis of the job ads
25 Apr. 2025
S.Amiri
"""


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
        self._nested_skills(log)

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
