import matplotlib.pyplot as plt

from collections.abc import Iterable
from numpy import e, isclose

from tools.plotting.plot_task import PlotTask
from tools.plotting.axis_formatter import AxisFormatter
from tools.plotting.formatters import LogFormatter


class PlotHelper:
    """
    General wrapper to create matplotlib plots
    more easily
    """
    
    poop_color_rotation = ["xkcd:puke green", "xkcd:puke", "xkcd:vomit", "xkcd:ugly green", "xkcd:vomit green",
                           "xkcd:poop", "xkcd:snot green", "xkcd:dirt", "xkcd:shit", "xkcd:dirty pink", "xkcd:shit brown",
                           "xkcd:sickly green", "xkcd:poo brown", "xkcd:baby poop", "xkcd:slime green", "xkcd:snot",
                           "xkcd:poo", "xkcd:blood", "xkcd:ugly yellow", "xkcd:sick green", "xkcd:muddy brown", "xkcd:ugly pink",
                           "xkcd:baby poop green", "xkcd:vomit yellow", "xkcd:weird green", "xkcd:dirty blue", "xkcd:baby poo",
                           "xkcd:puke brown", "xkcd:ugly purple", "xkcd:diarrhea", "xkcd:baby shit green", "xkcd:barf green",
                           "xkcd:dried blood", "xkcd:piss yellow", "xkcd:poop green", "xkcd:shit green", "xkcd:icky green",
                           "xkcd:dirty purple", "xkcd:ugly blue", "xkcd:baby puke green", "xkcd:sickly yellow",
                           "xkcd:ugly brown", "xkcd:baby shit brown", "xkcd:nasty green"]
    color_rotation_1 = ["cornflowerblue", "lawngreen", "orangered", "darkorchid", "sandybrown", "palevioletred",
                        "xkcd:vermillion"]
    color_rotation_2 = ["darkgreen", "yellowgreen", "darkturquoise", "red"]
    
    
    def __init__(self, default_color: str = "xkcd:hot pink", sup_title_size: int = 24,
                 title_size: int = 20, plot_size: tuple[float, float] = (12, 8)) -> None:
        
        self.figure_counter: int = 0
        self.plot_queue: list[PlotTask] = []
        
        self.extra_titel: str | None = None
        self.xlabel: str = ""
        self.ylabel: str = ""
        
        self.default_color = default_color
        self.sup_title_size = sup_title_size
        self.title_size = title_size
        self.plot_size = plot_size
        
        self.do_grid: bool = True
        self._color_rotation: Iterable[str] | None = self.color_rotation_1
        self.allow_plot_xy_lims = True
        self.is_log_with_base: tuple[float|None, float|None] = (None, None)
        
        self._axis_formatters: list[AxisFormatter|None] = [None, None]


    def enqueue_plot_task(self, *plots: PlotTask) -> None:
        for plot in plots:
            self.plot_queue.append(plot)
    
    def plot_queued(self, xlabel: str, ylabel: str, extra_titel: str = None) -> None:
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.extra_titel = extra_titel
        self._plot()
    
    def plot_plot_task(self, xlabel: str, ylabel: str, *plots: PlotTask,
                       extra_titel: str = None) -> None:
        self.enqueue_plot_task(*plots)
        self.plot_queued(xlabel, ylabel, extra_titel)
    
    def set_color_rotation(self, color_rotation: Iterable[str]) -> None:
        self._color_rotation = color_rotation
    
    def clear_color_rotation(self) -> None:
        self._color_rotation = None
    
    def disable_grid(self) -> None:
        self.do_grid = False
    
    def enable_grid(self) -> None:
        self.do_grid = True
    
    def disable_plot_xy_lims(self) -> None:
        self.allow_plot_xy_lims = False
    
    def enable_plot_xy_lims(self) -> None:
        self.allow_plot_xy_lims = True
    
    def set_log_plot(self, base: tuple[float|None, float|None] = (None, None), str_repr: tuple[str|None, str|None] = (None, None)) -> None:
        self.is_log_with_base = base

        if base[0]:
            str_repr_x = str_repr[0]
            if not str_repr_x:
                str_repr_x = self._guess_str_repr(base[0])
            self.set_axis_formatter(LogFormatter(base[0], str_repr_x, "x"))
        else:
            self.set_axis_formatter(None)
        if base[1]:
            str_repr_y = str_repr[1]
            if not str_repr_y:
                str_repr_y = self._guess_str_repr(base[1])
            self.set_axis_formatter(LogFormatter(base[1], str_repr_y, "y"), 1)
        else:
            self.set_axis_formatter(None, 1)
    
    def set_axis_formatter(self, ax_formatter: AxisFormatter|None, slot: int = 0) -> None:
        self._axis_formatters[slot] = ax_formatter


    def _guess_str_repr(self, num: float) -> str:
        if isclose(num, e):
            return 'e'
        
        elif isclose(int(num), num):
            return str(int(num))
        else:
            return str(num)
    
    def _get_figure_title(self) -> str:
        self.figure_counter += 1
        return f"Diagramm ({self.figure_counter})"

    def _plot(self) -> None:
        # set the plot size
        plt.rcParams['figure.figsize'] = self.plot_size
        # add the queued plots:])
        if not self._color_rotation == None:
            color_iterator = iter(self._color_rotation)
        else:
            color_iterator = iter([])
        for plot_task in self.plot_queue:
            mark: bool = False
            if plot_task.has_no_color():
                plot_task.set_color(next(color_iterator, None))
                mark = True
            if self.allow_plot_xy_lims:
                plot_task.do_xy_lims()
            plot_task.plot()
            if mark:
                plot_task.set_color(None)
        self.plot_queue.clear()
        
        # add the layout:
        plt.suptitle(self._get_figure_title(), color=self.default_color,
                     fontweight='bold', fontsize=self.sup_title_size, x=0.5)
        if self.extra_titel:
            plt.title(self.extra_titel, color=self.default_color, fontsize=self.title_size,
                      x=0.5)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.legend()
        plt.grid(self.do_grid)
        if self.is_log_with_base[0] != None:
            plt.xscale("log", base=(b:=self.is_log_with_base[0]))
        if self.is_log_with_base[1] != None:
            plt.yscale("log", base=self.is_log_with_base[1])
        for formatter in self._axis_formatters:
            if formatter:
                formatter.format_axes()
        plt.show()