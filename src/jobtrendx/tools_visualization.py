"""
Plotting tools for visualizaing the data from statistics
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


def plot_counts_series(counts: pd.Series,
                       threshold: float = 0.03
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
    total = counts.sum()
    fraction = counts / total
    mask = fraction < threshold

    major = counts[~mask].copy()
    minor = counts[mask]

    other_label = "Other:"
    grouped = major.copy()
    if not minor.empty:
        grouped[other_label] = minor.sum()

    # Colors
    n = len(grouped)
    colors = sns.color_palette("Set3", n_colors=n).as_hex()
    explode = [0.05] * n

    fig, ax = plt.subplots(figsize=(10, 10))
    wedges, _, autotexts = ax.pie(
        grouped.values,
        labels=None,
        colors=colors,
        explode=explode,
        autopct=lambda pct: f"{pct:.1f}%\n({int(round(pct * total / 100))})",
        pctdistance=0.8,
        startangle=140
    )

    # Legend items
    handles = []
    labels = []

    for i, item in enumerate(grouped.index):
        if item == other_label:
            # Add colored "Other:" label
            handles.append(Patch(facecolor=colors[i], label=item))
            labels.append(item)
            # Add plain text sub-items without color boxes
            for sub in minor.index[:10]:
                handles.append(Patch(facecolor='none', edgecolor='none'))
                labels.append(f"  - {sub}")
        else:
            handles.append(Patch(facecolor=colors[i], label=item))
            labels.append(item)

    ax.legend(
        handles,
        labels,
        title="Job Titles",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        frameon=False
    )

    ax.set_title("Distribution of Job Titles", fontsize=16, weight='bold')
    plt.tight_layout()
    fig.savefig(fname='job_title.jpeg')
    plt.show()
