"""
Plotting tools for visualizaing the data from statistics
"""

from collections import defaultdict
from dataclasses import dataclass

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.gridspec as gridspec

from . import logger


@dataclass
class WedgeInfo:
    """The info about the wedges"""
    wedge: mpl.patches.Wedge
    xy_wedge: tuple[float, float]
    xy_shifted: tuple[float, float]
    value: float  # grouped.values[i]


class PlotCountsSeries:
    """
    Plot Pie chart for the data in a pd.Series
    """
    # pylint: disable=too-few-public-methods
    counts: pd.Series
    data_name: str
    total: float

    def __init__(self,
                 threshold: float = 0.03,
                 angle_threshold: float = 10.0,
                 ):
        """
        Initialize the PlotCountsSeries class.

        Parameters:
        -----------
        counts : pd.Series
            Series with job titles as index and counts as values.
        threshold : float
            Minimum fraction to display separately. Others will be grouped.
        data_name : str
            Name of the data being visualized.
        """
        self.threshold = threshold
        self.other_label = "Other:"
        self.angle_threshold = angle_threshold

    def plot_series(self,
                    counts: pd.Series,
                    data_name: str = 'counts',
                    ax_return: bool = False,
                    ax: mpl.axes._axes.Axes | None = None
                    ) -> None | tuple[mpl.figure.Figure, mpl.axes._axes.Axes]:
        """
        Plot a professional pie chart for counts, grouping
        minor categories into 'Other'.
        """
        # pylint: disable=too-many-locals

        self.counts = counts
        self.data_name = data_name
        self.total = counts.sum()
        grouped, minor = self._normalize_others()

        length: int = len(grouped)
        explode = [0.05] * length
        colors = self._set_colors(length=length)

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))
        else:
            fig = ax.figure

        wedges = self._create_donut_chart_wedges(grouped, explode, colors, ax)
        xy_wedge, xy_shifted = self._calculate_wedge_centers(wedges)

        wedge_infos = [WedgeInfo(wedge=p,
                                 xy_wedge=loc_wedge,
                                 xy_shifted=loc_shifted,
                                 value=val)
                       for p, loc_wedge, loc_shifted, val in zip(wedges,
                                                                 xy_wedge,
                                                                 xy_shifted,
                                                                 grouped.values
                                                                 )]
        self._place_wedge_labels(wedge_infos, ax)

        handles, labels = self._handle_legend(grouped, minor, colors)

        self._create_legend(ax, handles, labels)
        ax.set_title(self.data_name.capitalize(),
                     loc='left',
                     fontsize=16,
                     weight='bold')
        if ax_return:
            return fig, ax
        fout: str = self.data_name.replace(' ', '_')
        save_fig(fig, fout)
        return None

    def _create_legend(self,
                       ax: mpl.axes._axes.Axes,
                       handles: list,
                       labels: list[str]
                       ) -> None:
        """Set the legend"""
        ax.legend(
            handles,
            labels,
            title=None,
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            frameon=False
        )

    def _place_wedge_labels(self,
                            wedge_infos: list[WedgeInfo],
                            ax: mpl.axes._axes.Axes
                            ) -> None:
        """
        Place labels for each wedge based on their arc length
        and position."""
        for info in wedge_infos:
            ang = self._compute_mid_angle(info.wedge)
            arc_length = info.wedge.theta2 - info.wedge.theta1
            pct = 100 * info.value / self.total

            if arc_length > self.angle_threshold:
                self._draw_inner_label(ax, info.xy_wedge, pct, info.value)
            else:
                self._draw_outer_label(
                    ax, info.xy_wedge, info.xy_shifted, ang, pct, info.value)

    def _compute_mid_angle(self, wedge: mpl.patches.Wedge) -> float:
        """Compute the mid angle of the wedge."""
        return (wedge.theta2 - wedge.theta1) / 2. + wedge.theta1

    def _draw_inner_label(self, ax: mpl.axes._axes.Axes,
                          xy: tuple[float, float],
                          pct: float,
                          value: float
                          ) -> None:
        """Draw label inside the wedge."""
        x, y = xy
        ax.text(0.9 * x, 0.9 * y,
                f"{pct:.1f}%\n({int(value)})",
                ha='center', va='center', fontsize=10, weight='normal')

    def _draw_outer_label(self,
                          ax: mpl.axes._axes.Axes,
                          xy_wedge: tuple[float, float],
                          xy_shifted: tuple[float, float],
                          ang: float,
                          pct: float,
                          value: float
                          ) -> None:
        """Draw label outside the wedge with an arrow."""
        # pylint: disable=too-many-positional-arguments
        # pylint: disable=too-many-arguments
        x_wedge, y_wedge = xy_wedge
        x_shifted, y_shifted = xy_shifted
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x_wedge))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"

        ax.annotate(f"{pct:.1f}%  ({int(value)})",
                    xy=(x_wedge, y_wedge),
                    xytext=(0.75 * np.sign(x_shifted), 1.3 * y_shifted),
                    horizontalalignment=horizontalalignment,
                    fontsize=9,
                    arrowprops={"arrowstyle": "-",
                                "connectionstyle": connectionstyle})

    def _calculate_wedge_centers(self,
                                 wedges: list[mpl.patches.Wedge]
                                 ) -> tuple[list[tuple[float, float]],
                                            list[tuple[float, float]]]:
        """Find the centers of the wedges"""
        xy_wedge: list[tuple[float, float]] = []
        small_wedges: list[int] = []

        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1) / 2. + p.theta1
            arc_length = p.theta2 - p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            xy_wedge.append((x, y))

            if arc_length <= self.angle_threshold:
                small_wedges.append(i)

        xy_shifted = xy_wedge.copy()
        if small_wedges:
            small_wedges.sort(key=lambda i: xy_wedge[i][1], reverse=True)
            for shift_idx, wedge_idx in enumerate(small_wedges):
                x, y = xy_wedge[wedge_idx]
                xy_shifted[wedge_idx] = (x * 0.9, y - shift_idx * 0.05)
        return xy_wedge, xy_shifted

    def _create_donut_chart_wedges(self,
                                   grouped: pd.Series,
                                   explode: list[float],
                                   colors: list[str],
                                   ax
                                   ) -> list:
        """Create the wedges"""
        wedges, _ = ax.pie(
            grouped.values,
            labels=None,
            colors=colors,
            explode=explode,
            startangle=87,
            labeldistance=1.1,
            wedgeprops={"width": 0.5}
        )
        return wedges

    def _normalize_others(self) -> tuple[pd.Series, pd.Series]:
        """Normalize and group the small slices"""
        fraction = self.counts / self.total
        mask = fraction < self.threshold

        major = self.counts[~mask].copy()
        minor = self.counts[mask]

        grouped = major.copy()
        if len(minor) >= 2:
            grouped[self.other_label] = minor.sum()
        return grouped, minor

    def _set_colors(self,
                    length: int,
                    style: str = "Set3"
                    ) -> list:
        """Set the color of the pie"""
        return sns.color_palette(style, n_colors=length).as_hex()

    def _handle_legend(self,
                       grouped: pd.Series,
                       minor: pd.Series,
                       colors: list[str]
                       ) -> tuple[list, list]:
        handles: list = []
        labels: list = []
        for i, item in enumerate(grouped.index):
            if item == self.other_label:
                handles.append(Patch(facecolor=colors[i], label=item))
                labels.append(item)
                for sub in minor.index[:10]:
                    handles.append(Patch(facecolor='none', edgecolor='none'))
                    labels.append(f"  - {sub}")
                if len(minor.index) >= 10:
                    handles.append(Patch(facecolor='none', edgecolor='none'))
                    labels.append(f"  - {'...'}")
            else:
                handles.append(Patch(facecolor=colors[i], label=item))
                labels.append(item)
        return handles, labels


