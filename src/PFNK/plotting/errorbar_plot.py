import numpy as np
import matplotlib.pyplot as plt

from collections.abc import Iterable
from typing import overload, Self
from numpy import nan
from numpy.typing import NDArray
from uncertainties import UFloat, ufloat as uf
from kafe2 import XYContainer

from ..fitting.xy_fitting_container import XYFittingContainer


class ErrorbarPlot:
    """
    PlotTask of an Errorbar Plot
    """
    
    _uf = np.vectorize(lambda v, e: uf(v, e), otypes=[object])
    
    def __init__(self, label: str, x_data: Iterable[UFloat],
                 y_data: Iterable[UFloat], color: str = None) -> None:
        self.label = label
        self.x_data = x_data
        self.y_data = y_data
        self.color = color
        self.ecolor: str|None = None
    
    """
    todo: implement a __repr__ that returns an empty string but uses
    todo: IPython.display Latex and display to print itselve as formatted Latex
    """


    def plot(self) -> None:
        ecolor = self.ecolor if self.ecolor else self.color
        plt.errorbar([x.n for x in self.x_data], [y.n for y in self.y_data], ecolor=ecolor,
                     xerr=[x.s for x in self.x_data], yerr=[y.s for y in self.y_data],
                     fmt='o', color=self.color, label=self.label, capsize=3, markersize=3)
    
    def has_no_color(self) -> bool:
        return self.color == None
    
    def set_color(self, color: str | None) -> None:
        self.color = color
    
    def do_xy_lims(self) -> None: ...
    
    def set_ecolor(self, ecolor) -> Self:
        self.ecolor = ecolor
        return self
    
    def to_XYContainer(self, axis_labels: tuple[str|None, str|None] = (None, None)) -> XYContainer:
        container = XYContainer([x.n for x in self.x_data], [y.n for y in self.y_data])
        container.add_error(0, [x.s for x in self.x_data])
        container.add_error(1, [y.s for y in self.y_data])
        container.axis_labels = axis_labels
        container.label = self.label
        return container
    
    def to_XYFittingContainer(self, axis_labels: tuple[str|None, str|None] = (None, None)) -> XYFittingContainer:
        return XYFittingContainer(self.to_XYContainer(axis_labels))


    @overload
    @classmethod
    def from_array(cls, label: str, data: NDArray, *, color: str = None) -> Self: ...
    @overload
    @classmethod
    def from_array(cls, label: str, data: NDArray, xerr: float|NDArray, *, color: str = None) -> Self: ...
    @overload
    @classmethod
    def from_array(cls, label: str, data: NDArray, *, yerr: float|NDArray, color: str = None) -> Self: ...
    @overload
    @classmethod
    def from_array(cls, label: str, data: NDArray, xerr: float|NDArray, yerr: float|NDArray, color: str = None) -> Self: ...
    @classmethod
    def from_array(cls, label: str, data: NDArray, xerr: float|NDArray = nan, yerr: float|NDArray = nan, color: str = None) -> Self:
        if not data.dtype == object:
            x_vals = data[:, 0].astype(float)
            y_vals = data[:, 1].astype(float)
            data = np.column_stack((cls._uf(x_vals, xerr), cls._uf(y_vals, yerr)))
        
        return cls(label, data[:, 0], data[:, 1], color)
    
    @overload
    @classmethod
    def from_arrays(cls, label: str, x_data: NDArray, y_data: NDArray, *, color: str = None) -> Self: ...
    @overload
    @classmethod
    def from_arrays(cls, label: str, x_data: NDArray, y_data: NDArray, xerr: float|NDArray, *, color: str = None) -> Self: ...
    @overload
    @classmethod
    def from_arrays(cls, label: str, x_data: NDArray, y_data: NDArray, *, yerr: float|NDArray, color: str = None) -> Self: ...
    @overload
    @classmethod
    def from_arrays(cls, label: str, x_data: NDArray, y_data: NDArray, xerr: float|NDArray, yerr: float|NDArray, color: str = None) -> Self: ...
    @classmethod
    def from_arrays(cls, label: str, x_data: NDArray, y_data: NDArray, xerr: float|NDArray = nan, yerr: float|NDArray = nan, color: str = None) -> Self:
        if not x_data.dtype == object:
            x_data = cls._uf(x_data.astype(float), xerr)
        if not y_data.dtype == object:
            y_data = cls._uf(y_data.astype(float), yerr)
        
        return cls(label, x_data, y_data, color)
    
    @classmethod
    def from_csv(cls, file_identifier: str, label: str = None, x_row: int = 0, y_row: int = 1, skip_header: int = 1, xerr: float|NDArray = None,
                 yerr: float|NDArray = None, filetype_identifier: str = "csv", color: str = None) -> Self:
        if not label:
            label = file_identifier
        file_data = np.genfromtxt("data/" + file_identifier + "." + filetype_identifier,
                                  delimiter=",", skip_header=skip_header)
        x_data = file_data[:, x_row]
        y_data = file_data[:, y_row]
        if not xerr:
            xerr = cls.guess_error_from_array(x_data)
        if not yerr:
            yerr = cls.guess_error_from_array(y_data)
        return cls.from_arrays(label, x_data, y_data, xerr, yerr, color)
    
    @classmethod
    def from_XYFittingContainer(cls, container: XYFittingContainer) -> Self:
        label = "histogramm data" if container.label == None else container.label
        return cls(label, cls._uf(container.x, container.x_err), cls._uf(container.y, container.y_err))
    
    
    @staticmethod
    def guess_error_from_array(array: NDArray) -> float:
        return np.min((arr := (np.abs(np.diff(array))))[arr != 0]) / 2