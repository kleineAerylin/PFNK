import numpy as np
import matplotlib.pyplot as plt

from collections.abc import Iterable
from typing import Self
from numpy.typing import NDArray



class Plot:
    """
    PlotTask of a Simple Plot
    """
    
    default_params_1: dict = {}
    default_params_2: dict = {"linewidth": 3}
    params: dict = default_params_1.copy()
    
    def __init__(self, label: str, x_data: Iterable[float],
                 y_data: Iterable[float], color: str = None, **kwargs) -> None:
        self.label = label
        self.x_data = x_data
        self.y_data = y_data
        self.color = color
        self.params.update(kwargs)
    

    def plot(self) -> None:
        plt.plot(np.array(self.x_data), np.array(self.y_data),
                 color=self.color, label=self.label, **self.params)
    
    @classmethod
    def set_params(cls, **kwargs) -> None:
        cls.params.update(kwargs)
    
    def has_no_color(self) -> bool:
        return self.color == None
    
    def set_color(self, color: str | None) -> None:
        self.color = color
    
    def do_xy_lims(self) -> None: ...
    
    @classmethod
    def from_array(cls, label: str, data: NDArray, color: str = None) -> Self:
        return cls(label, data[:, 0], data[:, 1], color)
    
    @classmethod
    def from_csv(cls, file_identifier: str, label: str = None, x_row: int = 0, y_row: int = 1, skip_header: int = 1,
                 filetype_identifier: str = "csv", color: str = None, delimiter: str = ",") -> Self:
        if not label:
            label = file_identifier
        file_data = np.genfromtxt("data/" + file_identifier + "." + filetype_identifier,
                                    delimiter=delimiter, skip_header=skip_header)
        x_data = file_data[:, x_row]
        y_data = file_data[:, y_row]
        
        return cls(label, x_data, y_data, color)