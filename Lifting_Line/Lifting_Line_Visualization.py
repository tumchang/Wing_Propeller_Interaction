"""
============================================================================
This script is a Visualization tool set for plotting
LIFTING_LINE Software results
-------------
Author: Chang Xu   TUM   03739064  August.2023
Supervisor: Yiyuan Ma & Alexandros Lessis

Copyright @ Bauhaus Luftfahrt e.V
============================================================================
"""


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.interpolate import griddata


class TecGeomSec:
    def __init__(self):
        self.Zone_T = None
        self.N = None
        self.E = None
        self.ET = None
        self.F = None
        self.XYZ = []

    @staticmethod
    def from_string(section_str):
        instance = TecGeomSec()
        lines = section_str.strip().split("\n")

        # Parse ZONE line
        zone_line = lines[0]
        parts = zone_line.split(",")
        for part in parts:
            key, val = part.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"')  # Remove leading/trailing whitespaces and quotes

            if key == "ZONE T":
                instance.Zone_T = val
            elif key == "N":
                instance.N = int(val)
            elif key == "E":
                instance.E = int(val)
            elif key == "ET":
                instance.ET = val
            elif key == "F":
                instance.F = val

        # Parse XYZ data
        for line in lines[1: instance.N + 1]:
            coords = [float(val) for val in line.split()]
            if len(coords) == 3:
                instance.XYZ.append(coords)

        instance.XYZ = np.array(instance.XYZ)
        return instance


"""
===================================================================================================================
This section are the codes for parsing the *.plt files from the LIFTING_LINE calculation results
===================================================================================================================
"""


def parse_attributes(tecplot_dir, name):
    # geom_file = tecplot_dir + '/aircraft_geometry.plt'
    geom_file = tecplot_dir + f'/{name}_geometry.plt'

    with open(geom_file, 'r') as file:
        content = file.read()

    # Split the content into sections
    sections = content.split("ZONE")[1:]  # Excluding any content before the first ZONE
    sections = ["ZONE" + section for section in sections]  # Add "ZONE" back to each section

    # Convert each section string to a TecGeomSec instance
    geom_secs = [TecGeomSec.from_string(section) for section in sections]
    return geom_secs


def parse_distribution(tecplot_dir, name, parse_total=False):
    # distribution_file = tecplot_dir + "/aircraft_distribution.plt"
    distribution_file = tecplot_dir + f'/{name}_distribution.plt'
    if parse_total:
        distribution_file = tecplot_dir + f'/{name}_total.plt'

    # Lists to store columns and data
    columns = []
    data = []

    # Flags to know the current parsing status
    is_reading_columns = False
    is_reading_data = False

    with open(distribution_file, 'r') as f:
        for line in f:
            line = line.strip()

            # If it's the start of the VARIABLES section
            if line.startswith("VARIABLES"):
                is_reading_columns = True
                columns.append(line.split('=')[1].replace('"', '').replace(',', '').strip())
                continue

            # If it's still the VARIABLES section
            if is_reading_columns and ('"' in line):
                columns.append(line.replace('"', '').replace(',', '').strip())
                continue

            # End of VARIABLES section
            if is_reading_columns and not ('"' in line):
                is_reading_columns = False

            # Start of data after ZONE line
            if line.startswith("ZONE"):
                is_reading_data = True
                continue

            # Read the data rows
            if is_reading_data:
                values = [float(val) for val in line.split()]
                data.append(values)

    columns.pop(0)

    # Convert list to DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Create a boolean mask for NaN rows (NaN rows are marked as True, other rows are marked as False)
    mask = df.isna().all(axis=1)

    # Calculate the difference and then cumsum
    groups = mask.diff().ne(0).cumsum()

    # Start by creating an empty dictionary
    df_dict = {}

    # Enumerate over the groups created by the groupby method
    for i, (name, group) in enumerate(df.groupby(groups)):

        # Check if the current group doesn't consist entirely of NaN rows
        if not group.isna().all(axis=1).any():
            # Create a key for the current group
            key = f"df_{int(i / 2)}"

            # Store the group in the dictionary using the created key
            df_dict[key] = group

    # Drop all NaN lines in Dataframe
    df = df.dropna()

    return df, df_dict,


