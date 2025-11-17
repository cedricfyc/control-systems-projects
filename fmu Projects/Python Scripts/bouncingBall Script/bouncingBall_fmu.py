#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bouncing Ball FMU Simulation
Simulates a bouncing ball using FMI/FMU and plots the results.
"""

import os
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("QtAgg")

try:
    from pyfmi import load_fmu
except ImportError:
    print("Error: pyfmi is not installed. Install it with: pip install pyfmi")
    sys.exit(1)


def run_demo(with_plots=True, show_plots=False):
    """
    Run the bouncing ball simulation.

    Parameters
    ----------
    with_plots : bool
        If True, generate and save plots.
    show_plots : bool
        If True, display plots interactively (requires GUI).
    """

    # Simulation parameters
    T_START = 0.0   # Start time (s)
    T_END = 3.0     # End time (s)
    DT = 0.01       # Time step (s)
    RTOL = 1e-5     # Relative tolerance

    # Load the FMU
    fmu_path = ("../../fmus/BouncingBall.fmu")

    if not os.path.exists(fmu_path):
        print(f"Error: FMU file not found at {fmu_path}")
        print("Please ensure 'BouncingBall.fmu' is in the same directory as this script.")
        return None, None

    print(f"Loading FMU from: {fmu_path}")

    try:
        bouncing_fmu = load_fmu(fmu_path)
    except Exception as e:
        print(f"Error loading FMU: {e}")
        return None, None

    print(f"Successfully loaded FMU: {bouncing_fmu.get_name()}")

    # Initialize the model
    try:
        bouncing_fmu.setup_experiment(start_time=T_START)
        bouncing_fmu.enter_initialization_mode()
        bouncing_fmu.exit_initialization_mode()
    except Exception as e:
        print(f"Error during initialization: {e}")
        return None, None

    # Event iteration at initialization
    eInfo = bouncing_fmu.get_event_info()
    eInfo.newDiscreteStatesNeeded = True

    while eInfo.newDiscreteStatesNeeded:
        bouncing_fmu.enter_event_mode()
        bouncing_fmu.event_update()
        eInfo = bouncing_fmu.get_event_info()

    bouncing_fmu.enter_continuous_time_mode()

    # Get initial states
    x = bouncing_fmu.continuous_states
    x_nominal = bouncing_fmu.nominal_continuous_states
    event_ind = bouncing_fmu.get_event_indicators()

    # Get value references for variables
    try:
        vref = [
            bouncing_fmu.get_variable_valueref("h"),
            bouncing_fmu.get_variable_valueref("v"),
        ]
    except Exception as e:
        print(f"Error getting variable references: {e}")
        return None, None

    # Initialize solution storage
    t_sol = [T_START]
    sol = [bouncing_fmu.get_real(vref)]

    # Main integration loop
    time = T_START
    T_next = T_END
    atol = 0.01 * RTOL * x_nominal

    print(f"Starting simulation from t={T_START}s to t={T_END}s...")

    step_count = 0

    while time < T_END and not bouncing_fmu.get_event_info().terminateSimulation:
        # Compute derivatives
        dx = bouncing_fmu.get_derivatives()

        # Determine step size
        h = min(DT, T_next - time)
        time = time + h

        bouncing_fmu.time = time

        # Integration step (Euler)
        x = x + h * dx
        bouncing_fmu.continuous_states = x

        # Event indicators
        event_ind_new = bouncing_fmu.get_event_indicators()

        step_event = bouncing_fmu.completed_integrator_step()
        time_event = abs(time - T_next) <= 1e-10
        state_event = any((event_ind_new > 0.0) != (event_ind > 0.0))

        if step_event or time_event or state_event:
            bouncing_fmu.enter_event_mode()
            eInfo = bouncing_fmu.get_event_info()
            eInfo.newDiscreteStatesNeeded = True

            while eInfo.newDiscreteStatesNeeded:
                bouncing_fmu.event_update(intermediateResult=True)
                eInfo = bouncing_fmu.get_event_info()

            if eInfo.valuesOfContinuousStatesChanged:
                x = bouncing_fmu.continuous_states

            if eInfo.nominalsOfContinuousStatesChanged:
                atol = 0.01 * RTOL * bouncing_fmu.nominal_continuous_states

            if eInfo.nextEventTimeDefined:
                T_next = min(eInfo.nextEventTime, T_END)
            else:
                T_next = T_END

            bouncing_fmu.enter_continuous_time_mode()

        event_ind = event_ind_new
        t_sol.append(time)
        sol.append(bouncing_fmu.get_real(vref))

        step_count += 1

    print(f"Simulation completed: {step_count} steps, {len(t_sol)} data points")

    sol_array = np.array(sol)
    t_sol_array = np.array(t_sol)

    print(f"Height range: [{sol_array[:, 0].min():.3f}, {sol_array[:, 0].max():.3f}] m")
    print(f"Velocity range: [{sol_array[:, 1].min():.3f}, {sol_array[:, 1].max():.3f}] m/s")

    # Plot results
    if with_plots:
        try:
            # Height
            plt.figure(figsize=(10, 6))
            plt.plot(t_sol_array, sol_array[:, 0], linewidth=2)
            plt.title(f"{bouncing_fmu.get_name()} - Height vs Time", fontsize=14)
            plt.ylabel("Height (m)", fontsize=12)
            plt.xlabel("Time (s)", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig("bouncing_height.png", dpi=150)
            print("✓ Saved: bouncing_height.png")

            # Velocity
            plt.figure(figsize=(10, 6))
            plt.plot(t_sol_array, sol_array[:, 1], linewidth=2)
            plt.title(f"{bouncing_fmu.get_name()} - Velocity vs Time", fontsize=14)
            plt.ylabel("Velocity (m/s)", fontsize=12)
            plt.xlabel("Time (s)", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig("bouncing_velocity.png", dpi=150)
            print("✓ Saved: bouncing_velocity.png")

            if show_plots:
                plt.show()

        except Exception as e:
            print(f"Error creating plots: {e}")
            import traceback
            traceback.print_exc()

    return t_sol_array, sol_array


def main():
    """Main entry point."""
    print("=" * 60)
    print("Bouncing Ball FMU Simulation")
    print("=" * 60)

    t_sol, sol = run_demo(with_plots=True, show_plots=True)

    print("\n" + "=" * 60)
    if t_sol is not None:
        print("Simulation completed successfully!")
    else:
        print("Simulation failed. Check the error messages above.")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
