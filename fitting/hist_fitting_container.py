import numpy as np

from collections.abc import Callable
from typing import Self, overload
from numpy.typing import NDArray
from kafe2 import HistContainer, HistFit, Plot

from fitting.kafe2_interaction_types import ParameterLimitBoundary

Real = int|float


class HistFittingContainer:
    """
    Conatiner for Histogram Data that allows to comfortably
    perform kafe2 HistFits
    """
    
    def __init__(self, container: HistContainer) -> None:
        # Organise data in a histogram container
        self.data = container
        self.adapt_label_on_operations = True
    
    def __len__(self) -> int:
        return len(self.data.bin_centers)
    
    @overload
    def __getitem__(self, key: int) -> tuple: ...
    @overload
    def __getitem__(self, key: slice) -> Self: ...
    def __getitem__(self, key):
        if isinstance(key, int):
            return (self.data.bin_centers[key], self.data.data[key])
        if not isinstance(key, slice):
            raise NotImplemented
        container = HistContainer(bin_edges=self.bin_edges[key.start:key.stop+1])
        container.set_bins(self.heights[key.start:key.stop])
        container.label = self.label
        container.axis_labels = self.axis_labels
        return self.__class__(container)
    
    def __sub__(self, other: 'HistFittingContainer') -> Self:
        if not isinstance(other, HistFittingContainer):
            raise NotImplemented
        if not len(self) == len(other):
            raise ValueError("Can't subtract HistFittingContainers of diffrent sizes")
        
        new_height_data = self.heights - other.heights
        container = HistContainer(bin_edges=self.data.bin_edges)
        container.set_bins(new_height_data)
        
        if self.adapt_label_on_operations:
            container.label = str(self.data.label) + " without " + str(other.label)
        else:
            container.label = str(self.data.label)
        if self.axis_labels == other.axis_labels:
            container.axis_labels = self.axis_labels
        
        return self.__class__(container)
    
    def __isub__(self, other: 'HistFittingContainer') -> Self:
        if not isinstance(other, HistFittingContainer):
            raise NotImplemented
        if not len(self) == len(other):
            raise ValueError("Can't subtract HistFittingContainers of diffrent sizes")
        
        new_height_data = self.heights - other.heights
        self.data.set_bins(new_height_data)
        
        if self.adapt_label_on_operations:
            self.label = str(self.data.label) + " without " + str(other.label)
        
        return self
    
    def __truediv__(self, other: Real) -> Self:
        if not isinstance(other, Real):
            raise NotImplemented

        new_height_data = np.clip(np.round(self.heights / other), 0, None)
        container = HistContainer(bin_edges=self.data.bin_edges)
        container.set_bins(new_height_data)
        container.axis_labels = self.axis_labels
        
        if self.adapt_label_on_operations:
            container.label = str(self.data.label) + " divided by " + str(other)
        else:
            container.label = str(self.data.label)
        
        return self.__class__(container)
    
    def __itruediv__(self, other: Real) -> Self:
        if not isinstance(other, Real):
            raise NotImplemented
        
        new_height_data = np.clip(np.round(self.heights / other), 0, None)
        self.data.set_bins(new_height_data)
        
        if self.adapt_label_on_operations:
            self.label = str(self.data.label) + " divided by " + str(other)
        
        return self


    @property
    def label(self) -> str|None:
        return self.data.label
    
    @label.setter
    def label(self, label: str):
        self.data.label = label
    
    @property
    def axis_labels(self):
        return self.data.axis_labels

    @property
    def bin_edges(self):
        return self.data.bin_edges
    
    @property
    def bin_mids(self):
        return self.data.bin_centers
    
    @property
    def heights(self) -> NDArray:
        return self.data.data

    @property
    def count_datapoints(self):
        return np.sum(self.data.data)

    @property
    def start(self) -> float:
        return self.bin_mids[0]
    
    @property
    def end(self) -> float:
        return self.bin_mids[-1]


    def do_hist_fit(self, model: Callable[..., float],
                    constraints: list[tuple[str, int|float, int|float]] = [],
                    fixed_params: list[tuple[str, int|float]] = [],
                    limited_params: list[tuple[str, dict[ParameterLimitBoundary, int|float]]] = [],
                    parameter_names: dict[str, str] = None,
                    model_label: str = None, model_name: str = None, model_expression: str = None,
                    show_result: bool = True, show_report: bool = False,
                    **initial_values
                    ) -> dict:
        fit = HistFit(self.data, model, density=True)
        
        # Assign parameter constraints and set as initial values
        for constraint in constraints:
            fit.add_parameter_constraint(name = constraint[0], value = constraint[1],
                                         uncertainty = constraint[2])
            fit.set_parameter_values(**{constraint[0]: constraint[1]})
        # Assign fixed parameter values
        for param_fix in fixed_params:
            fit.fix_parameter(name = param_fix[0], value = param_fix[1])
        # Apply the parameter limits passed
        for param_limit in limited_params:
            fit.limit_parameter(param_limit[0], **param_limit[1])
        # Assign additional initial values
        fit.set_parameter_values(**initial_values)
        #Assign parameter names as well as model label, name and expression
        if parameter_names != None:
            fit.assign_parameter_latex_names(**parameter_names)
        if model_label != None:
            fit.model_label = model_label
        if model_name != None:
            fit.assign_model_function_latex_name(model_name)
        if model_expression != None:
            fit.assign_model_function_latex_expression(model_expression)
        # Perform fit
        fit.do_fit()  
        # Plot fit results if desired
        if show_result:
            plot = Plot(fit)
            plot.plot()
            plot.show()
        # Report fit results if desired
        if show_report:
            fit.report()
        # Return fit
        return fit.get_result_dict()
    
    def rename(self, label: str) -> Self:
        self.label = label
        return self


    @classmethod
    def from_arrays(cls, edges: NDArray, height_data: NDArray, label: str = None,
                 axislabels: tuple[None|str, None|str] = (None, None)) -> Self:
        container = HistContainer(bin_edges=edges)
        container.set_bins(height_data)
        container.label = label
        container.axis_labels = axislabels
        return cls(container)