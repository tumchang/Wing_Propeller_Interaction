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
airfoil_name = 'CLARK_Y'
polar_dir = f'./xfoil/{airfoil_name}_polar.txt'
if not os.path.exists(polar_dir):
    xfoil_polar(xfoil_path, airfoil_name)
    # Copy the polar file to xfoil folder
    shutil.move(f'./{airfoil_name}_polar.txt', './xfoil')

"""
================================================================================================================
This section is used for Optimization process
================================================================================================================
"""


def xf_xr_lili(oper_pnt, cpacs_init, RPM, xdict, origin_wing, prop_flag, oper_pnt2, RPM2, opt_method):
    # for RPM in oper_pnt.RPM_list:
    """
    ================================================================================================================
    This section is used for Conducting the XRotor Analysis to get Slipstream data
    ================================================================================================================
    """
    # Set up the Propeller, using geometry data and operation points
    geom_data = geomdata(beta_70=oper_pnt.beta_70)

    # Initialize the Propeller Class
    propeller_1 = Propeller(polar_dir, geom_data, oper_pnt, RPM)
    propeller_1.generate_prop_section()
    propeller_2 = Propeller(polar_dir, geom_data, oper_pnt2, RPM2)
    propeller_2.generate_prop_section()

    # Set up xrotor case
    xrotor_case_1 = case(propeller_1, geom_data)
    xrotor_case_2 = case(propeller_2, geom_data)
    # Operate XRotor
    xr_1 = operate_xrotor(xrotor_case_1, RPM=RPM)
    xr_2 = operate_xrotor(xrotor_case_2, RPM=RPM2)
    # Get the slipstream output
    slipstream = vput_xr(xr_1, RPM, print_flag=True)
    slipstream_2 = vput_xr(xr_2, RPM, print_flag=True)
    # Normalize the slipstream with Vinf
    slipstream_norm = slipstream_normalize(slipstream, xr_1)
    slipstream_norm_2 = slipstream_normalize(slipstream_2, xr_1)
    combined_slipstream = {"slipstream_norm_1": slipstream_norm,
                           "slipstream_norm_2": slipstream_norm_2}

    """
    ================================================================================================================
    This section is used for Conducting the Lifting Line Analysis
    ================================================================================================================
    """
    # Add the slipstream data to CPACS file
    xml_path = add_slipstream(cpacs_init, combined_slipstream,
                              RPM, opt_method=opt_method, prop_flag=prop_flag)
    # xml_path = add_slipstream(cpacs_init, slipstream_norm,
    #                           RPM, prop_flag=prop_flag)
    print(xml_path)
    print("slipstream added")

    Cdo_wing = variable_change(xdict, xml_path, origin_wing.section, oper_pnt)
    print("new variable for new opt iter added")

    # Run the Lifting Line.exe for conducting analysis
    xml_dir = run_lili(lili_path, xml_path)

    # Lifting Line results visualization
    CL, CDi, total_coeff, eta_y = lili_visualization(xml_dir, save_plot=False)

    new_wing = WingShape(xml_path, eta_y, wing_method='Torenbeek')

    Lift = CL * new_wing.area
    Drag = (CDi + 3 * Cdo_wing) * new_wing.area

    L_D = Lift/Drag
    # Lift = CL * (
    #         ((origin_df['chord'][1] + xdict["chord3"]) * (xdict["half span"] - origin_df['tip_y'][1]) / 2)
    #         + ((origin_df['chord'][0] + origin_df['chord'][1]) * (origin_df['tip_y'][1] - origin_df['tip_y'][0]) / 2)
    # )
    # Drag = (CDi + Cdo) * (
    #         ((origin_df['chord'][1] + xdict["chord3"]) * (xdict["half span"] - origin_df['tip_y'][1]) / 2)
    #         + ((origin_df['chord'][0] + origin_df['chord'][1]) * (origin_df['tip_y'][1] - origin_df['tip_y'][0]) / 2)
    # )

    # Breguet Range Equation (at design operating points)
    # 600 g/kWh (two Engines)
    PSFC = 600/(1000*1000*3600)
    s = ((1 / (9.8*PSFC))
         * L_D *
         np.log(origin_wing.MTOW / (origin_wing.ZFW_no_wing + new_wing.wing_weight_est)))

    Obj = s

    return Obj, new_wing.wing_weight_est


if __name__ == '__main__':
    """
    ================================================================================================================
    This section is used for debugging and doing validation of the XF-XR-LILI workflow
    ================================================================================================================
    """
    pass
    # Definition of propeller operating point
    # oper_point = OperPNT()
    # # oper_point.beta_70 = 55.31
    # oper_point.rho = 0.52517
    # oper_point.hub_radius = 0.0236
    # oper_point.tip_radius = 0.236/2
    # # oper_point.RPM_list = list(range(700, 1001, 100))
    # # oper_point.RPM_list = [632.5, 674.66667, 722.857, 778.46, 843.33]
    # oper_point.RPM_list = [15254]
    # # [632.5, 778.46, 843.33]
    # oper_point.Vinf = 51  # Q = 1500 Pa = 0.5 * 1.225 * Vinf**2
    # oper_point.B = 4

    # cpacs_init = f'C:/Users/chang.xu/wing_propeller_interaction/prop_plate.xml'
    # # Set up the Propeller, using geometry data and operation points
    # geom_data = geomdata(beta_70=55.31)
    #
    # # Initialize the Propeller Class
    # propeller = Propeller(polar_dir, geom_data, oper_point, 800)
    # propeller.generate_prop_section()
    #
    # # Set up xrotor case
    # xrotor_case = case(propeller, geom_data)
    # # Operate XRotor
    # xr = operate_xrotor(xrotor_case, RPM=15254)
    # # Get the slipstream output
    # slipstream = vput_xr(xr, 15254, print_flag=True)
    # # Normalize the slipstream with Vinf
    # slipstream_norm = slipstream_normalize(slipstream, xr)
    #
    # # Add contraction & development factor consideration
    # slipstream_dev_coeff = calc_dev_coeff(oper_point, 0.201)
    # slipstream_norm_contracted = slipstream_norm.copy()
    # slipstream_norm_contracted[:, 1] = slipstream_norm_contracted[:, 1] * slipstream_dev_coeff/2
    #
    # # Add the slipstream data to CPACS file
    # xml_path = add_slipstream(cpacs_init, slipstream_norm_contracted,
    #                           15254, prop_flag=prop_flag)
    #
    # print("finished")