def parse_total_dist(total_dist_dir):
    # 1. Extract Variable Names
    variables = []
    with open(total_dist_dir + "/CPACS4LILI_Distribution.plt", "r") as file:
        lines = file.readlines()
        start_idx = next(i for i, line in enumerate(lines) if "VARIABLES" in line)
        end_idx = next(i for i, line in enumerate(lines[start_idx:]) if "ZONE" in line) + start_idx
        for line in lines[start_idx:end_idx]:
            variables.extend(line.strip().split("=")[-1].split(","))
    variables = [var.replace('"', '').strip() for var in variables if var.strip()]

    # 2. Extract Data Sections
    sections = []
    current_section = []
    in_data_section = False
    with open(total_dist_dir + "/CPACS4LILI_Distribution.plt", "r") as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line.startswith("ZONE"):
                in_data_section = True
                if current_section:
                    sections.append(current_section)
                    current_section = []
                continue
            if in_data_section and stripped_line and not any(
                    keyword in stripped_line for keyword in ["ZONE", "T", "I", "DATAPACKING", "ZONETYPE", "AUXDATA"]):
                current_section.append(stripped_line)
        if current_section:
            sections.append(current_section)

    # 3. Create DataFrames
    dfs = [pd.DataFrame([list(map(float, row.split())) for row in section], columns=variables) for section in sections
           if section]

    return dfs


"""
===================================================================================================================
This section are the codes for plotting the *.plt files from the LIFTING_LINE calculation results
===================================================================================================================
"""


def plot_distribution(distribution_dic, variable, num_plot):
    fig = plt.figure(figsize=(16, 16))
    ax = fig.add_subplot(111, projection='3d')

    # List comprehension to extract the dataframes
    X_df = [distribution_dic[f'df_{i}']["X"] for i in range(num_plot)]
    Y_df = [distribution_dic[f'df_{i}']["Y"] for i in range(num_plot)]
    var_df = [distribution_dic[f'df_{i}'][variable] for i in range(num_plot)]

    # Use pd.concat to stack them vertically
    X = pd.concat(X_df, axis=0, ignore_index=True)
    Y = pd.concat(Y_df, axis=0, ignore_index=True)
    Z = pd.concat(var_df, axis=0, ignore_index=True)

    # scatter = ax.scatter(X, Y, Z, c=distribution_df[variable], cmap='viridis', s=50)
    # plt.colorbar(scatter, ax=ax, label='CFY Value')

    xi = np.linspace(min(X), max(X), 1000)
    yi = np.linspace(min(Y), max(Y), 1000)
    xi, yi = np.meshgrid(xi, yi)

    # Interpolate
    zi = griddata((X, Y), Z, (xi, yi), method='linear')

    surf = ax.plot_surface(xi, yi, zi, cmap='viridis')
    plt.colorbar(surf, ax=ax, label='CFZ Value')

    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('CFY Value')
    ax.set_title('3D Scatter plot of CFZ')

    # ax.legend()
    # ax.set_xlim(10, 25)
    # ax.set_ylim(0, 20)
    # ax.set_zlim(0, 2)
    #
    # ax.set_box_aspect([0.75, 1, 0.1])


def plot_geom_secs(geom_secs, num_plot, panel_plot=1):

    fig = plt.figure(figsize=(16, 16))
    ax = fig.add_subplot(111, projection='3d')

    # TODO: You can change the surfurce that you want to plot here
    for i in range(num_plot):
        # Unpack XYZ data
        X = geom_secs[i].XYZ[:, 0]
        Y = geom_secs[i].XYZ[:, 1]
        Z = geom_secs[i].XYZ[:, 2]
        ax.scatter(X, Y, Z, label=geom_secs[i].Zone_T)

        if panel_plot == 1:
            # Collect panels
            panels = []
            for j in range(0, geom_secs[i].N, 4):
                panel = [[X[j], Y[j], Z[j]],
                         [X[j + 1], Y[j + 1], Z[j + 1]],
                         [X[j + 2], Y[j + 2], Z[j + 2]],
                         [X[j + 3], Y[j + 3], Z[j + 3]]]
                panels.append(panel)

            # Plotting panels
            poly3d = Poly3DCollection(panels, facecolors='cyan', linewidths=1, edgecolors='k', alpha=0.5)
            ax.add_collection3d(poly3d)
        else:
            pass

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # ax.legend()
    ax.set_xlim(10, 40)
    ax.set_ylim(-20, 20)
    ax.set_zlim(-4, 4)

    ax.set_box_aspect([0.75, 1, 0.2])


