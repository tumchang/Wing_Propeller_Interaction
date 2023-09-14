import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

for i in range(1, 11):
    # Load the data
    data = np.loadtxt('.\\fuselage\\' + 'D150_VAMP_FL1_ProfSupEl' + str(i) + '.fxs', skiprows=1)
    x_old = data[:, 0]
    y_old = data[:, 1]

    # Convert the old x and y values to complex numbers
    complex_old = x_old + 1j*y_old

    # Create an array of theta values from 0 to 2pi
    theta_old = np.linspace(0, 2*np.pi, len(x_old))

    # Interpolate the old data
    cs = CubicSpline(theta_old, complex_old)

    # Generate new theta values
    theta_new = np.linspace(0, 2*np.pi, 91)

    # Generate new complex values
    complex_new = cs(theta_new)

    # Extract the new x and y values
    x_new = np.real(complex_new)
    y_new = np.imag(complex_new)

    # Create a plot
    fig, ax = plt.subplots(figsize=(10, 5))

    # Plot old data as scatter
    ax.plot(x_old, y_old, '-x', label='Original Data')

    # Plot new data as curve
    ax.plot(x_new, y_new, '-o', label='Scaled Data')

    # Set title and show legend
    ax.set_title('Comparison for File ' + str(i))
    ax.legend()

    # Show the plot
    plt.tight_layout()
    plt.show()


print('fitting completed')
