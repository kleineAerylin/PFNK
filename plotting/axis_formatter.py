import matplotlib.pyplot as plt

from typing import Literal
from matplotlib.ticker import Formatter, Locator
from matplotlib.axes import Axes


axies_selector = Literal["", "x", "y"]


class AxisFormatter:
    """
    Base Class for a formatter that changes how the Axis
    of a plt plot are labeled
    """
    
    def __init__(self, formatter: Formatter, locator: Locator, applying_axes: axies_selector) -> None:
        self.formatter = formatter
        self. locator = locator
        self.applying_axes = applying_axes
    
    def format_axes(self) -> None:
        ax = plt.gca()
        self.apply_locator(ax)
        self.apply_formatter(ax)

    def apply_formatter(self, ax: Axes) -> None:
        if "x" == self.applying_axes:
            ax.xaxis.set_major_formatter(self.formatter)
        if "y" == self.applying_axes:
            ax.yaxis.set_major_formatter(self.formatter)
    
    def apply_locator(self, ax: Axes) -> None:
        if "x" == self.applying_axes:
            ax.xaxis.set_major_locator(self.locator)
        if "y" == self.applying_axes:
            ax.yaxis.set_major_locator(self.locator)