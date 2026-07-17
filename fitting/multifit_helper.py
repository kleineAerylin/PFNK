from kafe2 import MultiFit, Plot, FitBase

class MultiFitHelper:
    """
    General wrapper to create kafe2 MultiFits
    more easily
    """
    
    def do_mf(self, *fits: FitBase, show_result: bool = True, show_report: bool = False,
                    plot_y_lims: tuple[float, float] = None, seperate_figures: bool = True,
                    do_log_x: bool = False) -> dict:
        
        fit = MultiFit(fits)
        # Perform fit
        fit.do_fit()
        # Plot fit results if desired
        if show_result:
            plot = Plot(fit, seperate_figures)
            if plot_y_lims:
                plot.y_range = [plot_y_lims]
            if do_log_x:
                plot.x_scale = 'log'
            plot.plot()
            plot.show()
        # Report fit results if desired
        if show_report:
            fit.report()
        # Return fit
        return fit.get_result_dict()