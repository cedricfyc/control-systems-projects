#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive PyFMI Simulation Template
========================================
A robust, production-ready template for simulating FMUs with PyFMI.

This template includes:
- Built-in PyFMI simulate() method (RECOMMENDED for most cases)
- Advanced manual integration with event handling
- Parameter adjustment and sensitivity analysis
- Multiple solver options with proper configuration
- Comprehensive error handling and validation
- Result plotting and analysis tools

Author: [Your Name]
Date: 2025
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Union

try:
    from pyfmi import load_fmu
    from pyfmi.fmi import FMUException
except ImportError:
    print("Error: pyfmi is not installed.")
    print("Install it with: pip install pyfmi")
    sys.exit(1)


class FMUSimulator:
    """
    Comprehensive FMU simulator class with PyFMI.

    This class provides a complete interface for loading, configuring,
    simulating, and analyzing FMU models using PyFMI.

    Attributes
    ----------
    fmu_path : str
        Path to the FMU file.
    model : FMUModelBase
        Loaded FMU model object.
    results : ResultDymolaTextual
        Simulation results from last run.
    """

    def __init__(self, fmu_path: str):
        """
        Initialize the FMU simulator.

        Parameters
        ----------
        fmu_path : str
            Path to the FMU file (.fmu extension).
        """
        self.fmu_path = fmu_path
        self.model = None
        self.results = None
        self._is_initialized = False

    def load_fmu(self) -> None:
        """
        Load the FMU file and perform basic validation.

        Raises
        ------
        FileNotFoundError
            If FMU file doesn't exist at specified path.
        FMUException
            If FMU loading fails.
        """
        # Validate file exists
        if not os.path.exists(self.fmu_path):
            raise FileNotFoundError(f"FMU file not found: {self.fmu_path}")

        # Validate file extension
        if not self.fmu_path.endswith('.fmu'):
            raise ValueError(f"File must have .fmu extension: {self.fmu_path}")

        print(f"\n{'=' * 70}")
        print(f"Loading FMU from: {self.fmu_path}")
        print(f"{'=' * 70}")

        try:
            # Load the FMU
            self.model = load_fmu(self.fmu_path)
            print(f"✓ Successfully loaded FMU: {self.model.get_name()}")
            print(f"  FMI Version: {self.model.get_version()}")
            print(f"  Model Identifier: {self.model.get_identifier()}")
            print(f"{'=' * 70}\n")

        except Exception as e:
            raise FMUException(f"Failed to load FMU: {e}")

    # =========================================================================
    # PARAMETER MANAGEMENT
    # =========================================================================

    def get_model_info(self) -> Dict:
        """
        Get comprehensive information about the FMU model.

        Returns
        -------
        info : dict
            Dictionary containing model metadata.
        """
        if self.model is None:
            self.load_fmu()

        info = {
            'name': self.model.get_name(),
            'version': self.model.get_version(),
            'identifier': self.model.get_identifier(),
            'author': getattr(self.model, 'author', 'Unknown'),
            'description': getattr(self.model, 'description', 'No description'),
            'generation_tool': getattr(self.model, 'generation_tool', 'Unknown'),
        }

        return info

    def list_all_variables(self, variable_type: Optional[str] = None) -> None:
        """
        List all variables in the FMU.

        Parameters
        ----------
        variable_type : str, optional
            Filter by type: 'input', 'output', 'parameter', 'state', or None for all.
        """
        if self.model is None:
            self.load_fmu()

        print(f"\n{'=' * 70}")
        print(f"FMU VARIABLES: {self.model.get_name()}")
        print(f"{'=' * 70}\n")

        model_vars = self.model.get_model_variables()

        # Categorize variables
        inputs = []
        outputs = []
        parameters = []
        states = []
        locals_vars = []

        for var_name, var_obj in model_vars.items():
            causality = getattr(var_obj, 'causality', None)
            variability = getattr(var_obj, 'variability', None)

            if causality == 0:  # Input
                inputs.append(var_name)
            elif causality == 1:  # Output
                outputs.append(var_name)
            elif variability == 1:  # Parameter (tunable)
                parameters.append(var_name)
            elif causality == 2:  # Local
                locals_vars.append(var_name)

        # Print based on filter
        if variable_type is None or variable_type.lower() == 'input':
            print(f"INPUTS ({len(inputs)}):")
            for var in inputs[:10]:  # Show first 10
                print(f"  • {var}")
            if len(inputs) > 10:
                print(f"  ... and {len(inputs) - 10} more")
            print()

        if variable_type is None or variable_type.lower() == 'output':
            print(f"OUTPUTS ({len(outputs)}):")
            for var in outputs[:10]:
                print(f"  • {var}")
            if len(outputs) > 10:
                print(f"  ... and {len(outputs) - 10} more")
            print()

        if variable_type is None or variable_type.lower() == 'parameter':
            print(f"PARAMETERS ({len(parameters)}):")
            for var in parameters[:10]:
                print(f"  • {var}")
            if len(parameters) > 10:
                print(f"  ... and {len(parameters) - 10} more")
            print()

        print(f"{'=' * 70}\n")

    def get_tunable_parameters(self) -> Dict[str, float]:
        """
        Get all tunable parameters from the FMU.

        Returns
        -------
        tunable_params : dict
            Dictionary mapping parameter names to their current values.
        """
        if self.model is None:
            self.load_fmu()

        tunable_params = {}

        try:
            model_vars = self.model.get_model_variables()

            for var_name, var_obj in model_vars.items():
                # Check if variable is a tunable parameter (variability == 1)
                if hasattr(var_obj, 'variability') and var_obj.variability == 1:
                    try:
                        current_value = self.model.get(var_name)
                        tunable_params[var_name] = current_value
                    except:
                        pass

        except Exception as e:
            print(f"Warning: Could not retrieve all tunable parameters: {e}")

        return tunable_params

    def list_tunable_parameters(self, show_values: bool = True) -> None:
        """
        Print all tunable parameters with their current values and descriptions.

        Parameters
        ----------
        show_values : bool, default=True
            If True, display current parameter values.
        """
        if self.model is None:
            self.load_fmu()

        print(f"\n{'=' * 70}")
        print("TUNABLE PARAMETERS")
        print(f"{'=' * 70}")

        try:
            model_vars = self.model.get_model_variables()
            tunable_found = False
            count = 0

            for var_name, var_obj in model_vars.items():
                # Check if variable is a tunable parameter
                if hasattr(var_obj, 'variability') and var_obj.variability == 1:
                    tunable_found = True
                    count += 1

                    description = getattr(var_obj, 'description', 'No description')

                    if show_values:
                        try:
                            current_value = self.model.get(var_name)
                            print(f"\n{count}. {var_name}")
                            print(f"   Value: {current_value}")
                            print(f"   Description: {description}")
                        except:
                            print(f"\n{count}. {var_name}")
                            print(f"   Value: Unable to retrieve")
                            print(f"   Description: {description}")
                    else:
                        print(f"\n{count}. {var_name}")
                        print(f"   Description: {description}")

            if not tunable_found:
                print("\nNo tunable parameters found in this FMU.")

        except Exception as e:
            print(f"Error retrieving parameters: {e}")

        print(f"\n{'=' * 70}\n")

    def set_parameters(self, parameters: Dict[str, float]) -> None:
        """
        Set model parameters before simulation (basic method).

        Parameters
        ----------
        parameters : dict
            Dictionary mapping parameter names to values.

        Examples
        --------
        >>> simulator.set_parameters({'mass': 10.0, 'gravity': 9.81})
        """
        if self.model is None:
            self.load_fmu()

        print(f"\nSetting parameters...")
        for param_name, param_value in parameters.items():
            try:
                self.model.set(param_name, param_value)
                print(f"  ✓ {param_name} = {param_value}")
            except Exception as e:
                print(f"  ✗ Warning: Could not set {param_name}: {e}")

    def adjust_tunable_parameters(self, param_adjustments: Dict[str, float],
                                  relative: bool = False) -> None:
        """
        Adjust tunable parameters with validation (advanced method).

        This method validates that parameters are actually tunable before
        attempting to set them, and provides clear feedback.

        Parameters
        ----------
        param_adjustments : dict
            Dictionary mapping parameter names to new values.
        relative : bool, default=False
            If True, multiply current values by the given factors.
            If False, set parameters to absolute values.

        Examples
        --------
        Absolute adjustment:
        >>> simulator.adjust_tunable_parameters({'mass': 10.0, 'gravity': 9.81})

        Relative adjustment (scale current values):
        >>> simulator.adjust_tunable_parameters({'mass': 1.5, 'damping': 0.8}, relative=True)
        """
        if self.model is None:
            self.load_fmu()

        print(f"\n{'=' * 70}")
        print("ADJUSTING TUNABLE PARAMETERS")
        print(f"{'=' * 70}\n")

        # Get all tunable parameters for validation
        tunable_params = self.get_tunable_parameters()

        for param_name, new_value in param_adjustments.items():
            # Validate parameter is tunable
            if param_name not in tunable_params:
                print(f"⚠ Warning: '{param_name}' is not a tunable parameter. Skipping.")
                continue

            try:
                current_value = self.model.get(param_name)

                if relative:
                    # Relative adjustment (multiply current value)
                    final_value = current_value * new_value
                    self.model.set(param_name, final_value)
                    print(f"✓ {param_name}: {current_value:.6g} → {final_value:.6g} (×{new_value})")
                else:
                    # Absolute adjustment (set to new value)
                    self.model.set(param_name, new_value)
                    print(f"✓ {param_name}: {current_value:.6g} → {new_value:.6g}")

            except Exception as e:
                print(f"✗ Error adjusting '{param_name}': {e}")

        print(f"\n{'=' * 70}\n")

    # =========================================================================
    # SIMULATION METHODS - BUILT-IN (RECOMMENDED)
    # =========================================================================

    def simulate(self,
                 start_time: float = 0.0,
                 final_time: float = 10.0,
                 options: Optional[Dict] = None,
                 input_data: Optional[Tuple] = None) -> object:
        """
        Run simulation using PyFMI's built-in simulate() method.

        This is the RECOMMENDED method for most FMU simulations. It uses
        high-quality, adaptive ODE solvers with automatic event handling.

        Parameters
        ----------
        start_time : float, default=0.0
            Simulation start time (seconds).
        final_time : float, default=10.0
            Simulation end time (seconds).
        options : dict, optional
            Simulation options. If None, uses default options with CVode solver.
            See configure_simulation_options() for details.
        input_data : tuple, optional
            Tuple of (input_names, input_trajectory) for time-varying inputs.
            input_names: list of input variable names
            input_trajectory: (time_array, values_array)

        Returns
        -------
        results : ResultDymolaTextual
            Simulation results object containing all variables vs. time.

        Examples
        --------
        Basic simulation:
        >>> results = simulator.simulate(final_time=10.0)

        Custom options:
        >>> opts = simulator.configure_simulation_options(solver='CVode', ncp=1000)
        >>> results = simulator.simulate(final_time=10.0, options=opts)

        With inputs:
        >>> input_names = ['input_voltage']
        >>> time_vec = np.linspace(0, 10, 100)
        >>> input_vec = np.sin(time_vec)
        >>> results = simulator.simulate(final_time=10.0,
        ...                              input_data=(input_names, (time_vec, input_vec)))
        """
        if self.model is None:
            self.load_fmu()

        # Use default options if none provided
        if options is None:
            options = self.configure_simulation_options()

        print(f"\n{'=' * 70}")
        print(f"STARTING SIMULATION: {self.model.get_name()}")
        print(f"{'=' * 70}")
        print(f"Time span: [{start_time}, {final_time}] seconds")
        print(f"Solver: {options.get('solver', 'CVode')}")
        print(f"Communication points: {options.get('ncp', 500)}")
        print(f"{'=' * 70}\n")

        try:
            # Run simulation
            if input_data is not None:
                # Simulation with time-varying inputs
                input_names, input_trajectory = input_data
                self.results = self.model.simulate(
                    start_time=start_time,
                    final_time=final_time,
                    options=options,
                    input=input_names,
                    input_trajectory=input_trajectory
                )
            else:
                # Standard simulation
                self.results = self.model.simulate(
                    start_time=start_time,
                    final_time=final_time,
                    options=options
                )

            print("✓ Simulation completed successfully!")
            print(f"  Total simulated time: {final_time - start_time} seconds")
            print(f"  Number of result points: {len(self.results['time'])}")
            print(f"{'=' * 70}\n")

            return self.results

        except Exception as e:
            print(f"\n✗ Simulation failed: {e}")
            import traceback
            traceback.print_exc()
            raise

    def configure_simulation_options(self,
                                     solver: str = 'CVode',
                                     ncp: int = 500,
                                     rtol: float = 1e-6,
                                     atol: Optional[float] = None,
                                     max_step: Optional[float] = None,
                                     initialize: bool = True) -> Dict:
        """
        Configure simulation options for the built-in simulate() method.

        Parameters
        ----------
        solver : str, default='CVode'
            ODE solver to use. Options:
            - 'CVode': Variable-order, variable-step BDF/Adams (RECOMMENDED)
            - 'Radau5IDA': Implicit Runge-Kutta, good for stiff problems
            - 'ExplicitEuler': Simple explicit Euler (not recommended)
            - 'ImplicitEuler': Simple implicit Euler
            - 'LSODAR': Automatic stiff/non-stiff switching
        ncp : int, default=500
            Number of communication points (output points).
        rtol : float, default=1e-6
            Relative tolerance for the solver.
        atol : float, optional
            Absolute tolerance. If None, uses rtol * 0.01 * nominal values.
        max_step : float, optional
            Maximum step size. If None, solver chooses automatically.
        initialize : bool, default=True
            If True, initialize the model before simulation.

        Returns
        -------
        options : dict
            Configured options dictionary for simulate().

        Notes
        -----
        CVode is recommended for most simulations as it automatically
        adapts to problem stiffness and provides excellent accuracy/speed.
        """
        if self.model is None:
            self.load_fmu()

        # Get default options from model
        options = self.model.simulate_options()

        # Set basic options
        options['ncp'] = ncp
        options['solver'] = solver
        options['initialize'] = initialize

        # Solver-specific options
        if solver == 'CVode':
            options['CVode_options'] = {
                'rtol': rtol,
                'maxord': 5,  # Maximum order (1-5 for BDF)
                'discr': 'BDF',  # BDF for stiff problems, 'Adams' for non-stiff
            }
            if atol is not None:
                options['CVode_options']['atol'] = atol
            if max_step is not None:
                options['CVode_options']['maxh'] = max_step

        elif solver == 'Radau5IDA':
            options['Radau5IDA_options'] = {
                'rtol': rtol,
            }
            if atol is not None:
                options['Radau5IDA_options']['atol'] = atol

        elif solver in ['ExplicitEuler', 'ImplicitEuler']:
            if max_step is not None:
                options['step_size'] = max_step
            else:
                options['step_size'] = 0.01  # Default step size

        return options

    # =========================================================================
    # SIMULATION METHODS - ADVANCED MANUAL INTEGRATION
    # =========================================================================

    def simulate_advanced(self,
                          start_time: float = 0.0,
                          final_time: float = 10.0,
                          dt: float = 0.01,
                          rtol: float = 1e-5,
                          variable_refs: Optional[List[str]] = None,
                          integrator: str = 'rk4') -> Tuple[np.ndarray, np.ndarray]:
        """
        Run advanced simulation with manual integration loop and event handling.

        WARNING: This method is for advanced users who need explicit control
        over the integration process. For most cases, use simulate() instead.

        This implements the low-level FMI 2.0 simulation loop with:
        - Manual time stepping
        - Event detection and handling
        - State event iteration
        - Continuous state management

        Parameters
        ----------
        start_time : float, default=0.0
            Simulation start time (seconds).
        final_time : float, default=10.0
            Simulation end time (seconds).
        dt : float, default=0.01
            Integration time step (seconds).
        rtol : float, default=1e-5
            Relative tolerance for event detection.
        variable_refs : list of str, optional
            List of variable names to track. If None, tracks all outputs.
        integrator : str, default='rk4'
            Integration method: 'euler', 'rk2', or 'rk4'.

        Returns
        -------
        t_sol : np.ndarray
            Time vector.
        sol : np.ndarray
            Solution array with shape (n_time_points, n_variables).

        Notes
        -----
        This method is useful when you need:
        - Custom integration algorithms
        - Explicit event handling
        - Step-by-step control over the simulation
        - Co-simulation with other models
        """
        if self.model is None:
            self.load_fmu()

        print(f"\n{'=' * 70}")
        print(f"STARTING ADVANCED SIMULATION: {self.model.get_name()}")
        print(f"{'=' * 70}")
        print(f"Integration method: {integrator.upper()}")
        print(f"Time step: {dt} seconds")
        print(f"{'=' * 70}\n")

        # ===== INITIALIZATION PHASE =====
        try:
            self.model.setup_experiment(start_time=start_time)
            self.model.enter_initialization_mode()
            self.model.exit_initialization_mode()
        except Exception as e:
            raise RuntimeError(f"Initialization failed: {e}")

        # Initial event iteration (handle discrete states at t=0)
        eInfo = self.model.get_event_info()
        eInfo.newDiscreteStatesNeeded = True
        while eInfo.newDiscreteStatesNeeded:
            self.model.enter_event_mode()
            self.model.event_update()
            eInfo = self.model.get_event_info()
        self.model.enter_continuous_time_mode()

        # Get initial continuous states
        x = self.model.continuous_states
        x_nominal = self.model.nominal_continuous_states
        event_ind = self.model.get_event_indicators()

        # Get variable references for output tracking
        if variable_refs is None:
            variable_refs = []

        vref = []
        for var in variable_refs:
            try:
                vref.append(self.model.get_variable_valueref(var))
            except:
                print(f"Warning: Could not get reference for variable '{var}'")

        # Initialize solution storage
        t_sol = [start_time]
        sol = [self.model.get_real(vref)] if vref else []

        # ===== MAIN INTEGRATION LOOP =====
        time = start_time
        T_next = final_time  # Next time event
        atol = 0.01 * rtol * x_nominal
        step_count = 0
        event_count = 0

        while time < final_time and not self.model.get_event_info().terminateSimulation:

            # --- Integration Step ---
            h = min(dt, T_next - time)  # Determine step size

            # Choose integrator
            if integrator.lower() == 'euler':
                x_new = self._euler_step(x, h)
            elif integrator.lower() == 'rk2':
                x_new = self._rk2_step(x, h)
            elif integrator.lower() == 'rk4':
                x_new = self._rk4_step(x, h)
            else:
                raise ValueError(f"Unknown integrator: {integrator}")

            # Advance time and update states
            time = time + h
            self.model.time = time
            x = x_new
            self.model.continuous_states = x

            # --- Event Detection ---
            event_ind_new = self.model.get_event_indicators()

            # Check for different event types
            step_event = self.model.completed_integrator_step()
            time_event = abs(time - T_next) <= 1e-10
            state_event = any((event_ind_new > 0.0) != (event_ind > 0.0))

            # --- Event Handling ---
            if step_event or time_event or state_event:
                event_count += 1
                self.model.enter_event_mode()
                eInfo = self.model.get_event_info()
                eInfo.newDiscreteStatesNeeded = True

                # Event iteration loop
                while eInfo.newDiscreteStatesNeeded:
                    self.model.event_update(intermediateResult=True)
                    eInfo = self.model.get_event_info()

                # Update states if they changed during event
                if eInfo.valuesOfContinuousStatesChanged:
                    x = self.model.continuous_states

                # Update nominal values if they changed
                if eInfo.nominalsOfContinuousStatesChanged:
                    atol = 0.01 * rtol * self.model.nominal_continuous_states

                # Schedule next time event
                if eInfo.nextEventTimeDefined:
                    T_next = min(eInfo.nextEventTime, final_time)
                else:
                    T_next = final_time

                self.model.enter_continuous_time_mode()
                event_ind = event_ind_new

            # Store solution
            t_sol.append(time)
            if vref:
                sol.append(self.model.get_real(vref))

            step_count += 1

        print(f"✓ Advanced simulation completed!")
        print(f"  Integration steps: {step_count}")
        print(f"  Events handled: {event_count}")
        print(f"  Data points: {len(t_sol)}")
        print(f"{'=' * 70}\n")

        return np.array(t_sol), np.array(sol)

    def _euler_step(self, x: np.ndarray, h: float) -> np.ndarray:
        """Explicit Euler integration step: x_new = x + h * f(x)"""
        dx = self.model.get_derivatives()
        return x + h * dx

    def _rk2_step(self, x: np.ndarray, h: float) -> np.ndarray:
        """2nd-order Runge-Kutta (midpoint method)."""
        # k1 = f(x)
        k1 = self.model.get_derivatives()

        # k2 = f(x + h/2 * k1)
        self.model.continuous_states = x + 0.5 * h * k1
        k2 = self.model.get_derivatives()

        # x_new = x + h * k2
        return x + h * k2

    def _rk4_step(self, x: np.ndarray, h: float) -> np.ndarray:
        """4th-order Runge-Kutta integration step."""
        time = self.model.time

        # k1 = f(x, t)
        k1 = self.model.get_derivatives()

        # k2 = f(x + h/2 * k1, t + h/2)
        self.model.time = time + 0.5 * h
        self.model.continuous_states = x + 0.5 * h * k1
        k2 = self.model.get_derivatives()

        # k3 = f(x + h/2 * k2, t + h/2)
        self.model.continuous_states = x + 0.5 * h * k2
        k3 = self.model.get_derivatives()

        # k4 = f(x + h * k3, t + h)
        self.model.time = time + h
        self.model.continuous_states = x + h * k3
        k4 = self.model.get_derivatives()

        # x_new = x + h/6 * (k1 + 2*k2 + 2*k3 + k4)
        return x + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

    # =========================================================================
    # RESULT ANALYSIS AND PLOTTING
    # =========================================================================

    def get_variable(self, var_name: str) -> np.ndarray:
        """
        Get variable values from simulation results.

        Parameters
        ----------
        var_name : str
            Name of the variable to retrieve.

        Returns
        -------
        values : np.ndarray
            Variable values over time.

        Raises
        ------
        ValueError
            If no simulation results are available or variable not found.
        """
        if self.results is None:
            raise ValueError("No simulation results available. Run simulate() first.")

        try:
            return self.results[var_name]
        except KeyError:
            raise ValueError(f"Variable '{var_name}' not found in results.")

    def get_time(self) -> np.ndarray:
        """Get the time vector from simulation results."""
        if self.results is None:
            raise ValueError("No simulation results available. Run simulate() first.")
        return self.results['time']

    def plot_results(self,
                     variables: List[str],
                     save_path: Optional[str] = None,
                     show: bool = True,
                     figsize: Tuple[int, int] = (12, 8),
                     grid: bool = True) -> Tuple:
        """
        Plot simulation results for specified variables.

        Parameters
        ----------
        variables : list of str
            List of variable names to plot.
        save_path : str, optional
            Path to save the plot. If None, plot is not saved.
        show : bool, default=True
            If True, display the plot interactively.
        figsize : tuple, default=(12, 8)
            Figure size (width, height) in inches.
        grid : bool, default=True
            If True, show grid on plots.

        Returns
        -------
        fig : matplotlib.figure.Figure
            Figure object.
        axes : array of matplotlib.axes.Axes
            Array of subplot axes.

        Examples
        --------
        >>> simulator.plot_results(['height', 'velocity'], save_path='results.png')
        """
        if self.results is None:
            raise ValueError("No simulation results available. Run simulate() first.")

        time = self.get_time()
        n_vars = len(variables)

        # Create subplots
        fig, axes = plt.subplots(n_vars, 1, figsize=figsize, squeeze=False)
        axes = axes.flatten()

        # Plot each variable
        for i, var_name in enumerate(variables):
            try:
                values = self.get_variable(var_name)

                axes[i].plot(time, values, linewidth=2, label=var_name)
                axes[i].set_xlabel('Time (s)', fontsize=12)
                axes[i].set_ylabel(var_name, fontsize=12)
                axes[i].set_title(f'{var_name} vs Time', fontsize=14, fontweight='bold')

                if grid:
                    axes[i].grid(True, alpha=0.3, linestyle='--')

                axes[i].legend(loc='best')

            except ValueError as e:
                print(f"Warning: Could not plot '{var_name}': {e}")

        plt.tight_layout()

        # Save if requested
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✓ Plot saved to: {save_path}")

        # Show if requested
        if show:
            plt.show()

        return fig, axes

    def plot_phase_diagram(self,
                           var_x: str,
                           var_y: str,
                           save_path: Optional[str] = None,
                           show: bool = True) -> Tuple:
        """
        Create a phase diagram (state space plot) of two variables.

        Parameters
        ----------
        var_x : str
            Variable name for x-axis.
        var_y : str
            Variable name for y-axis.
        save_path : str, optional
            Path to save the plot.
        show : bool, default=True
            If True, display the plot.

        Returns
        -------
        fig : matplotlib.figure.Figure
            Figure object.
        ax : matplotlib.axes.Axes
            Axes object.
        """
        if self.results is None:
            raise ValueError("No simulation results available. Run simulate() first.")

        x_data = self.get_variable(var_x)
        y_data = self.get_variable(var_y)

        fig, ax = plt.subplots(figsize=(10, 8))

        # Plot trajectory
        ax.plot(x_data, y_data, linewidth=2, alpha=0.7)

        # Mark start and end points
        ax.plot(x_data[0], y_data[0], 'go', markersize=10, label='Start')
        ax.plot(x_data[-1], y_data[-1], 'ro', markersize=10, label='End')

        ax.set_xlabel(var_x, fontsize=12)
        ax.set_ylabel(var_y, fontsize=12)
        ax.set_title(f'Phase Diagram: {var_y} vs {var_x}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='best')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✓ Phase diagram saved to: {save_path}")

        if show:
            plt.show()

        return fig, ax

    def print_summary(self) -> None:
        """Print a summary of simulation results."""
        if self.results is None:
            print("No simulation results available.")
            return

        time = self.get_time()

        print(f"\n{'=' * 70}")
        print("SIMULATION SUMMARY")
        print(f"{'=' * 70}")
        print(f"Model: {self.model.get_name()}")
        print(f"Time span: [{time[0]:.3f}, {time[-1]:.3f}] seconds")
        print(f"Number of data points: {len(time)}")
        print(f"Average time step: {np.mean(np.diff(time)):.6f} seconds")
        print(f"{'=' * 70}\n")

    # =========================================================================
    # PARAMETER SENSITIVITY ANALYSIS
    # =========================================================================

    def parameter_sweep(self,
                        param_name: str,
                        param_values: List[float],
                        output_vars: List[str],
                        start_time: float = 0.0,
                        final_time: float = 10.0,
                        plot: bool = True) -> Dict:
        """
        Perform parameter sweep (sensitivity analysis).

        Run multiple simulations with different parameter values and
        collect results for comparison.

        Parameters
        ----------
        param_name : str
            Name of parameter to vary.
        param_values : list of float
            List of parameter values to test.
        output_vars : list of str
            List of output variables to track.
        start_time : float, default=0.0
            Simulation start time.
        final_time : float, default=10.0
            Simulation end time.
        plot : bool, default=True
            If True, create comparison plots.

        Returns
        -------
        sweep_results : dict
            Dictionary containing results for each parameter value.

        Examples
        --------
        >>> results = simulator.parameter_sweep(
        ...     param_name='mass',
        ...     param_values=[5.0, 10.0, 15.0, 20.0],
        ...     output_vars=['height', 'velocity']
        ... )
        """
        print(f"\n{'=' * 70}")
        print(f"PARAMETER SWEEP: {param_name}")
        print(f"{'=' * 70}")
        print(f"Parameter values: {param_values}")
        print(f"Output variables: {output_vars}")
        print(f"{'=' * 70}\n")

        sweep_results = {
            'parameter_name': param_name,
            'parameter_values': param_values,
            'output_vars': output_vars,
            'results': []
        }

        # Run simulation for each parameter value
        for i, param_val in enumerate(param_values):
            print(f"Running simulation {i + 1}/{len(param_values)}: {param_name} = {param_val}")

            # Reload FMU for fresh start
            self.model = None
            self.load_fmu()

            # Set parameter
            self.set_parameters({param_name: param_val})

            # Run simulation
            results = self.simulate(start_time=start_time, final_time=final_time)

            # Store results
            sweep_results['results'].append({
                'param_value': param_val,
                'time': results['time'],
                'outputs': {var: results[var] for var in output_vars}
            })

        # Create comparison plots
        if plot:
            self._plot_parameter_sweep(sweep_results)

        print(f"\n✓ Parameter sweep completed!")
        print(f"{'=' * 70}\n")

        return sweep_results

    def _plot_parameter_sweep(self, sweep_results: Dict) -> None:
        """Create plots comparing results from parameter sweep."""
        param_name = sweep_results['parameter_name']
        param_values = sweep_results['parameter_values']
        output_vars = sweep_results['output_vars']
        results = sweep_results['results']

        n_vars = len(output_vars)
        fig, axes = plt.subplots(n_vars, 1, figsize=(12, 4 * n_vars), squeeze=False)
        axes = axes.flatten()

        # Color map for different parameter values
        colors = plt.cm.viridis(np.linspace(0, 1, len(param_values)))

        for i, var_name in enumerate(output_vars):
            for j, result in enumerate(results):
                time = result['time']
                values = result['outputs'][var_name]
                param_val = result['param_value']

                axes[i].plot(time, values, linewidth=2,
                             color=colors[j],
                             label=f'{param_name}={param_val:.3g}')

            axes[i].set_xlabel('Time (s)', fontsize=12)
            axes[i].set_ylabel(var_name, fontsize=12)
            axes[i].set_title(f'{var_name} vs Time (Parameter Sweep)',
                              fontsize=14, fontweight='bold')
            axes[i].grid(True, alpha=0.3, linestyle='--')
            axes[i].legend(loc='best', fontsize=10)

        plt.tight_layout()
        plt.savefig(f'parameter_sweep_{param_name}.png', dpi=150, bbox_inches='tight')
        print(f"✓ Sweep plots saved to: parameter_sweep_{param_name}.png")
        plt.show()


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def example_basic_usage():
    """Example 1: Basic FMU simulation with built-in solver (RECOMMENDED)."""

    print("\n" + "=" * 70)
    print("EXAMPLE 1: BASIC SIMULATION")
    print("=" * 70 + "\n")

    # Path to your FMU
    fmu_path = "path/to/your/model.fmu"

    try:
        # 1. Create simulator and load FMU
        sim = FMUSimulator(fmu_path)
        sim.load_fmu()

        # 2. Explore the model (optional)
        sim.list_all_variables(variable_type='output')
        sim.list_tunable_parameters()

        # 3. Set/adjust parameters (optional)
        sim.adjust_tunable_parameters({
            'mass': 10.0,
            'gravity': 9.81
        })

        # 4. Configure simulation options
        options = sim.configure_simulation_options(
            solver='CVode',
            ncp=1000,
            rtol=1e-6
        )

        # 5. Run simulation
        results = sim.simulate(
            start_time=0.0,
            final_time=10.0,
            options=options
        )

        # 6. Plot results
        sim.plot_results(
            variables=['output1', 'output2'],
            save_path='simulation_results.png',
            show=True
        )

        # 7. Print summary
        sim.print_summary()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_parameter_sensitivity():
    """Example 2: Parameter sensitivity analysis."""

    print("\n" + "=" * 70)
    print("EXAMPLE 2: PARAMETER SENSITIVITY ANALYSIS")
    print("=" * 70 + "\n")

    fmu_path = "path/to/your/model.fmu"

    try:
        sim = FMUSimulator(fmu_path)

        # Run parameter sweep
        sweep_results = sim.parameter_sweep(
            param_name='damping_coefficient',
            param_values=[0.1, 0.5, 1.0, 2.0, 5.0],
            output_vars=['position', 'velocity'],
            final_time=20.0,
            plot=True
        )

    except Exception as e:
        print(f"Error: {e}")


def example_advanced_integration():
    """Example 3: Advanced simulation with manual integration."""

    print("\n" + "=" * 70)
    print("EXAMPLE 3: ADVANCED MANUAL INTEGRATION")
    print("=" * 70 + "\n")

    fmu_path = "path/to/your/model.fmu"

    try:
        sim = FMUSimulator(fmu_path)
        sim.load_fmu()

        # Run with manual RK4 integration
        t_sol, sol = sim.simulate_advanced(
            start_time=0.0,
            final_time=10.0,
            dt=0.01,
            variable_refs=['height', 'velocity'],
            integrator='rk4'  # Options: 'euler', 'rk2', 'rk4'
        )

        # Plot manually
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 1, 1)
        plt.plot(t_sol, sol[:, 0])
        plt.ylabel('Height')
        plt.grid(True)

        plt.subplot(2, 1, 2)
        plt.plot(t_sol, sol[:, 1])
        plt.xlabel('Time (s)')
        plt.ylabel('Velocity')
        plt.grid(True)

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error: {e}")


