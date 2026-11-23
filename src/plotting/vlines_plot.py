import matplotlib.pyplot as plt


class VLinesPlot:
    """
    PlotTask of a VBar
    """
    
    def __init__(self, bottom: float, top: float, *xs: float, color: str = None,
                 label: str = None) -> None:
        self.xs = xs
        self.bottom = bottom
        self.top = top
        self.color = color
        self.label = label


    def plot(self) -> None:
        if self.label:
            plt.vlines(self.xs, self.bottom, self.top, color=self.color, label=self.label)
            return
        plt.vlines(self.xs, self.bottom, self.top, color=self.color)
    
    def has_no_color(self) -> bool:
        return self.color == None
    
    def set_color(self, color: str | None) -> None:
        self.color = color
    
    def do_xy_lims(self) -> None: ...