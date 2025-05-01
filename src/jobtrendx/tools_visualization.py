"""
Plotting tools for visualizaing the data from statistics
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


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
    total: float
    data_name: str

    def __init__(self,
                 threshold: float = 0.03,
                 angle_threshold: float = 10
                 ) -> None:
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
                    data_name: str = 'counts'
                    ) -> None:
        """
        Plot a professional pie chart for counts, grouping
        minor categories into 'Other'.
        """
        self.total = counts.sum()
        self.counts = counts
        self.data_name = data_name

        grouped, minor = self._normalize_others()
        length: int = len(grouped)
        explode = [0.05] * length
        colors = self._set_colors(length=length)

        fig, ax = plt.subplots(figsize=(10, 10))
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
        ax.set_title(f"Distribution of {self.data_name.capitalize()}",
                     fontsize=16,
                     weight='bold')
        self._save_fig(fig)

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
        if not minor.empty:
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

    def _save_fig(self,
                  fig
                  ) -> None:
        """Save figure"""
        plt.tight_layout()
        fout: str = self.data_name.replace(' ', '_')
        fig.savefig(fname=f'{fout}.jpeg')
