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
from pyoptsparse.pyOpt_history import History

# Specify the CPACS file to include engine Nacelle or not
nonac = True
prop_flag = False

# Operation Point definition
oper_point = OperPNT()
oper_point.beta_70 = 55.31
oper_point.rho = 1.225
oper_point.hub_radius = 0.376
oper_point.tip_radius = 1.88
# oper_point.RPM_list = list(range(700, 1001, 100))
oper_point.RPM_list = [800]
oper_point.Vinf = 142
oper_point.B = 6

RPM = 800
# CPACS Ref File
if nonac:
    cpacs_init = "./Do328_nonac.xml"
else:
    cpacs_init = "./Do328.xml"
# cpacs_init = './Do328_nonac.xml'

# Get the origin shape and area of the wing
original_wing = WingShape(cpacs_init)
# origin_df, origin_area, origin_AR, origin_lambda = get_original_wing(cpacs_init)
# origin_wing_weight =

# cpacs_ref = "./LILI/Do328_out/propTrue_RPM800/propTrue_RPM800.xml"


# For Xdict x[0]=chord3, x[1]=twist3, x[2]=span, x[3]=section3** tip x position
def objective_function(xdict):
    x = np.zeros(len(xdict))
    x[0], x[1], x[2] = xdict["chord3"], xdict["twist3"], xdict["half span"]

    funcs = {}
    # ================================================================================================================
    # Definition of optimization object(Breguet Range Function estimation)
    # ================================================================================================================
    s, wing_weight_new = xf_xr_lili(oper_point, cpacs_init, RPM, xdict, original_wing)

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
    # 4. Wing structural weight increase percentage
    AR_new = (2*x[2])**2 / area
    conval[3] = wing_weight_new / original_wing.wing_weight_est
    # 5. AR change percentage
    conval[4] = AR_new/original_wing.AR

    # funcs["con"] = conval
    funcs["Whole Span"] = conval[0]
    funcs["Wing Area"] = conval[1]
    funcs["Taper Ratio"] = conval[2]
    funcs["Wing Weight Change"] = conval[3]
    funcs["Aspect Ratio Change"] = conval[4]

    fail = False

    return funcs, fail


def optimize_wing():
    optProb = Optimization('WingOptimization', objective_function)

    # x[0]=chord3, x[1]=twist3, x[2]=span, x[3]=section3 tip x position
    optProb.addVar("chord3", "c", lower=0.01, upper=2.21, value=original_wing.section["chord"][2])
    optProb.addVar("twist3", "c", lower=-5, upper=2, value=-0.5)
    optProb.addVar("half span", "c", lower=5, upper=18, value=original_wing.section["tip_y"][2])
    # optProb.addVarGroup("xvars", 3, "c",
    #                     #      chord3,                 twist3,                 span,            sweep
    #                     lower=[0.01,                        -5,                     5],
    #                     upper=[2.21,                         2,                    18],
    #                     value=[origin_df["chord"][2],     -0.5, origin_df["tip_y"][2]],
    #                     )

    # Set constraints
    # 1. The whole wing span should not be larger than 36m
    # 2. The wing area should not be smaller than original area
    # 3. The taper ratio of the outer section should not be smaller than 0.2 or larger than 0.7
    # 4. Wing structural weight increase percentage
    # 5. AR change percentage
    optProb.addCon("Whole Span", lower=0, upper=36)
    optProb.addCon("Wing Area", lower=original_wing.area, upper=None)
    optProb.addCon("Taper Ratio", lower=0.2, upper=0.7)
    optProb.addCon("Wing Weight Change", lower=0.8, upper=1.2)
    optProb.addCon("Aspect Ratio Change", lower=0.8, upper=2)
    # optProb.addConGroup("con", 5,
    #                     lower=[None, origin_area, origin_df["chord"][1]*0.2, 0.8, 0.8],
    #                     upper=[36,          None, origin_df["chord"][1]*0.7, 1.2,   2]
    #                     )

    # Set the objective
    optProb.addObj('obj')
    print(optProb)

    # rst begin OPT
    # Optimizer
    optOptions = {
        "IPRINT": 1,
        # "PrintOut": 1,
        # "TOLC": 1e-02,
        # "TOLG": 1e-02,
        # "TOLX": 1e-03,
        # "RPF": 0.01
    }

    opt = SLSQP(options=optOptions)

    # rst begin solve
    # Solve
    sol = opt(optProb, sens="CD", storeHistory='opt_history_noprop.hst')

    # Check Solution
    print(sol)

    # History visualization
    history = History('opt_history_noprop.hst', optProb=SLSQP)


if __name__ == '__main__':
    solution = optimize_wing()
    print(solution)
    # history = History('opt_history_noprop.hst', optProb=SLSQP)

    pass
