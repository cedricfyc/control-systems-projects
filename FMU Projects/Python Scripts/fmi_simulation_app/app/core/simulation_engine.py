from dataclasses import dataclass, field

from PySide6.QtCore import QObject, Signal

@dataclass
class SimulationConfig:
    """Holds all settings needed to run a simulation."""

    # experiment details
    start_time: float = 0.0
    stop_time: float = 0.0
    step_size: float = 0.0

    # FMUs that are included
    fmu_ids: list = field(default_factory=list)

    # Format -> {fmu_id: {var_name: value}}
    parameter_overrides: dict = field(default_factory=dict)


@dataclass
class SimulationResult:
    """
    Holds the time-series outputs of a completed simulation run.
    """
    # list[float]
    time: list = field(default_factory=list)

    # {signal_name: list[float]}
    signals: list = field(default_factory=list)

    # any metadata placeholder
    metadata: dict = field(default_factory=dict)


class SimulationEngine(QObject):
    """
    Executes a simulation run. Intended to be run on a different thread
    from the GUI so that the latter is not blocked.
    """

    # --- Signals: how this object communicates progress/results back to the GUI ---
    # percent complete, 0-100
    progress_updated = Signal(int)

    # human-readable status text
    status_message = Signal(str)

    # (time, {signal_name: value}) for live plotting
    data_point_ready = Signal(float, dict)

    # emits a SimulationResult when done
    simulation_finished = Signal(object)

    # emits an error message on failure
    simulation_error = Signal(str)

    def __init__(self, fmu_manager=None, config: SimulationConfig = None):
        # call parent constructor
        super().__init__()
        self.fmu_manager = fmu_manager
        self.config = config or SimulationConfig()
        self._is_running = False
        self._is_paused = False
        self._stop_requested = False

    def configure(self, config: SimulationConfig):
        """Update the simulation configuration before running"""
        self.config = config

    def run(self):
        """
        Main simulation loop entry point. Meant to be connected to
        QThread.started so it runs on the worker thread.

        TODO: Implement the actual time-stepping loop:
              - Initialize FMU instance(s) via self.fmu_manager.
              - Loop from start_time to stop_time in increments of step_size.
              - At each step: set inputs, do_step(), read outputs.
              - Emit progress_updated / data_point_ready as you go.
              - Respect self._stop_requested and self._is_paused.
              - On completion, build a SimulationResult and emit
                simulation_finished. On failure, emit simulation_error.
        """
        raise NotImplementedError

    def pause(self) -> None:
        """Pause a running simulation (checked cooperatively inside run())."""
        self._is_paused = True

    def resume(self) -> None:
        """Resume a paused simulation."""
        self._is_paused = False

    def stop(self) -> None:
        """Request that the running simulation stop early."""
        self._stop_requested = True

    def is_running(self) -> bool:
        """Return state of simulation: running or paused."""
        return self._is_running