"""
============================================================================
This script the used for conducting BEM analysis to get
Propeller slipstream parameters

Reference Article: https://www3.nd.edu/~tcorke/w.WindTurbineCourse/Aerodynamics_Presentation.pdf
-------------
Author: Chang Xu   TUM   03739064  August.2023
Supervisor: Yiyuan Ma & Alexandros Lessis

Copyright @ Bauhaus Luftfahrt e.V
============================================================================
"""

# Module Import
from xrotor_lili_func import *
from xfoil.Xfoil import *


# Path to xfoil.exe file
xfoil_path = "./xfoil/xfoil.exe"

# =====================================================================================================================
# This Section is used for Airfoil Polar data preparation
# =====================================================================================================================
# Should the XRotor and BEM solver results saved to csv file to make a carpet diagram?
save_to_csv = False

# Airfoil to be used
airfoil_name = 'CLARK_Y'
polar_dir = f'./xfoil/{airfoil_name}_polar.txt'
if not os.path.exists(polar_dir):
    xfoil_polar(xfoil_path, airfoil_name)
else:
    pass

# =====================================================================================================================
# This Section is used for defining the operating and geometry parameters of the Propeller
# =====================================================================================================================
beta_70 = 55.31
# geom_data = geomdata(beta_70=beta_70)
geom_data = validation_geomdata_58689()

# tip_loss_model = 'A&L'
tip_loss_model = 'Veldhuis'
# tip_loss_model = 'Prandtl'

oper_point = OperPNT()
oper_point.beta_70 = 55.31
oper_point.rho = 1.225
oper_point.hub_radius = 0.0236
oper_point.tip_radius = 0.236/2
# oper_point.RPM_list = list(range(700, 1001, 100))
# oper_point.RPM_list = [632.5, 674.66667, 722.857, 778.46, 843.33]
oper_point.RPM_list = [15376]
# [632.5, 778.46, 843.33]
oper_point.Vinf = 51.4096
oper_point.B = 4

# oper_point = OperPNT()
# oper_point.beta_70 = 55.31
# oper_point.rho = 1.225
# oper_point.hub_radius = 0.376
# oper_point.tip_radius = 1.88
# # oper_point.RPM_list = list(range(700, 1001, 100))
# # oper_point.RPM_list = [632.5, 674.66667, 722.857, 778.46, 843.33]
# oper_point.RPM_list = [800]
# # [632.5, 778.46, 843.33]
# oper_point.Vinf = 142
# oper_point.B = 6

# propeller = Propeller(polar_dir, geom_data, rho, hub_radius, tip_radius, RPM, Vinf, B)

# cl_cdmin = propeller.airfoil_polar.get_cl_at_cdmin()
# dCddCL2 = propeller.airfoil_polar.get_dCDdCL2()

# Pre-allocate the results
# xrotor results
xrotor_thrust_list = []
xrotor_Ct_list = []
xrotor_Cp_list = []
xrotor_thrust_post = []

# My bem Solver results
my_thrust_list = []
my_Ct_list = []
my_Cp_list = []
J_list = []

# history results
a_history_list = []
cl_history_list = []
cd_history_list = []

# convergence results
convergence_his = []

