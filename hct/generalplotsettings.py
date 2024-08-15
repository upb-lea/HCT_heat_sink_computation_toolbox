"""Plot settings: Normal font or LaTeX font."""
from matplotlib import pyplot as plt

def global_plot_settings_font_latex() -> None:
    """Set the plot fonts to LaTeX-font."""
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Palatino"],
    })


def global_plot_settings_font_sansserif() -> None:
    """Set the plot fonts to Sans-Serif-Font."""
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica"]})
