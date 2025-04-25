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
        tools.plot_job_titles(self.stats.job_title_top)
