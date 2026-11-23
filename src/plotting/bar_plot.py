import numpy as np
import matplotlib.pyplot as plt

from typing import Self
from numpy.typing import NDArray

from src.fitting import HistFittingContainer


class BarPlot:
    """
    PlotTask of a Bar Plot
    """
    
    def __init__(self, label: str, x_data: NDArray, height_data: NDArray,
                 width: float = 1, face_color: str = None, edge_color: str = None,
                 force_lims: bool = True) -> None:
        self.label = label
        self.x_data = x_data
        self.height_data = height_data
        self.width = width
        self.face_color = face_color
        self.edge_color = edge_color
        self.force_lims = force_lims


    def plot(self) -> None:
        edge_color = self.face_color if self.edge_color == None else self.edge_color
        plt.bar(self.x_data, self.height_data, self.width, facecolor=self.face_color, edgecolor=edge_color,
                label=self.label, align='edge')
    
    def has_no_color(self) -> bool:
        return self.face_color == None and self.edge_color == None
    
    def set_color(self, color: str | None) -> None:
        self.face_color = color
    
    def do_xy_lims(self) -> None:
        if self.force_lims:
            plt.ylim(0, max(self.height_data) * 1.2)
            plt.xlim(min(self.x_data), max(self.x_data))
    
    def change_width(self, width: float) -> Self:
        self.width = width
        return self
    
    def to_HistFittingContainer(self, axislabels: tuple[str|None, str|None] = (None, None), bin_edges: NDArray|None = None) -> HistFittingContainer:
        steps = np.diff(self.x_data)
        if bin_edges is None:
            if not np.allclose(steps, step := steps[0]):
                raise ValueError("bin sizes aren't uniform. Cant predict bin edges")
            bin_edges = np.arange(self.x_data[0]-0.5*step, self.x_data[-1]+step, step = step)
        if bin_edges is None:
            raise ValueError("Guessing bin edges failed")
        return HistFittingContainer.from_arrays(bin_edges, self.height_data, self.label, axislabels)


    @classmethod
    def from_HistFittingContainer(cls, container: HistFittingContainer, width: float = 1) -> Self:
        label = "histogramm data" if container.label == None else container.label
        return cls(label, container.bin_mids, container.heights, width=width)