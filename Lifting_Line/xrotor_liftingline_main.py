"""
============================================================================
This script is the workflow of conducting wing-propeller aerodynamic
interaction analysis using Xrotor and Lifting Line software

Xrotor: https://web.mit.edu/drela/Public/web/xrotor/
Lifting Line: https://www.dlr.de/as/en/desktopdefault.aspx/tabid-188/379_read-625/
-------------
Author: Chang Xu   TUM   03739064  August.2023
Supervisor: Yiyuan Ma & Alexandros Lessis

Copyright @ Bauhaus Luftfahrt e.V
============================================================================
"""

# Module import
from xrotor_lili_func import *
from xfoil.Xfoil import *
from Lifting_Line_Visualization import *

"""
================================================================================================================
This section is used for specify file directory
and Analysis basic parameter setting
================================================================================================================
"""
# Specify the CPACS file to include engine Nacelle or not
nonac = True
prop_flag = True

# =============================================================================================================
# Specify all the file path and exe path
# =============================================================================================================
# Path to xfoil.exe file
xfoil_path = "./xfoil/xfoil.exe"
# CPACS Ref File
if nonac:
    cpacs_ref = "./atr72-500_nonac.xml"
else:
    cpacs_ref = "./atr72-500.xml"
# Path to CPACS4LILI.exe
lili_path = "P:/LIFTING_LINE-master/LIFTING_LINE-master/CPACS4LILI.exe"

# =============================================================================================================
# Specify the operation conditions
# =============================================================================================================
# Airfoil to be used, generate airfoil polar data.txt
airfoil_name = '65-212'
polar_dir = f'./xfoil/{airfoil_name}_polar.txt'
if not os.path.exists(polar_dir):
    xfoil_polar(xfoil_path, airfoil_name)

# Definition of propeller operating point
beta_70 = 55.31
rho = 1.225
hub_radius = 0.376
tip_radius = 1.88
# RPM_list = list(range(700, 1001, 25))
RPM_list = [800]
Vinf = 142
B = 6


if __name__ == '__main__':

    for RPM in RPM_list:
        """
        ================================================================================================================
        This section is used for Conducting the XRotor Analysis to get Slipstream data
        ================================================================================================================
        """
        # Set up the Propeller, using geometry data and operation points
        geom_data = geomdata(beta_70=beta_70)

        # Initialize the Propeller Class
        propeller = Propeller(polar_dir, geom_data, rho, hub_radius, tip_radius, RPM, Vinf, B)
        propeller.generate_prop_section()

        # Set up xrotor case
        xrotor_case = case(beta_70, propeller)
        # Operate XRotor
        xr = operate_xrotor(xrotor_case, RPM=RPM)
        # Get the slipstream output
        slipstream = vput_xr(xr, RPM, print_flag=False)
        # Normalize the slipstream with Vinf
        slipstream_norm = slipstream_normalize(slipstream, xr)

        """
        ================================================================================================================
        This section is used for Conducting the Lifting Line Analysis
        ================================================================================================================
        """
        # Add the slipstream data to CPACS file
        xml_path = add_slipstream(cpacs_ref, slipstream_norm,
                                  RPM, prop_flag=prop_flag)

        # Run the Lifting Line.exe for conducting analysis
        xml_dir = run_lili(lili_path, xml_path)

        # Lifting Line results visualization
        lili_visualization(xml_dir, save_plot=True)

    print("finished")
