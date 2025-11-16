import numpy as np
from qtpy.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class DrawdownPlot(QWidget):
    """
    Embedded Matplotlib plot showing observed and modeled drawdown.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.fig = Figure(figsize=(5, 4))
        self.canvas = FigureCanvasQTAgg(self.fig)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Time (minutes or days)")
        self.ax.set_ylabel("Drawdown (ft)")
        self.ax.set_title("Pumping Test Analysis")

    # -----------------------------------------
    # PUBLIC METHOD TO PLOT NEW RESULTS
    # -----------------------------------------

    def plot_drawdown(self, t, s_obs, s_theis=None, s_neuman=None):
        """
        t        : time array
        s_obs    : observed drawdown
        s_theis  : model drawdown from Theis (optional)
        s_neuman : model drawdown from Neuman (optional)
        """

        self.ax.clear()
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Drawdown (ft)")
        self.ax.set_title("Drawdown vs Time")

        # Observed points
        self.ax.plot(t, s_obs, "o", label="Observed Data", markersize=6)

        # Theis model
        if s_theis is not None:
            self.ax.plot(t, s_theis, "-", label="Theis Fit", linewidth=2)

        # Neuman model
        if s_neuman is not None:
            self.ax.plot(t, s_neuman, "--", label="Neuman Fit", linewidth=2)

        self.ax.legend()
        self.ax.grid(True, linestyle="--", alpha=0.3)

        self.canvas.draw()
