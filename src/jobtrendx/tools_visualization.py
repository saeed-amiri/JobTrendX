"""
Plotting tools for visualizaing the data from statistics
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


def plot_counts_series(counts: pd.Series,
                       threshold: float = 0.03,
                       data_name: str = 'counts'
                       ) -> None:
    """
    Plot a professional pie chart for counts, grouping
    minor categories into 'Other'.

    Parameters:
    -----------
    counts : pd.Series
        Series with job titles as index and counts as values.
    threshold : float
        Minimum fraction to display separately. Others will
        be grouped.
    """
    # Normalize and group small slices
    other_label = "Other:"
    total = counts.sum()
    angle_threshold: float = 10.0

    grouped, minor = _normalize_others(counts=counts,
                                       threshold=threshold,
                                       other_label=other_label)

    length: int = len(grouped)
    explode = [0.05] * length

    colors = _set_colors(length=length)

    fig, ax = plt.subplots(figsize=(10, 10))
    wedges = _create_donut_chart_wedges(grouped, explode, colors, ax)

    xy_wedge, xy_shifted = _calculate_wedge_centers(wedges, angle_threshold)

    _place_wedge_labels(total,
                        grouped,
                        ax,
                        wedges,
                        angle_threshold,
                        xy_wedge,
                        xy_shifted)

    handles, labels = _handle_legend(grouped=grouped,
                                     minor=minor,
                                     colors=colors,
                                     other_label=other_label)

    _create_legend(ax, handles, labels)

    ax.set_title(f"Distribution of {data_name.capitalize()}",
                 fontsize=16,
                 weight='bold')
    _save_fig(fig=fig, data_name=data_name)


def _create_legend(ax,
                   handles,
                   labels
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


def _place_wedge_labels(total,
                        grouped,
                        ax,
                        wedges,
                        angle_threshold,
                        xy_wedge,
                        xy_shifted) -> None:
    """Add the legend to the wedges"""
    for i, (p, loc_wedge, loc_shifted) in enumerate(zip(wedges,
                                                        xy_wedge,
                                                        xy_shifted)):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        arc_length = p.theta2 - p.theta1
        pct = 100 * grouped.values[i] / total
        x_wedge, y_wedge = loc_wedge
        x_shifted, y_shifted = loc_shifted

        if arc_length > angle_threshold:
            # Big slice → label inside
            ax.text(0.9 * x_wedge, 0.9 * y_wedge,
                    f"{pct:.1f}%\n({int(grouped.values[i])})",
                    ha='center', va='center', fontsize=10, weight='normal')
        else:
            # Small slice → label outside + arrow
            horizontalalignment = {
                -1: "right", 1: "left"}[int(np.sign(x_wedge))]
            connectionstyle = f"angle,angleA=0,angleB={ang}"

            ax.annotate(f"{pct:.1f}%  ({int(grouped.values[i])})",
                        xy=(x_wedge, y_wedge),
                        xytext=(1.3*np.sign(x_shifted), 1.3*y_shifted),
                        horizontalalignment=horizontalalignment,
                        fontsize=9,
                        arrowprops={"arrowstyle":"-",
                                    "connectionstyle":connectionstyle})


def _calculate_wedge_centers(wedges,
                             angle_threshold
                             ) -> tuple[list[tuple[float, float]],
                                        list[tuple[float, float]]]:
    """find the centers of the wedges"""
    xy_wedge: list[tuple[float, float]] = []
    small_wedges: list[int] = []

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1

        arc_length = p.theta2 - p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        xy_wedge.append((x, y))

        if arc_length <= angle_threshold:
            small_wedges.append(i)

    # Adjust small wedge label positions
    xy_shifted = xy_wedge.copy()
    if small_wedges:
        small_wedges.sort(key=lambda i: xy_wedge[i][1], reverse=True)
        for shift_idx, wedge_idx in enumerate(small_wedges):
            x, y = xy_wedge[wedge_idx]
            xy_shifted[wedge_idx] = (x * 0.9, y - shift_idx * 0.05)
    return xy_wedge, xy_shifted


def _create_donut_chart_wedges(grouped,
                               explode,
                               colors,
                               ax
                               ) -> list:
    """Create the wedgs"""
    wedges, _ = ax.pie(
        grouped.values,
        labels=None,
        colors=colors,
        explode=explode,
        startangle=60,
        labeldistance=1.1,  # push labels outward
        wedgeprops={"width":0.5}  # make it a donut
        )

    return wedges


def _normalize_others(counts: pd.Series,
                      threshold: float,
                      other_label: str
                      ) -> tuple[pd.Series, pd.Series]:
    """Nomarilze and group the small slices"""
    total = counts.sum()
    fraction = counts / total
    mask = fraction < threshold

    major = counts[~mask].copy()
    minor = counts[mask]

    grouped = major.copy()
    if not minor.empty:
        grouped[other_label] = minor.sum()
    return grouped, minor


def _set_colors(length: int,
                style: str = "Set3"
                ) -> list:
    """set the color of the pie"""
    return sns.color_palette(style, n_colors=length).as_hex()


def _handle_legend(grouped: pd.Series,
                   minor: pd.Series,
                   colors: list[str],
                   other_label: str
                   ) -> tuple[list, list]:
    handles: list = []
    labels: list = []
    for i, item in enumerate(grouped.index):
        if item == other_label:
            # Add colored "Other:" label
            handles.append(Patch(facecolor=colors[i], label=item))
            labels.append(item)
            # Add plain text sub-items without color boxes
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


def _save_fig(fig,
              data_name: str
              ) -> None:
    """save figure"""
    plt.tight_layout()
    fout: str = data_name.replace(' ', '_')
    fig.savefig(fname=f'{fout}.jpeg')