for RPM in oper_point.RPM_list:
    propeller = Propeller(polar_dir, geom_data, oper_point, RPM)

    propeller.generate_prop_section()

    # =====================================================================================================================
    # This section is used to conduct Xrotor analysis for comparison
    # =====================================================================================================================
    xrotor_case = case(propeller)
    # xrotor_case = case(airfoil_polars, propeller)
    xr = operate_xrotor(xrotor_case, RPM=RPM)

    xrotor_thrust_list.append(xr.performance.thrust)

    xrotor_Ct_list.append(
        xr.performance.thrust / (propeller.rho * (propeller.n ** 2) * ((propeller.tip_radius * 2) ** 4))
    )
    xrotor_Cp_list.append(
        xr.performance.power / (propeller.rho * (propeller.n ** 3) * ((propeller.tip_radius * 2) ** 5))
    )

    thrust_xr_post = xr_postprocess(xr)
    xrotor_thrust_post.append(thrust_xr_post)

    # xr.save_propeller_geometry()
    # xr.load_propeller_geometry('output.json')

    # =====================================================================================================================
    # This section is used for Conducting the BEM analysis
    # =====================================================================================================================
    a_old = np.zeros(len(geom_data))
    a_prime_old = np.zeros(len(geom_data))

    max_iterations = 200
    iteration = 0
    converged = False

    # if not converged:
    #     raise ValueError("BEM solver not converged, program terminated")
    # else:
    #     pass

    # Main loop of BEM analysis
    while not converged and iteration < max_iterations:
        a_new, a_prime_new, Cl, Cd, F = a_loop(a_old, a_prime_old,
                                               propeller, geom_data,
                                               loss_model=tip_loss_model)

        # Check convergence for both a and a_prime
        if convergence_check(a_old, a_new) and convergence_check(a_prime_old, a_prime_new):
            converged = True
        else:
            # Store history results
            a_history_list.append(list(a_old))
            cl_history_list.append(list(Cl))
            cd_history_list.append(list(Cd))

            # Update for next iteration
            a_old = a_new.copy()
            a_prime_old = a_prime_new.copy()
            iteration = iteration + 1

    a_history_array = np.asarray(a_history_list)
    cl_history_array = np.asarray(cl_history_list)
    cd_history_array = np.asarray(cd_history_list)

    # Insert Main loop Results
    propeller.Result_BEM.a = a_new
    propeller.Result_BEM.a_prime = a_prime_new
    propeller.Result_BEM.Cl = Cl
    propeller.Result_BEM.Cd = Cd
    propeller.Result_BEM.F = F

    # Getting CT and CP based on BEM results
    my_thrust, my_Ct, my_Cp = propeller.calculate_thrust()

    J_list.append(oper_point.Vinf / ((RPM / 60) * (2 * oper_point.tip_radius)))
    my_thrust_list.append(my_thrust)
    my_Ct_list.append(my_Ct)
    my_Cp_list.append(my_Cp)

    # History results plot
    convergence_his.append(converged)
    # cl_history_plot(cl_history_array)
    # cd_history_plot(cd_history_array)
    # a_history_plot(a_history_array)

    # CL comparison between xrotor and my solver
    r_cl_plot(propeller.geometry.r, Cl, xr)
    # r_cd_plot(propeller.geometry.r, Cd, xr)

# =====================================================================================================================
# This section is used for saving results to a dataframe
# =====================================================================================================================
my_df = pd.DataFrame({'J': J_list,
                      'Thrust': my_thrust_list,
                      'Ct': my_Ct_list,
                      'Cp': my_Cp_list})

x_rotor_df = pd.DataFrame({'J': J_list,
                           'Thrust': xrotor_thrust_list,
                           'Ct': xrotor_Ct_list,
                           'Cp': xrotor_Cp_list})

my_df['Source'] = f'{tip_loss_model}Results'
x_rotor_df['Source'] = 'XRotorResults'

if save_to_csv:
    # Concatenate the DataFrames vertically
    combined_df = pd.concat([my_df, x_rotor_df], axis=0)

    # Save to CSV
    combined_df.to_csv(f'./bem_solver/{tip_loss_model}'
                       f'/{tip_loss_model}Beta70={beta_70}.csv', index=False)
else:
    pass

# =====================================================================================================================
# This section is used for plotting Cl, Cd against r/R and compare them with XRotor Results
# =====================================================================================================================
# r_cl_plot(propeller.geometry.r, Cl, xr)

# Plot the J-Ct diagram
J_Ct_plot(x_rotor_df, my_df)
J_Cp_plot(x_rotor_df, my_df)

# Slip Stream plot
va_vt_plot_xr(xr)
va_vt_plot_bem(propeller)

plt.show()

print("Finish")
