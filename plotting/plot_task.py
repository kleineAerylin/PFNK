from typing import Protocol

class PlotTask(Protocol):
    """
    Symbolizes one plot task thats queued in the PlotHelper
    """
    
    def plot(self) -> None: ...
    
    def has_no_color(self) -> bool: ...
    
    def set_color(self, color: str | None) -> None: ...
    
    def do_xy_lims(self) -> None: ...