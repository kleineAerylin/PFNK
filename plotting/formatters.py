import numpy as np

from typing import Literal
from matplotlib.ticker import FuncFormatter, LogLocator

from tools.plotting.axis_formatter import AxisFormatter


axies_selector = Literal["", "x", "y"]


class LogFormatter(AxisFormatter):
    """
    Formatter that sets the axis to show powers of a value
    """
    
    def __init__(self, base: int|float, base_string_repr: str = None,
                 applying_axes: axies_selector = "x") -> None:
        
        super().__init__(FuncFormatter(self.format_power), LogLocator(base), applying_axes)
        self.base = base
        self.base_string_repr = base_string_repr if base_string_repr else str(base)
    
    def format_power(self, x: float, p) -> str:
        if x == 0:
            return '0'
        power = np.log(x) / np.log(self.base)
        
        if np.isclose(power, round(power)):
            power = round(power)
        return f"${self.base_string_repr}^{{{power}}}$"