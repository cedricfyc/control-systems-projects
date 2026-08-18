from PySide6.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class PlotWidget(QWidget):
    """
    Integrates a Matplotlib Figure/Canvas into the Qt layout system
    so that simulation results can be displayed within a widget.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Figure is the top-level Matplotlib drawing surface
        # FigureCanvas is the Qt widget that actually renders it
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # Standard Matplotlib pan/zoom/save toolbar for the canvas
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Subplots set - multiple axes can also be configured
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("Value")
        self.axes.grid(True)

        # Add toolbar and canvas
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def plot_signal(self, time_values: list, signal_values: list, label: str = "") -> None:
        """
        Plot a single time-series signal on the axes of the canvas.

        TODO: Decide on a strategy for multiple signals/overlays,
              legends, and live-updating during a running simulation
              (e.g. redraw every N data points instead of every point,
              for performance).

        Parameters
        ----------
        time_values
        signal_values
        label

        Returns
        -------

        """

        raise NotImplementedError

    def clear(self):
        """Remove all plotted data and reset the axes."""
        self.axes.clear()
        self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("Value")
        self.axes.grid(True)
        self.canvas.draw()