def save_fig(fig: mpl.figure.Figure,
             fname: str
             ) -> None:
    """Save figure"""
    plt.tight_layout()
    fig.savefig(fname=f'{fname}.jpeg')


class GridPlot:
    """Plot skills in grids"""
    row_nr: int
    col_nr: int

    def __init__(self,
                 row_nr: int = 3,
                 col_nr: int = 2
                 ) -> None:
        self.row_nr = row_nr
        self.col_nr = col_nr

    def normalize_data(self,
                       data: defaultdict[str, pd.Series],
                       log: logger.logging.Logger
                       ) -> defaultdict[str, pd.Series]:
        """
        Normalize the data based on the number of the
        requested grid size.
        Total grid is nr_grid = row_nr × col_nr.
        If the number of the keys in the skills is more than
        nr_grid, the first nr_grid - 1 keys with the most
        number of entries are kept, and the rest are combined
        into one key named 'Other'.

        Steps:
        1. Check if the number of grids is less than the
        number of keys.
        If so:
              2. Order the data.
              3. Keep the first nr_grid - 1 keys.
              4. Combine the rest into one key as 'Other'.
              5. Return the updated data.
        Else:
           1. Update the nr_col and nr_row to the closest
              values to match the length of the data.
           2. Return the input data without any change.
        """
        nr_grid = self.row_nr * self.col_nr

        if len(data) > nr_grid:
            major_data = self._get_major_data(data, nr_grid)
            return major_data

        else:
            # Adjust row_nr and col_nr to fit the data
            total_items = len(data)
            self.row_nr = int(np.ceil(total_items / self.col_nr))
            return data

    def mk_grids(self,
                 data: defaultdict[str, pd.Series]
                ) -> None:
        """make the grids and plots"""
        plt.close('all')
        fig = plt.figure(figsize=(20, 20))
        gs = gridspec.GridSpec(self.row_nr, self.col_nr, figure=fig)
        data_items = list(data.items())
        for idx, (key, series) in enumerate(data_items[:-1]):
            row, col = divmod(idx, self.col_nr)
            if row >= self.row_nr:
                break
            ax = fig.add_subplot(gs[row, col])
            plotter = PlotCountsSeries(threshold=0.02, angle_threshold=15)
            plotter.plot_series(series, data_name=key, ax=ax, ax_return=True)
        save_fig(fig, fname='detail')

    @staticmethod
    def _get_major_data(data: defaultdict[str, pd.Series],
                        nr_grid: int
                        ) -> defaultdict[str, pd.Series]:
        """get the data based on the nr of grids"""
        # Order the data by the size of the Series
        sorted_data = sorted(
                data.items(), key=lambda x: x[1].sum(), reverse=True)
        # Keep the first nr_grid - 1 keys
        major_data = defaultdict(pd.Series, dict(sorted_data[:nr_grid - 1]))
        # Combine the rest into 'Other'
        other_series = pd.concat(
            [item[1] for item in sorted_data[nr_grid - 1:]])
        major_data['Other'] = other_series.groupby(other_series.index).sum()
        return major_data
