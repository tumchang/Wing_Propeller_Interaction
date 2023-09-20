from xrotor_liftingline_main import xf_xr_lili
from xrotor_lili_func import *
from pyoptsparse import Optimization, SLSQP

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

cpacs_init = './Do328_nonac.xml'
# cpacs_ref = "./LILI/Do328_out/propTrue_RPM800/propTrue_RPM800.xml"


# For Xdict x[0]=chord3, x[1]=twist3, x[2]=span, x[3]=section3 tip x position
def objective_function(xdict):
    x = xdict["xvars"]

    funcs = {}
    funcs["obj"] = 10000 * xf_xr_lili(oper_point, cpacs_init, RPM, xdict)

    print([f"{value:.6f}" for value in x])
    print(funcs["obj"])

    conval = [0] * 1
    conval[0] = x[2] * 2.0
    funcs["con"] = conval

    fail = False

    return funcs, fail


def optimize_wing():
    optProb = Optimization('WingOptimization', objective_function)

    # x[0]=chord3, x[1]=twist3, x[2]=span, x[3]=section3 tip x position
    # optProb.addVar('chord', 'c', lower=0.01, upper=2.21, value=1.26)
    # optProb.addVar('twist', 'c', lower=-5, upper=2, value=-0.5)
    optProb.addVarGroup("xvars", 4, "c",
                        lower=[0.01, -5, 3.67, 0],
                        upper=[2.21, 2, 36, 10],
                        value=[1.26, -0.5, 10.49, 0.523329523674763]
                        )

    # Set constraints
    optProb.addConGroup("con", 1, lower=None, upper=36)

    # Set the objective
    optProb.addObj('obj')
    print(optProb)

    # rst begin OPT
    # Optimizer
    optOptions = {
        "IPRINT": 0,
        # "TOLC": 1e-02,
        # "TOLG": 1e-02,
        # "TOLX": 1e-03,
        # "RPF": 0.01
    }

    opt = SLSQP(options=optOptions)

    # rst begin solve
    # Solve
    sol = opt(optProb, sens="CD")

    # Check Solution
    print(sol)


if __name__ == '__main__':
    solution = optimize_wing()
    print(solution)
