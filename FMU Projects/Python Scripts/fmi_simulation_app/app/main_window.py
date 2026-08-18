from PySide6.QtWidgets import QMainWindow, QDockWidget, QTabWidget, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence

from .core.fmu_manager import FmuManager
from .core.project_manager import ProjectManager
from .core.simulation_engine import SimulationEngine, SimulationConfig

from .widgets.model_browser import ModelBrowserWidget
from .widgets.parameter_panel import ParameterPanelWidget
from .widgets.simulation_control import SimulationControlWidget
from .widgets.plot_widget import PlotWidget
from .widgets.log_console import LogConsoleWidget


class MainWindow(QMainWindow):
    """
    Main window of the application/top-level shell.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("FMU Simulation App")
        self.resize(1400, 900)

        # --- Core (non-GUI) objects ---
        # These hold states and handle the underlying simulation work
        # The GUI communicates with those through signals.
        self.fmu_manager = FmuManager()
        self.project_manager = ProjectManager()
        # SimulationEngine object is created when a run starts
        self.simulation_engine = None
        # QThread the engine runs on; created on run
        self.simulation_thread = None

        # --- Build the UI ---
        self._create_central_widget()
        self._create_dock_widgets()
        self._create_actions()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()

        # --- Connect widget signals to our handler methods ---
        self._connect_signals()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _create_central_widget(self) -> None:
        """
        Central area of the window: a tabbed set of plots, so that the
        user can have multiplie result views open (e.g. one per
        simulation run or one per signal group).
        Returns
        -------

        """
        self.plot_tabs = QTabWidget()
        self.plot_tabs.setTabsClosable(True)
        self.plot_tabs.setMovable(True)

        # Start with one empty plot tab.
        self.default_plot_widget = PlotWidget()
        self.plot_tabs.addTab(self.default_plot_widget, "Results")

        self.setCentralWidget(self.plot_tabs)

    def _create_dock_widgets(self) -> None:
        """
        Side/bottom docks: model browser, parameter panel, simulation
        controls and log console. Docks can be dragged, floated, tabbed
        or closed by the user.
        Returns
        -------

        """
        # Model browser (left side)
        self.model_browser = ModelBrowserWidget()
        self.model_browser_dock = QDockWidget("Model Browser", self)
        self.model_browser_dock.setWidget(self.model_browser)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.model_browser_dock)

        # Parameter panel (left side, tabbed under model browser)
        self.parameter_panel = ParameterPanelWidget()
        self.parameter_panel_dock = QDockWidget("Parameters", self)
        self.parameter_panel_dock.setWidget(self.parameter_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.parameter_panel_dock)
        self.tabifyDockWidget(self.model_browser_dock, self.parameter_panel_dock)

        # Simulation control (right side)
        self.simulation_control = SimulationControlWidget()
        self.simulation_control_dock = QDockWidget("Simulation Control", self)
        self.simulation_control_dock.setWidget(self.simulation_control)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.simulation_control_dock)

        # Log console (bottom)
        self.log_console = LogConsoleWidget()
        self.log_console_dock = QDockWidget("Log Console", self)
        self.log_console_dock.setWidget(self.log_console)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_console_dock)


    def _create_actions(self) -> None:
        """
        QAction objects represent a "command" (e.g. Open File) that
        can be triggered from multiple places at once (menu item AND
        toolbar button AND keyboard shortcuts) while only being defined
        once in this method.
        Returns
        -------

        """
        # --- File actions ---
        self.action_new_project = QAction("New Project", self)
        self.action_new_project.setShortcut(QKeySequence.StandardKey.New)

        self.action_open_project = QAction("Open Project", self)
        self.action_open_project.setShortcut(QKeySequence.StandardKey.Open)

        self.action_save_project = QAction("Save Project", self)
        self.action_save_project.setShortcut(QKeySequence.StandardKey.Save)

        self.action_save_project_as = QAction("Save Project As...", self)

        self.action_import_fmu = QAction("Import FMU...", self)

        self.action_exit = QAction("Exit", self)
        self.action_exit.setShortcut(QKeySequence.StandardKey.Quit)

        # --- Edit actions ---
        self.action_preferences = QAction("Preferences", self)

        # --- Simulation actions ---
        self.action_run_simulation = QAction("Run", self)
        self.action_pause_simulation = QAction("Pause", self)
        self.action_stop_simulation = QAction("Stop", self)

        # --- View actions (toggle dock visibility) ---
        self.action_toggle_model_browser = self.model_browser_dock.toggleViewAction()
        self.action_toggle_parameter_panel = self.parameter_panel_dock.toggleViewAction()
        self.action_toggle_simulation_control = self.simulation_control_dock.toggleViewAction()
        self.action_toggle_log_console = self.log_console_dock.toggleViewAction()

        # --- Help actions ---
        self.action_about = QAction("About", self)


    def _create_menu_bar(self) -> None:
        menu_bar = self.menuBar()

        # Add file menu and implement actions
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.action_new_project)
        file_menu.addAction(self.action_open_project)
        file_menu.addAction(self.action_save_project)
        file_menu.addAction(self.action_save_project_as)
        file_menu.addSeparator() # row seperator
        file_menu.addAction(self.action_import_fmu)
        file_menu.addSeparator()
        file_menu.addAction(self.action_exit)

        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction(self.action_preferences)

        simulation_menu = menu_bar.addMenu("&Simulation")
        simulation_menu.addAction(self.action_run_simulation)
        simulation_menu.addAction(self.action_pause_simulation)
        simulation_menu.addAction(self.action_stop_simulation)

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self.action_toggle_model_browser)
        view_menu.addAction(self.action_toggle_parameter_panel)
        view_menu.addAction(self.action_toggle_simulation_control)
        view_menu.addAction(self.action_toggle_log_console)

        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction(self.action_about)


    def _create_toolbar(self) -> None:
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.addAction(self.action_import_fmu)
        toolbar.addSeparator()
        toolbar.addAction(self.action_run_simulation)
        toolbar.addAction(self.action_pause_simulation)
        toolbar.addAction(self.action_stop_simulation)

    def _create_status_bar(self) -> None:
        # showMessage() can be called later to display transient status text.
        self.statusBar().showMessage("Ready")

    # ------------------------------------------------------------------
    # Signal/slot wiring
    # ------------------------------------------------------------------
    # Connect signals to actions so that the GUI buttons can interact with the
    # methods of the core. Widget features interact with core functionalities defined.
    def _connect_signals(self) -> None:
        # File menu
        self.action_new_project.triggered.connect(self.on_new_project)
        self.action_open_project.triggered.connect(self.on_open_project)
        self.action_save_project.triggered.connect(self.on_save_project)
        self.action_save_project_as.triggered.connect(self.on_save_project_as)
        self.action_import_fmu.triggered.connect(self.on_import_fmu)
        self.action_exit.triggered.connect(self.close)

        # Edit menu
        self.action_preferences.triggered.connect(self.on_open_preferences)

        # Simulation menu/toolbar
        self.action_run_simulation.triggered.connect(self.on_run_simulation)
        self.action_pause_simulation.triggered.connect(self.on_pause_simulation)
        self.action_stop_simulation.triggered.connect(self.on_stop_simulation)

        # Help menu
        self.action_about.triggered.connect(self.on_show_about)

        # Model browser dock
        self.model_browser.add_fmu_requested.connect(self.on_import_fmu)
        self.model_browser.remove_fmu_requested.connect(self.on_remove_fmu)
        self.model_browser.fmu_selected.connect(self.on_fmu_selected)

        # Parameter panel dock
        self.parameter_panel.apply_requested.connect(self.on_apply_parameters)

        # Simulation control dock (buttons mirror the toolbar actions)
        self.simulation_control.run_requested.connect(self.on_run_simulation)
        self.simulation_control.pause_requested.connect(self.on_pause_simulation)
        self.simulation_control.stop_requested.connect(self.on_stop_simulation)

        # Plot tabs
        self.plot_tabs.tabCloseRequested.connect(self.on_plot_tab_close_requested)

    # ------------------------------------------------------------------
    # Slots / callback methods - File menu
    # ------------------------------------------------------------------

    def on_new_project(self) -> None:
        """
        Handle "New Project": reset FMUManager/ProjectManager state and
        clear all GUI panels.

        TODO: Prompt to save unsaved changes before discarding.
        """
        pass

    def on_open_project(self) -> None:
        """
        Handle "Open Project...": show a file dialog, then load the
        selected project via self.project_manager.load_project().

        TODO: Implement dialog + loading + repopulating the GUI from
              the loaded Project.
        """
        pass

    def on_save_project(self) -> None:
        """
        Handle "Save Project": save to the project's existing file path,
        or fall back to "Save As" behavior if there isn't one yet.

        TODO: Implement using self.project_manager.save_project().
        """
        pass

    def on_save_project_as(self) -> None:
        """
        Handle "Save Project As...": always show a file dialog to pick
        a new save location.

        TODO: Implement dialog + self.project_manager.save_project().
        """
        pass

    def on_import_fmu(self) -> None:
        """
        Handle "Import FMU...": show a file dialog to pick a .fmu file,
        then load it via self.fmu_manager.load_fmu() and add it to the
        model browser.

        TODO: Implement dialog + loading + error handling +
              self.model_browser.add_fmu_item(...).
        """
        pass

    # ------------------------------------------------------------------
    # Slots / callback methods - Edit menu
    # ------------------------------------------------------------------

    def on_open_preferences(self) -> None:
        """
        Handle "Preferences...": open a settings dialog.

        TODO: Build a QDialog for application preferences (units,
              default solver settings, plotting options, etc.).
        """
        pass

    # ------------------------------------------------------------------
    # Slots / callback methods - Simulation menu / controls
    # ------------------------------------------------------------------

    def on_run_simulation(self) -> None:
        """
        Handle Run: build a SimulationConfig from the current GUI state,
        create a SimulationEngine, move it to a QThread, connect its
        signals, and start the thread.

        TODO: Implement using SimulationEngine + QThread as described
              in simulation_engine.py's module docstring.
        """
        self.simulation_engine = SimulationEngine()

    def on_pause_simulation(self) -> None:
        """
        Handle Pause: forward the request to the running SimulationEngine.

        TODO: Call self.simulation_engine.pause() if a run is active.
        """
        pass

    def on_stop_simulation(self) -> None:
        """
        Handle Stop: forward the request to the running SimulationEngine
        and clean up the worker thread once it finishes.

        TODO: Call self.simulation_engine.stop() if a run is active.
        """
        pass

    def on_simulation_progress(self, percent: int) -> None:
        """
        Slot for SimulationEngine.progress_updated. Update the
        progress bar in the simulation control dock.

        TODO: self.simulation_control.set_progress(percent)
        """
        pass

    def on_simulation_data_point(self, time_value: float, values: dict) -> None:
        """
        Slot for SimulationEngine.data_point_ready. Used for live
        plotting while a simulation is running.

        TODO: Append the new point to the active plot.
        """
        pass

    def on_simulation_finished(self, result) -> None:
        """
        Slot for SimulationEngine.simulation_finished. Receives a
        SimulationResult and should display it (e.g. plot all signals,
        reset button states, clean up the worker thread).

        TODO: Implement result handling + self.simulation_control.set_running_state(False)
        """
        pass

    def on_simulation_error(self, message: str) -> None:
        """
        Slot for SimulationEngine.simulation_error. Should show the
        error to the user (e.g. via the log console and/or a message box).

        TODO: self.log_console.append_log(message, level="ERROR")
        """
        pass

    # ------------------------------------------------------------------
    # Slots / callback methods - Model browser / parameter panel
    # ------------------------------------------------------------------

    def on_remove_fmu(self, fmu_id: str) -> None:
        """
        Handle a request (from the model browser) to unload an FMU.

        TODO: Call self.fmu_manager.unload_fmu(fmu_id) and remove the
              corresponding item from the model browser tree.
        """
        pass

    def on_fmu_selected(self, fmu_id: str) -> None:
        """
        Handle the user selecting an FMU in the model browser: refresh
        the parameter panel to show that model's variables.

        TODO: params = self.fmu_manager.get_model_variables(fmu_id)
              self.parameter_panel.set_parameters(params)
        """
        pass

    def on_apply_parameters(self) -> None:
        """
        Handle "Apply Changes" in the parameter panel: push the edited
        values from the table into the FMU via FMUManager.

        TODO: values = self.parameter_panel.get_edited_values()
              # then call self.fmu_manager.set_parameter_value(...) per entry
        """
        pass

    # ------------------------------------------------------------------
    # Slots / callback methods - Plot tabs / Help
    # ------------------------------------------------------------------

    def on_plot_tab_close_requested(self, index: int) -> None:
        """
        Handle the user closing a results tab.

        TODO: Confirm/close, but keep at least one tab open.
        """
        pass

    def on_show_about(self) -> None:
        """
        Handle "About": show a simple QMessageBox with app info.

        TODO: Replace with real version/author info once decided.
        """
        QMessageBox.about(
            self,
            "About FMU Simulation Platform",
            "FMU Simulation Platform\n\nA PySide6-based application for "
            "importing and simulating Functional Mock-up Units (FMUs).",
        )

    # ------------------------------------------------------------------
    # Window lifecycle
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        """
        Called automatically by Qt when the window is about to close.

        TODO: Prompt to save unsaved changes (check
              self.project_manager.current_project.is_modified) and
              stop any running simulation thread cleanly before exit.
        """
        super().closeEvent(event)

