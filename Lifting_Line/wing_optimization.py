"""
============================================================================
This script is used for the wing optimization loop using
PyoptSparse module

-------------
Author: Chang Xu   TUM   03739064  Sep.2023
Supervisor: Yiyuan Ma & Alexandros Lessis

Copyright @ Bauhaus Luftfahrt e.V
============================================================================
"""

from xrotor_liftingline_main import xf_xr_lili
from xrotor_lili_func import *
from pyoptsparse import Optimization, SLSQP, NSGA2


# Specify the CPACS file to include engine Nacelle or not
nonac = True
prop_flag = True

# Specify optimization method
opt_method = 'NSGA2'

# Operation Point definition
oper_point = OperPNT()
oper_point.beta_70 = 55.31
oper_point.rho = 0.6597
oper_point.hub_radius = 0.376
oper_point.tip_radius = 1.88
# oper_point.RPM_list = list(range(700, 1001, 100))
oper_point.RPM_list = [800]
oper_point.Vinf = 142
oper_point.B = 6

RPM = oper_point.RPM_list[0]

# Operation Point definition
oper_point_2 = OperPNT()
oper_point_2.beta_70 = 55.31
oper_point_2.rho = 0.6597
oper_point_2.hub_radius = 0.230
oper_point_2.tip_radius = 1.15
oper_point_2.RPM_list = [1200]
oper_point_2.Vinf = 142
oper_point_2.B = 7

RPM_2 = oper_point_2.RPM_list[0]

# CPACS Ref File
if nonac:
    cpacs_init = "./Do328_nonac_4.xml"
else:
    cpacs_init = "./Do328.xml"

# Get the origin shape and area of the wing
original_wing = WingShape(cpacs_init, eta_cp=0.42, wing_method='Torenbeek')


# For Xdict x[0]=chord3, x[1]=twist3, x[2]=span, x[3]=section3** tip x position
def objective_function(xdict):
    x = np.zeros(len(xdict))
    x[0], x[1], x[2] = xdict["chord3"], xdict["twist3"], xdict["half span"]

    funcs = {}
    # ================================================================================================================
    # Definition of optimization object(Breguet Range Function estimation)
    # ================================================================================================================
    s, wing_weight_new = xf_xr_lili(oper_point, cpacs_init, RPM, xdict, original_wing, prop_flag,
                                    oper_point_2, RPM_2,
                                    opt_method=opt_method)
    # s, wing_weight_new = xf_xr_lili(oper_point, cpacs_init, RPM, xdict, original_wing, prop_flag)

    funcs["obj"] = -s

    print([f"{value:.6f}" for value in x])
    print(funcs["obj"])

    # ================================================================================================================
    # Definition of constraints
    # ================================================================================================================
    # Definition of the number of constraints
    conval = [0] * 5
    # 1. Whole Wing Span
    conval[0] = x[2] * 2.0
    # 2. Whole Wing Area
    area = (
            (original_wing.section["chord"][0] + original_wing.section["chord"][1])
            * (original_wing.section["tip_y"][1] - original_wing.section["tip_y"][0])
            + (original_wing.section["chord"][1] + x[0]) * (x[2] - original_wing.section["tip_y"][1])
            )
    conval[1] = area
    # 3. Chord length of the outermost section
    conval[2] = x[0] / original_wing.section["chord"][1]
    # TODO: new constraint for wing weight percentage of the MTOW
    # 4. Wing structural weight increase percentage
    # conval[3] = wing_weight_new / original_wing.wing_weight_est
    # 4. new constraint for wing weight percentage of the MTOW
    conval[3] = wing_weight_new / original_wing.MTOW
    # 5. AR change percentage
    AR_new = (2 * x[2]) ** 2 / area
    conval[4] = AR_new/original_wing.AR

    # funcs["con"] = conval
    funcs["Whole Span"] = conval[0]
    funcs["Wing Area"] = conval[1]
    funcs["Taper Ratio"] = conval[2]
    funcs["Wing Weight Percentage"] = conval[3]
    funcs["Aspect Ratio Change"] = conval[4]

    fail = False

    return funcs, fail


def optimize_wing():
    optProb = Optimization('WingOptimization', objective_function)

    # x[0]=chord3, x[1]=twist3, x[2]=span, x[3]=section3 tip x position
    optProb.addVar("chord3", "c", lower=0.01, upper=2.21, value=original_wing.section["chord"][2])
    optProb.addVar("twist3", "c", lower=-5, upper=2, value=-0.5)
    optProb.addVar("half span", "c", lower=5, upper=18, value=original_wing.section["tip_y"][2])

    # Set constraints
    # 1. The whole wing span should not be larger than 36m
    # 2. The wing area should not be smaller than original area
    # 3. The taper ratio of the outer section should not be smaller than 0.2 or larger than 0.7
    # 4. Wing structural weight increase percentage
    # 5. AR change percentage
    optProb.addCon("Whole Span", lower=0, upper=36)
    optProb.addCon("Wing Area", lower=original_wing.area, upper=original_wing.area*1.2)
    optProb.addCon("Taper Ratio", lower=0.3, upper=0.7)
    optProb.addCon("Wing Weight Percentage", lower=0.05, upper=0.2)
    optProb.addCon("Aspect Ratio Change", lower=0.8, upper=2)

    # Set the objective
    optProb.addObj('obj')
    print(optProb)

    # rst begin OPT
    # Optimizer setting
    if opt_method == 'SLSQP':
        optOptions = {
            "IPRINT": 1,
            "ACC": 1e-08   # 1e-06 default
        }
        opt = SLSQP(options=optOptions)

    elif opt_method == 'NSGA2':
        optOptions = {
            "PopSize": 300,
            "maxGen": 5000
        }
        opt = NSGA2(options=optOptions)

    # rst begin solve
    # Solve
    if opt_method == 'SLSQP':
        sol = opt(optProb, sens="FDR", storeHistory=f'opt_history_{opt_method}.hst')
    elif opt_method == 'NSGA2':
        sol = opt(optProb, sens="CD", storeHistory=f'opt_history_{opt_method}.hst')

    # Check Solution
    print(sol)


if __name__ == '__main__':
    optimize_wing()

    # History visualization
    history_visualization(f'opt_history_{opt_method}.hst', optProb=opt_method)

    pass
