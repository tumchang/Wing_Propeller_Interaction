"""
============================================================================
This script is a automation of OpenVSP software analysis
using Python API
-------------
Author: Chang Xu   TUM   03739064  July.2023
Supervisor: Yiyuan Ma & Alexandros Lessis

Copyright @ Bauhaus Luftfahrt e.V
============================================================================
"""


# Module Import
from cpacs_vsp_wrapper import *
from Functions import *

# Clear and reinitialize OpenVSP to all default settings
vsp.VSPCheckSetup()
vsp.VSPRenew()
vsp.ClearVSPModel()
vsp.DeleteAllResults()

"""
------------------------------------------------------------
Analysis Method and VSPAero Parameter setting
------------------------------------------------------------
"""
# if test flag == 1 means that we are only generating the vsp model file for examination
test_flag = 0
cfd_analysis = 0

# Setting of Analysis method(Unsteady of steady)
Unsteady_Flag = 0
RPM = 800

# Setting of VSPAero analysis input parameters
recref = [500000]
# vref = [50]
vinf = [50]
rho = [1.225]
alpha = [3.0]
Mach = [0.6]
Wake = [5]
Wakenodes = [128]
n_cpu = [8]
Ref_flag = [2]
# numtimesteps = [120]
# timestepsizes = [0.00042]
auto_time_flag = [1]
num_rev_flag = [2]

# cpacs = CPACS(fr"C:\Users\chang.xu\wing_propeller_interaction\D150.xml")
# cpacs = CPACS(fr"C:\Users\chang.xu\wing_propeller_interaction\atr72-500_out.xml")
cpacs = CPACS(fr"C:\Users\chang.xu\wing_propeller_interaction\Do328_out.xml")
# cpacs = CPACS(fr"C:\Users\chang.xu\wing_propeller_interaction\FLIPASED01.xml")
vsp_model = VSP(cpacs)

# ==================================================================================
#     Geometry: Generate VSP3 Model file from Parameters Defined
# ==================================================================================

vsp_model.generate_vsp_model(test_flag=test_flag, unsteady_flag=Unsteady_Flag, rpm=RPM)

vsp.Update()

vsp_output_case_dir = save_vsp3_file(test_flag=test_flag, Unsteady_Flag=Unsteady_Flag, vsp_model=vsp_model, RPM=RPM)

# ==================================================================================
#     Analysis: VSPAero Compute Geometry to Create Vortex Lattice DegenGeom File
# ==================================================================================
compgeom_name = "VSPAEROComputeGeometry"

# analysis_method = vsp.GetIntAnalysisInput(compgeom_name, "AnalysisMethod")
analysis_method = [vsp.VORTEX_LATTICE]
vsp.SetIntAnalysisInput(compgeom_name, "AnalysisMethod", analysis_method, 0)

vsp.PrintAnalysisInputs(compgeom_name)

print("Executing...")
compgeom_resid = vsp.ExecAnalysis(compgeom_name)
print("DegenGeom COMPLETE")

# ==================================================================================
#     Analysis: VSPAero Compute Geometry to Create Vortex Lattice DegenGeom File
# ==================================================================================
if cfd_analysis == 1:
    save_cfd_mesh(vsp_model, vsp_output_case_dir)
    su2_mesh_generation(vsp_model, vsp_output_case_dir)
    su2_analysis(vsp_model, vsp_output_case_dir)
else:
    pass

# ==================================================================================
#                           VSPAERO Analysis Input
# ==================================================================================
# VSPAEROSinglePoint
analysis_name = "VSPAEROSinglePoint"

# Use rotating blades analysis or Actuator disk analysis
if RPM == 0:
    pass
else:
    if Unsteady_Flag == 1:
        vsp.SetIntAnalysisInput(analysis_name, "RotateBladesFlag", [1], 0)   # Rotating Blades
    else:
        vsp.SetIntAnalysisInput(analysis_name, "ActuatorDiskFlag", [1], 0)     # Actuator Disk


# Setting Analysis Input for VSPAero
vsp.SetIntAnalysisInput(analysis_name, "RefFlag", Ref_flag, 0)
vsp.SetDoubleAnalysisInput(analysis_name, "ReCref", recref, 0)
# vsp.SetDoubleAnalysisInput(analysis_name, "Vref", vref, 0)
vsp.SetDoubleAnalysisInput(analysis_name, "Vinf", vinf, 0)
vsp.SetDoubleAnalysisInput(analysis_name, "Rho", rho, 0)
vsp.SetDoubleAnalysisInput(analysis_name, "Alpha", alpha, 0)
vsp.SetDoubleAnalysisInput(analysis_name, "Mach", Mach, 0)
vsp.SetIntAnalysisInput(analysis_name, "WakeNumIter", Wake, 0)
vsp.SetIntAnalysisInput(analysis_name, "NumWakeNodes", Wakenodes, 0)
# vsp.SetDoubleAnalysisInput(analysis_name, "NumTimeSteps", numtimesteps, 0)
# vsp.SetDoubleAnalysisInput(analysis_name, "TimeStepSize", timestepsizes, 0)
vsp.SetIntAnalysisInput(analysis_name, "NCPU", n_cpu, 0)

# Time setting and Number of Revolution Setting
if Unsteady_Flag == 1:
    vsp.SetIntAnalysisInput(analysis_name, "AutoTimeStepFlag", auto_time_flag, 0)
    vsp.SetIntAnalysisInput(analysis_name, "AutoTimeNumRevs", num_rev_flag, 0)
else:
    pass

vsp.Update()

print('--> All Analysis Inputs')
vsp.PrintAnalysisInputs(analysis_name)

print("--> Start VSPAero Analysis")
results_id = vsp.ExecAnalysis(analysis_name)
print("--> VSPAero Analysis Finished")

# ==================================================================================
#                           Print Results and Plots
# ==================================================================================

# Open abd results file with VSPViewer and wait until close
vsp_viewer = subprocess.Popen(
    [
        r"P:\OpenVSP\vspviewer.exe",
        vsp_output_case_dir + f'/{vsp_model.name}_DegenGeom.adb'
    ]
)
VSPAero_return_code = vsp_viewer.wait()

# Print All results
results = vsp.PrintResults(results_id)

# Rotor Results
# rotor_res = vsp.FindResultsID("VSPAERO_Rotor", 0)
# thrust = vsp.GetDoubleResults(rotor_res, "Thrust", 0)
# print(thrust, len(thrust))

# Get the name of each result's file
results_array = vsp.GetAllResultsNames()

# Plot Aerodynamic results
lod_Df = lod_results_plot(
                         cl_plot_flag=1,
                         cd_plot_flag=1,
                         VoVref_plot_flag=1,
                         Clc_cref_plot_flag=1,
                         Cdc_cref_plot_flag=1,
                         save_directory=vsp_output_case_dir,
                         )

lod_Df.to_csv(vsp_output_case_dir + '/lod' + '+' + str(RPM) + '.csv')

# Get Aerodynamic results (CL, CD, CDtOt, Cdi etc.)
history_df = history_results()
print("--> Saving history results Df to csv file")
history_df.to_csv(vsp_output_case_dir + '/his' + '+' + str(RPM) + '.csv')
print("History DataFrame saving finished")

print('Whole Process Finished :)')
