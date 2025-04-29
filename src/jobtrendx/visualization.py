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
    
    def _job_titles(self,
                    log: logger.logging.Logger
                    ) -> None:
        """plot the job titles"""
        try:
            tools.plot_counts_series(self.stats.job_title_top,
                                     threshold=0.03,
                                     data_name='job titles')
        except Exception as err:
            log.info(f'\nNot posssible to plot `Job titles`!\n{err}')


    def _skills(self,
                log: logger.logging.Logger
                ) -> None:
        """plot the job titles"""
        try:
            tools.plot_counts_series(self.stats.skills_count,
                                     threshold=0.015,
                                     data_name='skills')
        except Exception as err:
            log.info(f'\nNot posssible to plot `Skills`!\n{err}')
