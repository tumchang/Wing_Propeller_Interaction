from xrotor_lili_func import *
from scipy.optimize import curve_fit


def parabolic_equation(cl, cd0, k):
    """Parabolic equation to fit Cd vs Cl^2 data."""
    return cd0 + k * cl ** 2


def compute_derivative(cd, cl):
    """Compute d(Cd)/d(Cl^2) from Cd and Cl data."""

    # Fit the data to the parabolic equation
    params, _ = curve_fit(parabolic_equation, cl, cd)
    cd0, k = params

    # The coefficient k represents d(Cd)/d(Cl^2)
    return cd0, k


polar_dir = f'./xfoil/65212_polar.txt'

polar = AirfoilPolar(polar_dir)
cd0, derivative_value = compute_derivative(polar.CD, polar.CL)

plt.plot(polar.CD, polar.CL)

# plt.plot(polar.alpha, polar.CL)

plt.show()

pass
