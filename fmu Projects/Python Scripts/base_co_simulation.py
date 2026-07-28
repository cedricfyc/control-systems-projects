from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
from fmpy.util import plot_result

import numpy as np
import shutil


def simulate_co_simulation_fmu(
        fmu_path,
        start_time=0.0,
        stop_time=None,
        step_size=None,
        parameter_values=None,
        input_function=None,
        show_plot=True):

    """
    Generic FMI 2.0 Co-Simulation simulator.

    Parameters
    ----------
    fmu_path : str
        Path to FMU.

    start_time : float

    stop_time : float or None

    step_size : float or None

    parameter_values : dict
        Example:
        {
            "p": 5.0
        }

    input_function : callable

        Function:

            values = input_function(time)

        Returns dictionary:

            {
                "Base": 2.0
            }

    show_plot : bool
    """

    parameter_values = parameter_values or {}

    md = read_model_description(fmu_path)

    if stop_time is None:
        if md.defaultExperiment is not None and md.defaultExperiment.stopTime is not None:
            stop_time = md.defaultExperiment.stopTime
        else:
            stop_time = 1.0

    if step_size is None:
        if md.defaultExperiment is not None and md.defaultExperiment.stepSize is not None:
            step_size = md.defaultExperiment.stepSize
        else:
            step_size = 1e-2

    unzipdir = extract(fmu_path)

    fmu = FMU2Slave(
        guid=md.guid,
        unzipDirectory=unzipdir,
        modelIdentifier=md.coSimulation.modelIdentifier,
        instanceName="instance1"
    )

    input_vars = [v for v in md.modelVariables if v.causality == "input"]
    output_vars = [v for v in md.modelVariables if v.causality == "output"]
    parameter_vars = [v for v in md.modelVariables if v.causality == "parameter"]

    fmu.instantiate()

    fmu.setupExperiment(
        startTime=start_time,
        stopTime=stop_time
    )

    fmu.enterInitializationMode()

    # ------------------------------------------------------
    # Set parameter values
    # ------------------------------------------------------

    for var in parameter_vars:

        if var.name not in parameter_values:
            continue

        value = parameter_values[var.name]

        if var.type == "Real":
            fmu.setReal([var.valueReference], [float(value)])

        elif var.type == "Integer":
            fmu.setInteger([var.valueReference], [int(value)])

        elif var.type == "Boolean":
            fmu.setBoolean([var.valueReference], [bool(value)])

        elif var.type == "String":
            fmu.setString([var.valueReference], [str(value)])

    fmu.exitInitializationMode()

    names = ["time"] + [v.name for v in input_vars] + [v.name for v in output_vars]

    rows = []

    current_time = start_time

    while current_time <= stop_time:

        # -----------------------------
        # Set inputs
        # -----------------------------

        if input_function is not None:

            values = input_function(current_time)

            for var in input_vars:

                if var.name not in values:
                    continue

                value = values[var.name]

                if var.type == "Real":
                    fmu.setReal([var.valueReference], [float(value)])

                elif var.type == "Integer":
                    fmu.setInteger([var.valueReference], [int(value)])

                elif var.type == "Boolean":
                    fmu.setBoolean([var.valueReference], [bool(value)])

                elif var.type == "String":
                    fmu.setString([var.valueReference], [str(value)])

        fmu.doStep(
            currentCommunicationPoint=current_time,
            communicationStepSize=step_size
        )

        current_time += step_size

        # Start a row of data
        row = [current_time]

        # Record inputs
        for var in input_vars:
        
            if var.type == "Real":
                # Read value of input based on its value reference as index
                input_value = fmu.getReal([var.valueReference])[0]

            elif var.type == "Integer":
                input_value = fmu.getInteger([var.valueReference])[0]

            elif var.type == "Boolean":
                input_value = fmu.getBoolean([var.valueReference])[0]

            elif var.type == "String":
                input_value = fmu.getString([var.valueReference])[0]

            else:
                input_value = None

            row.append(input_value)

        # Record outputs
        for var in output_vars:

            if var.type == "Real":
                output_value = fmu.getReal([var.valueReference])[0]

            elif var.type == "Integer":
                output_value = fmu.getInteger([var.valueReference])[0]

            elif var.type == "Boolean":
                output_value = fmu.getBoolean([var.valueReference])[0]

            elif var.type == "String":
                output_value = fmu.getString([var.valueReference])[0]

            else:
                output_value = None

            row.append(output_value)

        rows.append(tuple(row))

    fmu.terminate()
    fmu.freeInstance()

    shutil.rmtree(unzipdir, ignore_errors=True)

    dtype = [(name, np.float64) for name in names]

    result = np.array(rows, dtype=dtype)

    if show_plot:
        plot_result(result)

    return result


# ---------------------------------------------------------
# Example usage for your Power FMU
# ---------------------------------------------------------

def power_input(current_time):
    return {
        "Base": 3.0 if current_time > 1.0 else 1.0
    }


if __name__ == "__main__":

    simulation_result = simulate_co_simulation_fmu(
        fmu_path="../fmus/power_fmu_test.fmu",
        start_time=0,
        stop_time=10,
        parameter_values={
            "p": 5
        },
        input_function=power_input,
        show_plot=True
    )

    print(simulation_result)