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

def global_plot_settings_font_size(font_size: float) -> None:
    """
    Change the plot font size.

    :param font_size: font size
    :type font_size: float
    """
    font = {'size': font_size}
    plt.rc('font', **font)


def colors() -> dict:
    """Colors according to the GNOME color scheme (Color 4)."""
    nominator = 255
    color_dict = {
        "blue": tuple(ti / nominator for ti in (28, 113, 216)),
        'red': tuple(ti / nominator for ti in (192, 28, 40)),
        "green": tuple(ti / nominator for ti in (46, 194, 126)),
        "orange": tuple(ti / nominator for ti in (230, 97, 0)),
        "purple": tuple(ti / nominator for ti in (129, 61, 156)),
        "brown": tuple(ti / nominator for ti in (134, 94, 60)),
        "grey": tuple(ti / nominator for ti in (119, 118, 123)),
        "yellow": tuple(ti / nominator for ti in (245, 194, 17)),
        "black": tuple(ti / nominator for ti in (0, 0, 0)),
        "white": tuple(ti / nominator for ti in (255, 255, 255))
    }
    return color_dict
