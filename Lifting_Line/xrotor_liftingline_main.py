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


"""
================================================================================================================
This section is used for specify file directory
and Analysis basic parameter setting
================================================================================================================
"""
# Specify the CPACS file to include engine Nacelle or not
nonac = True
prop_flag = False

# =============================================================================================================
# Specify all the file path and exe path
# =============================================================================================================
# Path to xfoil.exe file
xfoil_path = "./xfoil/xfoil.exe"
# CPACS Ref File
# if nonac:
#     cpacs_ref = "./Do328_nonac.xml"
# else:
#     cpacs_ref = "./Do328.xml"
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
    # Copy the polar file to xfoil folder
    shutil.move(f'./{airfoil_name}_polar.txt', './xfoil')

# Definition of propeller operating point
oper_point = OperPNT()
oper_point.beta_70 = 55.31
oper_point.rho = 1.225
oper_point.hub_radius = 0.376
oper_point.tip_radius = 1.88
# oper_point.RPM_list = list(range(700, 1001, 100))
oper_point.RPM_list = [800]
oper_point.Vinf = 142
oper_point.B = 6

"""
================================================================================================================
This section is used for Optimization process
================================================================================================================
"""


def xf_xr_lili(oper_pnt, cpacs_init, RPM, xdict):
    # L_D_list = []

    # for RPM in oper_pnt.RPM_list:
    """
    ================================================================================================================
    This section is used for Conducting the XRotor Analysis to get Slipstream data
    ================================================================================================================
    """
    # Set up the Propeller, using geometry data and operation points
    geom_data = geomdata(beta_70=oper_pnt.beta_70)

    # Initialize the Propeller Class
    propeller = Propeller(polar_dir, geom_data, oper_pnt, RPM)
    propeller.generate_prop_section()

    # Set up xrotor case
    xrotor_case = case(propeller)
    # Operate XRotor
    xr = operate_xrotor(xrotor_case, RPM=RPM)
    # Get the slipstream output
    slipstream = vput_xr(xr, RPM, print_flag=True)
    # Normalize the slipstream with Vinf
    slipstream_norm = slipstream_normalize(slipstream, xr)

    """
    ================================================================================================================
    This section is used for Conducting the Lifting Line Analysis
    ================================================================================================================
    """
    # Add the slipstream data to CPACS file
    xml_path = add_slipstream(cpacs_init, slipstream_norm,
                              RPM, prop_flag=prop_flag)
    print(xml_path)
    print("slipstream added")
    variable_change(xdict, xml_path)
    print("new variable for new opt iter added")

    # Run the Lifting Line.exe for conducting analysis
    xml_dir = run_lili(lili_path, xml_path)

    # Lifting Line results visualization
    CL, CD, total_coeff = lili_visualization(xml_dir, save_plot=False)

    # Lift = CL * ((2.21734905105455 + xdict["xvars"][0]) * (xdict["xvars"][2] - 3.66034288011383) / 2 + 4.914513)
    Drag = CD * ((2.21734905105455 + xdict["xvars"][0]) * (xdict["xvars"][2] - 3.66034288011383) / 2 + 4.914513)

    return Drag


if __name__ == '__main__':
    # xf_xr_lili(oper_point)
    print("finished")
