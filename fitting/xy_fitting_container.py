import numpy as np

from collections.abc import Callable
from typing import Literal, Self, overload
from numpy import object_, nan
from numpy.typing import NDArray
from IPython.display import display, Markdown
from uncertainties import UFloat, ufloat as uf
from kafe2 import XYContainer, XYFit, Plot

from fitting.kafe2_interaction_types import ParameterLimitBoundary
from plotting.plot_helper import PlotHelper

Real = int|float


class XYFittingContainer:
    """
    Container for XY Data with errors that allows to comfortably
    perform kafe2 XYFits
    """
    
    _uf = np.vectorize(lambda v, e: uf(v, e), otypes=[object])
    data_points_colorcyle: list[str] | None = PlotHelper.kit_color_rotation
    model_colorcycle: list[str] | None = PlotHelper.color_rotation_1
    
    def __init__(self, container: XYContainer) -> None:
        # Organize data in a xy container
        self.data = container
        self.adapt_label_on_operations = True
    
    def __len__(self) -> int:
        return self.data.size
    
    def __getitem__(self, key: slice) -> Self:
        if not isinstance(key, slice):
            raise NotImplemented
        # compute integer indices selected by the slice
        indices = np.arange(self.data.size)[key]

        container = XYContainer(self.data.x[key], self.data.y[key])

        container.label = self.label
        container.axis_labels = self.axis_labels

        # transfer only the relevant error entries (sliced)
        # we access the internal _error_dicts used by XYContainer
        orig_errs = getattr(self.data, "_error_dicts", {})
        for err_id, err_dict in orig_errs.items():
            axis = err_dict.get("axis")
            enabled = err_dict.get("enabled", True)
            name = err_dict.get("name", None)
            err_obj = err_dict.get("err")

            try:
                # Matrix-like error (has covariance matrix)
                cov = getattr(err_obj, "cov_mat", None)
                if cov is not None:
                    cov = np.asarray(cov)
                    new_cov = cov[np.ix_(indices, indices)]
                    err_val = getattr(err_obj, "err_val", None)
                    if err_val is not None:
                        err_val = np.asarray(err_val)[indices]
                    relative = getattr(err_obj, "relative", False)
                    # add as absolute covariance matrix (cov)
                    container.add_matrix_error(axis=axis, err_matrix=new_cov, matrix_type="cov", name=name, err_val=err_val, relative=relative)
                else:
                    # Simple (pointwise) Gaussian error
                    err_val = None
                    if hasattr(err_obj, "err_val"):
                        err_val = np.asarray(getattr(err_obj, "err_val"))[indices]
                    else:
                        # try generic property "error"
                        val = getattr(err_obj, "error", None)
                        if val is not None:
                            # property may be array-like
                            try:
                                err_val = np.asarray(val)[indices]
                            except Exception:
                                err_val = None

                    if err_val is None:
                        # can't determine pointwise uncertainties — skip this error
                        continue

                    corr = getattr(err_obj, "corr_coeff", 0)
                    relative = getattr(err_obj, "relative", False)
                    container.add_error(axis=axis, err_val=err_val, name=name, correlation=corr, relative=relative)

                # preserve enabled/disabled state
                if not enabled:
                    # newly added error is the last entry in _error_dicts
                    last_key = list(container._error_dicts.keys())[-1]
                    container._error_dicts[last_key]["enabled"] = enabled
            except Exception:
                # be conservative: if anything fails while copying an error, skip it
                continue

        return self.__class__(container)
    
    def __repr__(self) -> str:
        x_label, y_label = self.axis_labels or (None, None)
        x_label = x_label or 'x'
        y_label = y_label or 'y'

        x_uf = np.asarray(self.x_uf)
        y_uf = np.asarray(self.y_uf)

        rows = [(str(xv), str(yv)) for xv, yv in zip(x_uf, y_uf)]

        x_col_width = max(len(x_text) for x_text, _ in rows + [(x_label, '')])
        y_col_width = max(len(y_text) for _, y_text in rows + [('', y_label)])

        x_has_error = self.data.has_x_errors
        y_has_error = self.data.has_y_errors

        meta = [
            f"{self.__class__.__name__}:",
            f"  label       : {self.label!r}",
            f"  axis_labels : ({x_label!r}, {y_label!r})",
            f"  points      : {len(self)}",
            f"  x_range     : ({self.min_x:g}, {self.max_x:g})",
            f"  y_range     : ({self.min_y:g}, {self.max_y:g})",
            f"  x_error     : {'yes' if x_has_error else 'no'}",
            f"  y_error     : {'yes' if y_has_error else 'no'}",
            ""
        ]

        header = f"{x_label:>{x_col_width}} | {y_label:>{y_col_width}}"
        separator = f"{'-' * x_col_width}-+-{'-' * y_col_width}"
        table = [header, separator]
        table += [f"{x_text:>{x_col_width}} | {y_text:>{y_col_width}}" for x_text, y_text in rows]

        return "\n".join(meta + table)


    @property
    def label(self) -> str|None:
        return self.data.label
    
    @label.setter
    def label(self, label: str):
        self.data.label = label
    
    @property
    def axis_labels(self) -> tuple[str|None, str|None]:
        return self.data.axis_labels

    @property
    def start(self) -> float:
        return self.data.x[0]
    
    @property
    def end(self) -> float:
        return self.data.x[-1]

    @property
    def x_err(self) -> NDArray:
        return self.data.x_err

    @property
    def y_err(self) -> NDArray:
        return self.data.y_err
    
    @property
    def x(self) -> NDArray:
        return self.data.x
    
    @property
    def y(self) -> NDArray:
        return self.data.y
    
    @property
    def x_uf(self) -> NDArray:
        return self._uf(self.x, self.x_err)
    
    @property
    def y_uf(self) -> NDArray:
        return self._uf(self.y, self.y_err)
    
    @property
    def min_x(self) -> float:
        return np.min(self.x)
    
    @property
    def min_y(self) -> float:
        return np.min(self.y)
    
    @property
    def max_x(self) -> float:
        return np.max(self.x)
    
    @property
    def max_y(self) -> float:
        return np.max(self.y)
    
    @property
    def diffs_x(self) -> NDArray:
        return self.x[1:] - self.x[:-1]
    
    @property
    def diffs_y(self) -> NDArray:
        return self.y[1:] - self.y[:-1]
    
    @property
    def diffs_x_uf(self) -> NDArray:
        return self.x_uf[1:] - self.x_uf[:-1]
    
    @property
    def diffs_y_uf(self) -> NDArray:
        return self.y_uf[1:] - self.y_uf[:-1]


    def do_xy_fit(self, model: Callable[..., float],
                    constraints: list[tuple[str, int|float, int|float]] = [],
                    fixed_params: list[tuple[str, int|float]] = [],
                    limited_params: list[tuple[str, dict[ParameterLimitBoundary, int|float]]] = [],
                    parameter_names: dict[str, str] = None,
                    model_label: str = None, model_name: str = None, model_expression: str = None,
                    show_result: bool = True, show_report: bool = False,
                    plot_y_lims: list[tuple[float, float]] = None,
                    do_log_x: bool = False,
                    **initial_values
                    ) -> dict:
        fit = self.get_fit(model, constraints, fixed_params, limited_params,
                           parameter_names, model_label, model_name, model_expression,
                           **initial_values)
        return self.perform_and_plot_fits([fit], show_result, show_report, plot_y_lims, do_log_x)[0]
    
    # todo: improve this as to enable setting stuff for each specific fit
    def do_xy_fit_on_intervals(self, models: list[Callable[..., float]],
                               bounds: list[tuple[float|None, float|None]],
                               constraints: list[tuple[str, int|float, int|float]] = [],
                               fixed_params: list[tuple[str, int|float]] = [],
                               limited_params: list[tuple[str, dict[ParameterLimitBoundary, int|float]]] = [],
                               parameter_names: dict[str, str] = None,
                               model_label: str = None, model_name: str = None, model_expression: str = None,
                               show_result: bool = True, show_report: bool = False,
                               plot_y_lims: list[tuple[float, float]] = None,
                               do_log_x: bool = False,
                               **initial_values
                               ) -> list[dict]:
        fits = []
        while len(models) < len(bounds):
            models.append(models[0])
        for bound, model in zip(bounds, models):
            fit = self.slice_based_on_x(bound[0], bound[1])\
                      .get_fit(model, constraints, fixed_params, limited_params,
                               parameter_names, model_label, model_name, model_expression,
                               **initial_values)
            fit.data_container.label = f"data for fit on {bound}" # pyright: ignore[reportAttributeAccessIssue]
            fits.append(fit)
            
        return self.perform_and_plot_fits(fits, show_result, show_report, plot_y_lims, do_log_x, True)
    
    def perform_and_plot_fits(self, fits: list[XYFit],
                              show_result: bool = True,
                              show_report: bool = False,
                              plot_y_lims: list[tuple[float, float]] = None,
                              do_log_x: bool = False,
                              add_self: bool = False
                              ) -> list[dict]:
        # Perform fits
        for fit in fits:
            fit.do_fit()
        # Plot fit results
        if show_result:
            if add_self:
                plot = Plot([*fits, self.data])
            else:
                plot = Plot(fits)
            dpcc = self.data_points_colorcyle
            if dpcc and len(dpcc) >= len(fits) + add_self:
                plot.customize('data', 'color', dpcc[:len(fits) + add_self])
            mcc = self.model_colorcycle
            if mcc and len(mcc) >= len(fits) + add_self:
                plot.customize('model_line', 'color', mcc[:len(fits) + add_self])
                plot.customize('model_error_band', 'color', mcc[:len(fits) + add_self])
            if plot_y_lims:
                plot.y_range = plot_y_lims
            elif add_self:
                plot.y_range = [(self.y.min() * 1.2, self.y.max() * 1.2)] * (len(fits) + 1)
            if do_log_x:
                plot.x_scale = 'log'
            plot.plot()
            plot.show()
        # Report fit results if desired
        if show_report:
            for fit in fits:
                fit.report()
        # Return fit
        return [fit.get_result_dict() for fit in fits]

    def get_fit(self, model: Callable[..., float],
                    constraints: list[tuple[str, int|float, int|float]] = [],
                    fixed_params: list[tuple[str, int|float]] = [],
                    limited_params: list[tuple[str, dict[ParameterLimitBoundary, int|float]]] = [],
                    parameter_names: dict[str, str] = None,
                    model_label: str = None, model_name: str = None, model_expression: str = None,
                    **initial_values
                    ) -> XYFit:
        fit = XYFit(self.data, model)
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
        return fit
    
    def rename(self, label: str) -> Self:
        self.label = label
        return self
    
    def apply_to_axis(self, func: Callable, axis: Literal['x', 'y', 0, 1]) -> Self:
        try:
            new_x = func(self.x_uf) if axis in ['x', 0] else self.x_uf
            new_y = func(self.y_uf) if axis in ['y', 1] else self.y_uf
        except TypeError:
            new_x = np.array([func(x) for x in self.x_uf]) if axis in ['x', 0] else self.x_uf
            new_y = np.array([func(y) for y in self.y_uf]) if axis in ['y', 1] else self.y_uf
        
        container = XYContainer([x.n for x in new_x], [y.n for y in new_y])
        container.add_error(0, [x.s for x in new_x])
        container.add_error(1, [y.s for y in new_y])
        container.axis_labels = self.axis_labels
        container.label = self.label
        
        return self.__class__(container)
    
    def set_axis_labels(self, x_label: str, y_label: str) -> Self:
        self.data.axis_labels = (x_label, y_label)
        return self
    
    def slice_based_on_x(self, min_val: float = None, max_val: float = None) -> Self:
        mask = np.ones(self.x_uf.shape, dtype=bool)
        
        if min_val is not None:
            mask &= self.x_uf >= min_val
        if max_val is not None:
            mask &= self.x_uf <= max_val

        indices = np.flatnonzero(mask)
        indices = indices[np.argsort(self.x_uf[indices])]
        sliced_x_uf = self.x_uf[indices]
        sliced_y_uf = self.y_uf[indices]
        label = self.label if self.label else "MISSING LABEL"
        
        return self.__class__.from_arrays(label, sliced_x_uf, sliced_y_uf, axis_labels=self.axis_labels)
    
    def display(self) -> None:
        # todo: improve as that the text that is displayed is actually formatted for Markdown
        display(Markdown(str(self)))


    @overload
    @classmethod
    def from_array(cls, label: str, data: NDArray[object_], *,
                   axis_labels: tuple[str|None, str|None] = (None, None)) -> Self: ...
    @overload
    @classmethod
    def from_array(cls, label: str, data: NDArray, xerr: float, *,
                   axis_labels: tuple[str|None, str|None] = (None, None)) -> Self: ...
    @overload
    @classmethod
    def from_array(cls, label: str, data: NDArray, *, yerr: float,
                   axis_labels: tuple[str|None, str|None] = (None, None)) -> Self: ...
    @overload
    @classmethod
    def from_array(cls, label: str, data: NDArray, xerr: float, yerr: float,
                   axis_labels: tuple[str|None, str|None] = (None, None)) -> Self: ...
    @classmethod
    def from_array(cls, label: str, data: NDArray, xerr: float = nan, yerr: float = nan,
                   axis_labels: tuple[str|None, str|None] = (None, None)) -> Self:
        if not data.dtype == object and isinstance(data[0, 0], UFloat):
            x_vals = data[:, 0].astype(float)
            y_vals = data[:, 1].astype(float)
            container = XYContainer(x_vals, y_vals)
            if xerr != nan:
                container.add_error(0, xerr)
            if yerr != nan:
                container.add_error(1, yerr)
        else:
            x_vals = data[:, 0]
            y_vals = data[:, 1]
            container = XYContainer([x.n for x in x_vals], [y.n for y in y_vals])
            container.add_error(0, [x.s for x in x_vals])
            container.add_error(1, [y.s for y in y_vals])
        container.axis_labels = axis_labels
        container.label = label
        
        return cls(container)
    
    @overload
    @classmethod
    def from_arrays(cls, label: str, x_data: NDArray[object_], y_data: NDArray[object_], *,
                    axis_labels: tuple[str|None, str|None] = (None, None)) -> Self: ...
    @overload
    @classmethod
    def from_arrays(cls, label: str, x_data: NDArray, y_data: NDArray, xerr: float|NDArray, *,
                    axis_labels: tuple[str|None, str|None] = (None, None)) -> Self: ...
    @overload
    @classmethod
    def from_arrays(cls, label: str, x_data: NDArray, y_data: NDArray, *, yerr: float|NDArray,
                    axis_labels: tuple[str|None, str|None] = (None, None)) -> Self: ...
    @overload
    @classmethod
    def from_arrays(cls, label: str, x_data: NDArray, y_data: NDArray, xerr: float|NDArray,
                    yerr: float|NDArray, axis_labels: tuple[str|None, str|None] = (None, None)) -> Self: ...
    @classmethod
    def from_arrays(cls, label: str, x_data: NDArray, y_data: NDArray, xerr: float|NDArray = nan,
                    yerr: float|NDArray = nan, axis_labels: tuple[str|None, str|None] = (None, None)) -> Self:
        if x_data.dtype == object and isinstance(x_data[0], UFloat):
            x_data, xerr = np.array([x.n for x in x_data]), np.array([x.s for x in x_data])
        if y_data.dtype == object and isinstance(y_data[0], UFloat):
            y_data, yerr = np.array([y.n for y in y_data]), np.array([y.s for y in y_data])
        container = XYContainer(x_data, y_data)
        if not isinstance(xerr, float) or not np.isnan(xerr):
            container.add_error(0, xerr)
        if not isinstance(yerr, float) or not np.isnan(yerr):
            container.add_error(1, yerr)
        container.axis_labels = axis_labels
        container.label = label
        
        return cls(container)