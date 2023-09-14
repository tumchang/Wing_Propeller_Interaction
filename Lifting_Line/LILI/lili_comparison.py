"""
============================================================================
This script is used for comparing the Cl or Lift distribution
of different LILI analysis results

Lifting Line: https://www.dlr.de/as/en/desktopdefault.aspx/tabid-188/379_read-625/
-------------
Author: Chang Xu   TUM   03739064  Sep.2023
Supervisor: Yiyuan Ma & Alexandros Lessis

Copyright @ Bauhaus Luftfahrt e.V
============================================================================
"""

import pandas as pd
import matplotlib.pyplot as plt


# Specify the folder first
dir1 = './atr72-500_out/propFalse_RPM0/'
dir2 = './atr72-500_out/propTrue_RPM800/'
vsp_res_dir = fr'C:\Users\chang.xu\wing_propeller_interaction\VSP\Steady\atr72-500_out\800/'

df1_path = dir1 + 'cl_dist.csv'
df2_path = dir2 + 'cl_dist.csv'
vsp_res_path = vsp_res_dir + 'yavg_cl_data3.csv'

df1 = pd.read_csv(df1_path)
df2 = pd.read_csv(df2_path)
df3 = pd.read_csv(vsp_res_path)

fig = plt.figure(figsize=(10, 10))

plt.plot(df1['Y'], df1['Cl'], '-x', label='No Prop')
plt.plot(df2['Y'], df2['Cl'], '-o', label='RPM=800 XRotor')
plt.plot(df3['Yavg'], df3['Cl'], 'o', label='RPM=800 VSP Actuator Disk')

plt.xlabel('Y')
plt.ylabel('Cl')
plt.title('Cl distribution')
plt.grid(True)

plt.xlim(-15, 15)
plt.ylim(0.0, 0.7)

plt.legend()

file_path = "./LILI_VSP_800.png"
plt.savefig(file_path, dpi=600)

plt.show()

print('finished')
