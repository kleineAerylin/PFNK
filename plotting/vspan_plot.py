import numpy as np
import matplotlib.pyplot as plt


class VSpanPlot:
    """
    PlotTask of a VSpan
    """
    
    def __init__(self, start: float, end: float, color: str = None,
                 label: str = None, main_alpha=0.2, line_alpha=0.4) -> None:
        self.start = start
        self.end = end
        self.color = color
        self.label = label
        self.main_alpha = main_alpha
        self.line_alpha = line_alpha


    def plot(self) -> None:
        plt.axvline(self.start, color=self.color,
                   alpha=self.line_alpha)
        plt.axvline(self.end, color=self.color,
                   alpha=self.line_alpha)
        plt.axvspan(self.start, self.end, color=self.color,
                    label=self.label, alpha=self.main_alpha)
    
    def has_no_color(self) -> bool:
        return self.color == None
    
    def set_color(self, color: str | None) -> None:
        self.color = color
    
    def do_xy_lims(self) -> None: ...