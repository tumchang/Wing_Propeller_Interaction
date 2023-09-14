"""
============================================================================
This script the used for plot the carpet diagram of Propeller
J-Ct carpet diagram under different Beta70 values
Data from my_BEM_solver and XRotor

Reference Article: https://www3.nd.edu/~tcorke/w.WindTurbineCourse/Aerodynamics_Presentation.pdf
-------------
Author: Chang Xu   TUM   03739064  August.2023
Supervisor: Yiyuan Ma & Alexandros Lessis

Copyright @ Bauhaus Luftfahrt e.V
============================================================================
"""

# Module import
import os
import pandas as pd
import re
import matplotlib.pyplot as plt

directory_paths = ['./A&L', './Veldhuis']
# directory_paths = ['./A&L']
# directory_paths = ['./Veldhuis']
csv_files = []

for directory_path in directory_paths:
    csv_files.extend([os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.csv')])

dfs = {}  # This dictionary will store Beta70 value: dataframe pairs

for csv_file in csv_files:
    # Extract the Beta70 value using regex
    # match = re.search(r'Beta70=([\d.]+)', csv_file)
    # if match:
    #     beta_value = match.group(1)
    #     dfs[f'{beta_value}'] = pd.read_csv(os.path.join(csv_file))
    match = re.search(r'([A-Za-z&]+)Beta70=([\d.]+)', os.path.basename(csv_file))
    if match:
        beta_key = match.group(1) + "Beta70=" + match.group(2)
        dfs[beta_key] = pd.read_csv(csv_file)

# Colors and markers for each source #FF6347
source_styles = {
    'A&LResults': {'color': '#4C87D6', 'marker': 's'},
    'VeldhuisResults': {'color': '#F2B825', 'marker': 'o'},
    'XRotorResults': {'color': '#FF6347', 'marker': 'x'}
}

# Create a set to track which sources have been plotted
plotted_sources = set()
annotated_betas = set()

plt.figure(figsize=(12, 8))

# for beta_value, df in dfs.items():
#     for source, group_df in df.groupby('Source'):
#         # Add +/- 5% error lines for XRotor results
#         if source == 'XRotorResults':
#             y_values = group_df['Ct'].values
#             plt.plot(group_df['J'], y_values * 1.05, linestyle='--', color='g', alpha=0.5)
#             plt.plot(group_df['J'], y_values * 0.95, linestyle='--', color='g', alpha=0.5)

for beta_value, df in dfs.items():
    for source, group_df in df.groupby('Source'):
        # Only add to the legend if we haven't plotted this source before
        if source not in plotted_sources:
            plt.plot(group_df['J'], group_df['Ct'], label=source, **source_styles[source])
            plotted_sources.add(source)
        else:
            plt.plot(group_df['J'], group_df['Ct'], **source_styles[source])

    # Extract the numeric value of beta_70 for annotation
    match = re.search(r'Beta70=([\d.]+)', beta_value)
    if match:
        numeric_beta_value = match.group(1)
        # Add beta_70 annotation near the end of the line, only if we haven't annotated this beta_value before
        if numeric_beta_value not in annotated_betas:
            plt.text(group_df['J'].iloc[-1] - 0.1, group_df['Ct'].iloc[-1],
                     r'$\beta_{70}=$' + f'{numeric_beta_value}',
                     color='black', fontsize=12,
                     horizontalalignment='left', verticalalignment='bottom')
            annotated_betas.add(numeric_beta_value)

# Adding labels, title, and grid
plt.legend()

plt.xlim(2.0, 3.6)
plt.ylim(0.0, 0.3)

plt.tick_params(direction='in', length=6, width=0.5, which='both')

plt.xlabel('J')
plt.ylabel('Ct')
plt.title('J vs Ct for All Beta70 Values')
plt.grid(True)
plt.tight_layout()

plt.legend()

file_path = "./carpet_diagram.png"
plt.savefig(file_path, dpi=600)

plt.show()




print("Finished")