def panel_dist_plot(distribution_dic, variable,
                    geom_secs, num_plot, mesh_flag=True):

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # List comprehension to extract the dataframes
    X_df = [distribution_dic[f'df_{i}']["X"] for i in range(num_plot)]
    Y_df = [distribution_dic[f'df_{i}']["Y"] for i in range(num_plot)]
    var_df = [distribution_dic[f'df_{i}'][variable] for i in range(num_plot)]

    # Use pd.concat to stack them vertically
    X = pd.concat(X_df, axis=0, ignore_index=True)
    Y = pd.concat(Y_df, axis=0, ignore_index=True)
    Z = pd.concat(var_df, axis=0, ignore_index=True)

    xi = np.linspace(min(X), max(X), 116)
    yi = np.linspace(min(Y), max(Y), 116)
    xi, yi = np.meshgrid(xi, yi)

    # Interpolate
    zi = griddata((X, Y), Z, (xi, yi), method='linear')

    if mesh_flag:
        surf = ax.plot_surface(xi, yi, zi*10, cmap='viridis')
        plt.colorbar(surf, ax=ax, label='CFY Value (scaled by 10)')

    # TODO: Change the panel number to be plotted
    for i in range(40):
        # Unpack XYZ data
        X = geom_secs[i].XYZ[:, 0]
        Y = geom_secs[i].XYZ[:, 1]
        Z = geom_secs[i].XYZ[:, 2]
        ax.scatter(X, Y, Z, label=geom_secs[i].Zone_T)

        # Collect panels
        panels = []
        for j in range(0, geom_secs[i].N, 4):
            panel = [[X[j], Y[j], Z[j]],
                     [X[j + 1], Y[j + 1], Z[j + 1]],
                     [X[j + 2], Y[j + 2], Z[j + 2]],
                     [X[j + 3], Y[j + 3], Z[j + 3]]]
            panels.append(panel)

        # Plotting panels
        poly3d = Poly3DCollection(panels, facecolors='cyan', linewidths=1, edgecolors='k', alpha=0.5)
        ax.add_collection3d(poly3d)

    ax.set_xlim(10, 15)
    ax.set_ylim(-15, 15)
    ax.set_zlim(-4, 4)

    ax.set_box_aspect([5/30, 1, 8/30])

    # elevation_angle = 30  # for example
    # azimuthal_angle = -135  # for example
    # ax.view_init(elev=elevation_angle, azim=azimuthal_angle)

    return fig


def cl_distribution_2d(distribution_dic):
    Y = np.asarray(distribution_dic[0].Y)
    cl = np.asarray(distribution_dic[0].CL)

    fig = plt.figure(figsize=(8, 6))

    plt.plot(Y, cl, '-o')

    plt.xlabel('Y')
    plt.ylabel('Cl')
    plt.title('Cl distribution')

    # plt.ylim(0.0, 0.8)

    plt.grid(True)

    # Save to DataFrame
    df = pd.DataFrame({'Y': Y, 'Cl': cl})

    return fig, df


def lift_distribution_2d(distribution_dic):
    Y = np.asarray(distribution_dic[0].Y)
    cl = np.asarray(distribution_dic[0].CL)
    area = np.asarray(distribution_dic[0].RefArea)

    Fz = cl * area

    fig = plt.figure(figsize=(8, 6))

    plt.plot(Y, Fz, '-o')

    plt.xlabel('Y')
    plt.ylabel('Fz')
    plt.title('Lift distribution')

    # plt.ylim(0.0, 0.8)

    plt.grid(True)

    # Save to DataFrame
    df = pd.DataFrame({'Y': Y, 'Fz': Fz})

    return fig, df


if __name__ == '__main__':
    aircraft_name = "CPACS4LILI_LILI-Config_1"

    # Tecplot directory
    # tecplot_dir = f"./aircraft.lili.V3.1/export/tecplot"

    # tecplot_dir = fr".\LILI\atr72\chord0\CPACS4LILI_LILI-Config_1.lili.V3.1\export\tecplot"
    # tecplot_dir = fr".\LILI\atr72\nofuse\CPACS4LILI_LILI-Config_1.lili.V3.1\export\tecplot"

    # tecplot_dir = f"./PROPELLER_COMPLEX/export/tecplot"
    # tecplot_dir = fr"P:\LIFTING_LINE-master\LIFTING_LINE-master\ReturnDirectory\CPACS4LILI_LILI-Config_1.lili.V3.1\export\tecplot"
    tecplot_dir = fr"C:\Users\chang.xu\wing_propeller_interaction\Lifting_Line\ReturnDirectory\CPACS4LILI_LILI-Config_1.lili.V3.1\export\tecplot"
    # tecplot_dir = fr"C:\Users\chang.xu\wing_propeller_interaction\Lifting_Line\{aircraft_name}.lili.V3.1\export\tecplot"

    # Execute the function to parse the data and plot as figures
    geom_secs = parse_attributes(tecplot_dir, aircraft_name)
    distribution, distribution_dict = parse_distribution(tecplot_dir, aircraft_name)

    # num_plot = 10

    # plot_geom_secs(geom_secs, 50)
    # plot_distribution(distribution_dict, "CFZ", 9)
    panel_dist_plot(distribution_dict, "CFZ", geom_secs, 3)

    cl_distribution_2d(distribution_dict)
    lift_distribution_2d(distribution_dict)

    # Show all the figures
    plt.show()

    print("finished")
