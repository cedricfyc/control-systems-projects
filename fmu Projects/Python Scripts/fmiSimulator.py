import os
import numpy as np
from typing import Dict, Optional, Tuple, List
from pyfmi import load_fmu
from pyfmi.fmi import FMUException
import csv

class fmiSimulator:
    """
    Load the FMU file and perform basic validation.

    Raises
    ------
    FileNotFoundError
        If FMU file doesn't exist at specified path.
    FMUException
        If FMU loading fails.
    """

    def __init__(self, fmu_path: str):
        self.fmu_path = fmu_path
        self.model = None
        self.results = None
        self._is_initialised = False

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
        if not os.path.exists(self.fmu_path):
            raise FileNotFoundError("FMU does not exist")

        # Validate file extension
        if not self.fmu_path.endswith('.fmu'):
            raise ValueError(f"File must have .fmu extension: {self.fmu_path}")

        print(f"\n{'=' * 70}")
        print(f"Loading FMU from: {self.fmu_path}")
        print(f"{'=' * 70}")

        try:
            # Load FMU
            self.model = load_fmu(self.fmu_path)
            print(f" Model Name: {self.model.get_version()}")
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

    def list_all_variables(self) -> None:
        """
        List all variables in the FMU.
        """
        if self.model is None:
            self.load_fmu()

        print(f"\n{'=' * 70}")
        print(f"FMU VARIABLES of {self.model.get_name()}")
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

        print(f"({len(inputs)}) INPUTS")
        for var in inputs:
            print(f"  • {var}")

        print(f"({len(outputs)}) OUTPUTS")
        for var in outputs:
            print(f"  • {var}")

        print(f"({len(parameters)}) PARAMETERS")
        for var in parameters:
            print(f"  • {var}")

        print(f"{'=' * 70}\n")

    def list_tunable_parameters(self) -> None:
        """
        Print all tunable parameters with their current values and descriptions.
        """
        if self.model is None:
            self.load_fmu()

        print(f"\n{'=' * 70}")
        print(f"FMU VARIABLES of {self.model.get_name()}")
        print(f"{'=' * 70}\n")

        try:
            model_vars = self.model.get_model_variables()
            tunable_found = False
            count = 0

            for var_name, var_obj in model_vars.items():
                # Check if variable is a tunable parameter
                if hasattr(var_obj, 'variability') and var_obj.variability == 1:
                    tunable_found = True
                    count += 1

                    # default values is 'No description'
                    description = getattr(var_obj, 'description', 'No description')

                    # display tunable parameters with current values
                    try:
                        current_value = self.model.get(var_name)
                        print(f"\n{count}. {var_name}")
                        print(f"   Value: {current_value}")
                        print(f"   Description: {description}")
                    except:
                        print(f"\n{count}. {var_name}")
                        print(f"   Value: Unable to retrieve")
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
        simulator = fmiSimulator()
        simulator.set_parameters({'mass': 10.0, 'gravity': 9.81})
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
        simulator = fmiSimulator()
        results = simulator.simulate(final_time=10.0)

        Retrieve Results:
        results = simulator.simulate(final_time=10.0)

        With inputs:
        input_name = ['input_voltage']
        time_vec = np.linspace(0, 10, 100)
        input_vec = np.sin(time_vec)
        results = simulator.simulate(final_time=10.0,
        ...                              input_data=(input_name, (time_vec, input_vec)))
        """

        if self.model is None:
            self.load_fmu()

        print(f"\n{'=' * 70}")
        print(f"STARTING SIMULATION FOR: {self.model.get_name()}")
        print(f"{'=' * 70}")
        print(f"Time span: [{start_time}, {final_time}] s")
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

            # Prints the full error traceback, which is extremely useful for debugging.
            import traceback
            traceback.print_exc()

            # Re-throws the exception after printing it.
            raise

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

    def save_results_csv(self, filename: str) -> None:
        """
        Save all simulation results to a CSV file.

        Parameters
        ----------
        filename : str
            Path to the output CSV file.

        Raises
        ------
        ValueError
            If no simulation results are available.
        """
        if self.results is None:
            raise ValueError("No simulation results available. Run simulate() first.")

        # Get all variable names, with 'time' first
        var_names = ['time'] + [var for var in self.results.keys() if var != 'time']

        # Open file and write CSV
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(var_names)

            # Get length of time array
            n_rows = len(self.results['time'])

            # Write data row by row
            for i in range(n_rows):
                row = [self.results[var][i] for var in var_names]
                writer.writerow(row)



    def parameter_sweep(self,
                        param_name: str,
                        param_values: List[float],
                        output_vars: List[str],
                        start_time: float = 0.0,
                        final_time: float = 10.0,
                        plot: bool = True,
                        save_csv: bool = True,
                        csv_dir: str = 'parameter_sweep_results') -> Dict:
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
        save_csv : bool, default=True
            If True, save results to CSV files.
        csv_dir : str, default='parameter_sweep_results'
            Directory to save CSV files.

        Returns
        -------
        sweep_results : dict
            Dictionary containing results for each parameter value.

        Examples
        --------
        simulator = fmiSimulator(fmu_path=fmu_path)
        results = simulator.parameter_sweep(
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

        # Create directory for CSV files if needed
        if save_csv:
            os.makedirs(csv_dir, exist_ok=True)

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

            # Save individual simulation to CSV
            if save_csv:
                csv_filename = os.path.join(
                    csv_dir,
                    f"{param_name}_{param_val:.6f}.csv".replace('.', 'p')
                )
                self._save_sweep_csv(csv_filename, results, output_vars)
                print(f"  ✓ Saved to {csv_filename}")

        # Save summary CSV with all results
        if save_csv:
            summary_filename = os.path.join(csv_dir, f"{param_name}_summary.csv")
            self._save_sweep_summary_csv(summary_filename, sweep_results)
            print(f"\n✓ Summary saved to {summary_filename}")

        print(f"\n✓ Parameter sweep completed!")
        print(f"{'=' * 70}\n")

        return sweep_results


    def _save_sweep_csv(self, filename: str, results: Dict, output_vars: List[str]) -> None:
        """
        Save individual sweep simulation results to CSV.

        Parameters
        ----------
        filename : str
            Path to output CSV file.
        results : dict
            Simulation results dictionary.
        output_vars : list of str
            List of output variables to save.
        """
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header
            header = ['time'] + output_vars
            writer.writerow(header)

            # Write data rows
            n_rows = len(results['time'])
            for i in range(n_rows):
                row = [results['time'][i]] + [results[var][i] for var in output_vars]
                writer.writerow(row)


    def _save_sweep_summary_csv(self, filename: str, sweep_results: Dict) -> None:
        """
        Save parameter sweep summary to CSV.

        This creates a wide-format CSV where each parameter value gets its own columns.

        Parameters
        ----------
        filename : str
            Path to output CSV file.
        sweep_results : dict
            Dictionary containing all sweep results.
        """
        param_name = sweep_results['parameter_name']
        output_vars = sweep_results['output_vars']

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)

            # Create header
            header = ['time']
            for result in sweep_results['results']:
                param_val = result['param_value']
                for var in output_vars:
                    header.append(f"{var}_{param_name}={param_val}")
            writer.writerow(header)

            # Write data rows
            n_rows = len(sweep_results['results'][0]['time'])
            for i in range(n_rows):
                row = [sweep_results['results'][0]['time'][i]]
                for result in sweep_results['results']:
                    for var in output_vars:
                        row.append(result['outputs'][var][i])
                writer.writerow(row)

    # # =============================================================================
    # # EXAMPLE USAGE
    # # =============================================================================

    @staticmethod
    def example_basic_usage() -> None:
        """Example 1: Basic FMU simulation with built-in solver (RECOMMENDED)."""

        print("\n" + "=" * 70)
        print("EXAMPLE 1: BASIC SIMULATION")
        print("=" * 70 + "\n")

        # Path to your FMU
        fmu_path = "path/to/your/model.fmu"

        try:
            # 1. Create simulator and load FMU
            sim = fmiSimulator(fmu_path)
            sim.load_fmu()

            # 2. Explore the model (optional)
            sim.list_all_variables()
            sim.list_tunable_parameters()

            # 3. Set/adjust parameters (optional)
            sim.set_parameters({
                'mass': 10.0,
                'gravity': 9.81
            })

            # 5. Run simulation
            results = sim.simulate(
                start_time=0.0,
                final_time=10.0
            )

            # 7. Print summary
            sim.save_results_csv("testResults.csv")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
