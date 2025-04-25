"""
Plotting tools for visualizaing the data from statistics
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


def plot_job_titles(job_counts: pd.Series,
                    threshold: float = 0.03
                    ) -> None:
    """
    Plot a professional pie chart for job titles, grouping
    minor categories into 'Other'.

    Parameters:
    -----------
    job_counts : pd.Series
        Series with job titles as index and counts as values.
    threshold : float
        Minimum fraction to display separately. Others will
        be grouped.
    """
    # Normalize and group small slices
    total = job_counts.sum()
    fraction = job_counts / total
    mask = fraction < threshold

    major = job_counts[~mask].copy()
    minor = job_counts[mask]

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

    for i, title in enumerate(grouped.index):
        if title == other_label:
            # Add colored "Other:" label
            handles.append(Patch(facecolor=colors[i], label=title))
            labels.append(title)
            # Add plain text sub-items without color boxes
            for sub in minor.index[:10]:
                handles.append(Patch(facecolor='none', edgecolor='none'))
                labels.append(f"  - {sub}")
        else:
            handles.append(Patch(facecolor=colors[i], label=title))
            labels.append(title)

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
