"""
Plotting tools for visualizaing the data from statistics
"""

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

    grouped, minor = _normalize_others(counts=counts,
                                       threshold=threshold,
                                       other_label=other_label)

    length: int = len(grouped)
    explode = [0.05] * length
    colors = _set_colors(length=length)

    fig, ax = plt.subplots(figsize=(10, 10))
    wedges, _, autotexts = ax.pie(
        grouped.values,
        labels=None,
        colors=colors,
        explode=explode,
        autopct=lambda pct: f"{pct:.1f}%\n({int(round(pct * total / 100))})",
        pctdistance=0.8,
        startangle=85
    )

    explode = [0.05] * length

    # Legend items
    handles, labels = _handle_legend(grouped=grouped,
                                     minor=minor,
                                     colors=colors,
                                     other_label=other_label)
    ax.legend(
        handles,
        labels,
        title=None,
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        frameon=False
    )

    ax.set_title(f"Distribution of {data_name.capitalize()}",
                 fontsize=16,
                 weight='bold')
    _save_fig(fig=fig, data_name=data_name)


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
            if len(minor.index >= 10):
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
