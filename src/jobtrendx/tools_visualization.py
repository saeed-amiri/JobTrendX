"""
Plotting tools for visualizaing the data from statistics
"""

from dataclasses import dataclass
from itertools import cycle
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
    """Plot the normal Pie chart"""
    # pylint: disable=too-few-public-methods

    counts: pd.Series
    total: float
    data_name: str

    def __init__(self,
                 threshold: float = 0.03,
                 angle_threshold: float = 10
                 ) -> None:
        self.threshold = threshold
        self.other_label = "Other:"
        self.angle_threshold = angle_threshold

    def plot_series(self,
                    counts: pd.Series,
                    data_name: str = 'counts'
                    ) -> None:
        """plot the pie"""

        self.total = counts.sum()
        self.counts = counts
        self.data_name = data_name

        grouped, minor = self._normalize_others()
        color_map = self._make_color_map(grouped.index.tolist())
        explode = [0.05] * len(grouped)

        fig, ax = plt.subplots(figsize=(10, 10))
        wedges, _ = self._create_donut_chart_wedges(
            grouped.values, explode, list(color_map.values()), ax)
        xy_wedge, xy_shifted = self._calculate_wedge_centers(wedges)

        wedge_infos = [
            WedgeInfo(wedge=p,
                      xy_wedge=loc_wedge,
                      xy_shifted=loc_shifted,
                      value=val)
            for p, loc_wedge, loc_shifted, val in zip(
                wedges, xy_wedge, xy_shifted, grouped.values)
                      ]

        self._place_wedge_labels(wedge_infos, ax)
        handles, labels = self._build_legend_entries(grouped, minor, color_map)
        self._create_legend(ax, handles, labels)
        ax.set_title(f"Distribution of {self.data_name.capitalize()}",
                     fontsize=16, weight='bold')
        self._save_fig(fig)

    def _make_color_map(self,
                        labels: list[str],
                        style: str = "Set3"
                        ) -> dict[str, str]:
        colors = sns.color_palette(style, n_colors=len(labels)).as_hex()
        return dict(zip(labels, colors))

    def _build_legend_entries(self,
                              grouped: pd.Series,
                              minor: pd.Series,
                              color_map: dict[str, str]
                              ) -> tuple[list, list]:
        handles = []
        labels = []
        for label in grouped.index:
            handles.append(Patch(facecolor=color_map[label], label=label))
            labels.append(label)
            if label == self.other_label:
                for sub in minor.index[:10]:
                    handles.append(Patch(facecolor='none', edgecolor='none'))
                    labels.append(f"  - {sub}")
                if len(minor.index) > 10:
                    handles.append(Patch(facecolor='none', edgecolor='none'))
                    labels.append("  - ...")
        return handles, labels

    def _create_legend(self,
                       ax: mpl.axes._axes.Axes,
                       handles: list,
                       labels: list[str]
                       ) -> None:
        ax.legend(handles,
                  labels,
                  loc="center left",
                  bbox_to_anchor=(1, 0.5),
                  frameon=False)

    def _place_wedge_labels(self,
                            wedge_infos: list[WedgeInfo],
                            ax: mpl.axes._axes.Axes
                            ) -> None:
        for info in wedge_infos:
            arc_length = self._arc_length(info.wedge)
            pct = 100 * info.value / self.total
            ang = self._compute_mid_angle(info.wedge)

            if arc_length > self.angle_threshold:
                self._draw_inner_label(ax, info.xy_wedge, pct, info.value)
            else:
                self._draw_outer_label(
                    ax, info.xy_wedge, ang, pct, info.value)

    def _arc_length(self,
                    wedge: mpl.patches.Wedge
                    ) -> float:
        return wedge.theta2 - wedge.theta1

    def _compute_mid_angle(self,
                           wedge: mpl.patches.Wedge
                           ) -> float:
        return self._arc_length(wedge) / 2. + wedge.theta1

    def _angle_to_coords(self,
                         angle_deg: float
                         ) -> tuple[float, float]:
        return np.cos(np.deg2rad(angle_deg)), np.sin(np.deg2rad(angle_deg))

    def _get_outer_label_pos(self,
                             angle: float,
                             offset: float = 1.3
                             ) -> tuple[float, float]:
        x, y = self._angle_to_coords(angle)
        return 0.75 * np.sign(x), offset * y

    def _draw_inner_label(self,
                          ax: mpl.axes._axes.Axes,
                          xy: tuple[float, float],
                          pct: float,
                          value: float
                          ) -> None:
        x, y = xy
        ax.text(0.9 * x,
                0.9 * y, f"{pct:.1f}%\n({int(value)})",
                ha='center',
                va='center',
                fontsize=10)

    def _draw_outer_label(self,
                          ax: mpl.axes._axes.Axes,
                          xy_wedge: tuple[float, float],
                          ang: float,
                          pct: float,
                          value: float
                          ) -> None:
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-positional-arguments
        x_wedge, y_wedge = xy_wedge
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x_wedge))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        ax.annotate(f"{pct:.1f}%  ({int(value)})",
                    xy=(x_wedge, y_wedge),
                    xytext=self._get_outer_label_pos(ang),
                    horizontalalignment=horizontalalignment,
                    fontsize=9,
                    arrowprops={"arrowstyle": "-",
                                "connectionstyle": connectionstyle})

    def _calculate_wedge_centers(self,
                                 wedges: list[mpl.patches.Wedge]
                                 ) -> tuple[list[tuple[float, float]],
                                            list[tuple[float, float]]]:
        xy_wedge = []
        small_wedges = []
        for i, p in enumerate(wedges):
            ang = self._compute_mid_angle(p)
            x, y = self._angle_to_coords(ang)
            xy_wedge.append((x, y))
            if self._arc_length(p) <= self.angle_threshold:
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
