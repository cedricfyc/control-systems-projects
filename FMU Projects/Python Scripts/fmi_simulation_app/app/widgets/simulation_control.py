from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QDoubleSpinBox,
    QPushButton,
    QProgressBar
)
from PySide6.QtCore import Signal


class SimulationControlWidget(QWidget):
    """
    Allows the user to set basic simulation settings and control
    the execution (run/pause/stop). Does not run the simulation itself.
    Instead, it emits signals so that the GUI (MainWindow) connects to
    the SimulationEngine object.
    """

    run_requested = Signal()
    pause_requested = Signal()
    stop_requested = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        # --- Time settings form ---
        # Ideally set default values from FMU
        form_layout = QFormLayout()

        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setRange(0.0, 1_000_000.0)
        self.start_time_spin.setValue(0.0)
        form_layout.addRow("Start Time [s]", self.start_time_spin)

        self.stop_time_spin = QDoubleSpinBox()
        self.stop_time_spin.setRange(0.0, 1_000_000.0)
        self.stop_time_spin.setValue(0.0)
        form_layout.addRow("Stop Time [s]", self.stop_time_spin)

        self.step_size_spin = QDoubleSpinBox()
        self.step_size_spin.setRange(0.000001, 1.0)
        self.step_size_spin.setDecimals(6)
        self.step_size_spin.setValue(0.001)
        form_layout.addRow("Step size [s]:", self.step_size_spin)

        main_layout.addLayout(form_layout)

        # --- Run/Pause/Stop buttons ---
        button_row = QHBoxLayout()
        self.run_button = QPushButton("Run")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        button_row.addWidget(self.run_button)
        button_row.addWidget(self.pause_button)
        button_row.addWidget(self.stop_button)
        main_layout.addLayout(button_row)

        # --- Progress bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

    def _connect_signals(self) -> None:
        self.run_button.clicked.connect(self._on_run_clicked)
        self.pause_button.clicked.connect(self._on_pause_clicked)
        self.stop_button.clicked.connect(self._on_stop_clicked)

    def _on_run_clicked(self) -> None:
        self.run_requested.emit()

    def _on_pause_clicked(self) -> None:
        self.pause_requested.emit()

    def _on_stop_clicked(self) -> None:
        self.stop_requested.emit()


    # --- Public API used by MainWindow to read settings/reflect state

    def get_time_settings(self) -> dict:
        """Return the currently configured start/stop/step values as a dict"""
        return {
            "start_time": self.start_time_spin.value(),
            "stop_time": self.stop_time_spin.value(),
            "step_size": self.step_size_spin.value()
        }

    def set_running_state(self, is_running: bool) -> None:
        """Enable/disable buttons appropriately based on the run state"""
        self.run_button.setEnabled(not is_running)
        self.pause_button.setEnabled(is_running)
        self.stop_button.setEnabled(is_running)

    def set_progress(self, percent: int) -> None:
        self.progress_bar.setValue(percent)