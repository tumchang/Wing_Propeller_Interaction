"""
============================================================================
This script is used for plotting lift or other parameters distribution
on the wing under different rotor RPMs (for OPENVSP results)
-------------
Author: Chang Xu   TUM   03739064  July.2023
Supervisor: Yiyuan Ma & Alexandros Lessis

Copyright @ Bauhaus Luftfahrt e.V
============================================================================
"""

import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_main_wing(lod_data_list, rpm_values):
    # Create the plot
    fig, ax = plt.subplots()

    for i in range(len(lod_data_list)):
        rpm_data = lod_data_list[i]
        RPM_value = rpm_values[i]

        # Extract right and left wing data
        right_wing = rpm_data[rpm_data['WingID'] == 1]
        left_wing = rpm_data[rpm_data['WingID'] == 2]

        # Flip the left wing for plotting
        left_wing_flipped = left_wing.iloc[::-1]

        # Concatenate the flipped left wing and right wing data
        whole_wing = pd.concat([left_wing_flipped, right_wing])

        # Plot the data
        if i < len(lod_data_list) - 1:
            ax.plot(whole_wing['Yavg'], whole_wing['Clc_cref'], linestyle="-", marker="o", label=f"RPM {RPM_value}")
        else:
            ax.plot(whole_wing['Yavg'], whole_wing['Clc_cref'],
                    linestyle="-", marker="o", label=f"RPM {RPM_value} Unsteady")

    ax.set_title('Main Wing')
    ax.set_xlabel('Y [m]')
    ax.set_ylabel('Cl*c/Cref')
    ax.legend()
    ax.tick_params(axis="x", direction="in")
    ax.tick_params(axis="y", direction="in")
    ax.grid(True)
    plt.show()


# Import RPM data and create file paths
current_folder = os.getcwd()
model_name = "Do328_out"
RPM_values = [0, 800, 800]
RPM_data_list = []

for RPM in RPM_values:
    steady_file_path = os.path.join(current_folder, f"Steady/{model_name}", str(RPM), f"lod+{RPM}.csv")
    unsteady_file_path = os.path.join(current_folder, f"UnSteady/{model_name}", str(RPM), f"lod+{RPM}.csv")
    if not os.path.exists(steady_file_path):
        raise FileNotFoundError(f'\nSteady results of RPM {RPM} does not exist. \n'
                                f'Please run steady analysis first.')
    if RPM != 0:
        if not os.path.exists(unsteady_file_path):
            raise FileNotFoundError(f'\nUnsteady results of RPM {RPM} does not exist. \n'
                                    f'Please run unsteady analysis first.')

steady_0rpm_data = pd.read_csv(os.path.join(current_folder, f"Steady/{model_name}", str(0), f"lod+{0}.csv"))
steady_rpm_data = pd.read_csv(steady_file_path)
unsteady_rpm_data = pd.read_csv(os.path.join(current_folder, f"UnSteady/{model_name}", str(800), f"lod+{800}.csv"))

RPM_data_list.append(steady_0rpm_data)
RPM_data_list.append(steady_rpm_data)
RPM_data_list.append(unsteady_rpm_data)

# Call the function with the list of RPM data and RPM values
plot_main_wing(RPM_data_list, RPM_values)