def example_with_inputs():
    """Example 4: Simulation with time-varying inputs."""

    print("\n" + "=" * 70)
    print("EXAMPLE 4: SIMULATION WITH TIME-VARYING INPUTS")
    print("=" * 70 + "\n")

    fmu_path = "path/to/your/model.fmu"

    try:
        sim = FMUSimulator(fmu_path)
        sim.load_fmu()

        # Define input signal
        time_vec = np.linspace(0, 10, 1000)
        input_signal = 5.0 * np.sin(2 * np.pi * 0.5 * time_vec)  # 0.5 Hz sine wave

        # Run simulation with input
        results = sim.simulate(
            final_time=10.0,
            input_data=(['input_force'], (time_vec, input_signal))
        )

        # Plot results
        sim.plot_results(['position', 'velocity'])

    except Exception as e:
        print(f"Error: {e}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyFMI COMPREHENSIVE SIMULATION TEMPLATE")
    print("=" * 70)
    print("\nChoose an example to run:")
    print("  1. Basic simulation (RECOMMENDED)")
    print("  2. Parameter sensitivity analysis")
    print("  3. Advanced manual integration")
    print("  4. Simulation with time-varying inputs")
    print("=" * 70 + "\n")

    # Uncomment the example you want to run:
    # example_basic_usage()
    # example_parameter_sensitivity()
    # example_advanced_integration()
    # example_with_inputs()

    print("Please uncomment one of the example functions to run.")