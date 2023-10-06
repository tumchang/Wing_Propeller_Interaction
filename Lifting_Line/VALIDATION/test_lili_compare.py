import matplotlib.pyplot as plt
import numpy as np

# =====================================================================================================================
# 0deg
# =====================================================================================================================
prowim_x = [0.097, 0.174, 0.252, 0.283, 0.315, 0.347, 0.378, 0.409, 0.531, 0.562, 0.593,
            0.623, 0.655, 0.687, 0.749, 0.812, 0.872, 0.919
            ]
openvsp_x = np.asarray([8.34E-03, 2.53E-02, 4.27E-02, 6.07E-02, 7.90E-02, 9.78E-02, 1.17E-01, 1.36E-01,
                        1.56E-01, 1.76E-01, 1.96E-01, 2.16E-01, 2.37E-01, 2.57E-01, 2.77E-01, 2.97E-01,
                        3.17E-01, 3.37E-01, 3.56E-01, 3.75E-01, 3.93E-01, 4.12E-01, 4.29E-01, 4.46E-01,
                        4.63E-01, 4.79E-01, 4.95E-01, 5.10E-01, 5.24E-01, 5.38E-01, 5.51E-01, 5.64E-01,
                        5.76E-01, 5.87E-01, 5.98E-01, 6.08E-01, 6.18E-01, 6.27E-01, 6.36E-01,
                        ])
openvsp_x = openvsp_x / 0.64

prowim_zero_deg_y = [0.027, 0.032, 0.042, 0.045, 0.097, 0.088, 0.078, 0.05, -0.026, -0.061, -0.079, -0.084, -0.046,
                     -0.023, -0.019, -0.014, -0.013, -0.0095
                     ]

lili_x = [0.016129033, 0.048387167, 0.080645167, 0.112903167, 0.145161333, 0.17742, 0.209676667, 0.241935,
          0.274193333, 0.306451667, 0.33871, 0.370968333, 0.403225, 0.435483333, 0.467741667, 0.5, 0.532258333,
          0.564516667, 0.596775, 0.629031667, 0.66129, 0.693548333, 0.725806667, 0.758065, 0.790321667, 0.82258,
          0.854838333, 0.887096667, 0.919355, 0.951613333, 0.983871667
          ]
lili_zero_deg_y = [0.0245705, 0.025021, 0.0259495, 0.0274157, 0.0295246, 0.0324524, 0.0365079, 0.0422643,
                   0.0515428, 0.0759082, 0.109064, 0.113922, 0.0978902, 0.0639168, 0.028421,
                   0.00433422, -0.0197029, -0.0545226, -0.0874604, -0.102673, -0.0972285,
                   -0.0650344, -0.0412325, -0.0313903, -0.0249544, -0.0200822, -0.01617,
                   -0.0128639, -0.00991066, -0.00709123, -0.00333131,
                   ]
openvsp_zero_deg_y = [2.54E-02, 2.59E-02, 2.72E-02, 2.87E-02, 3.07E-02, 3.37E-02, 3.68E-02, 4.34E-02,
                      5.23E-02, 6.78E-02, 1.13E-01, 1.30E-01, 1.31E-01, 1.09E-01, 3.34E-02, -5.55E-03, -4.33E-02,
                      -1.23E-01, -1.47E-01, -1.51E-01, -1.41E-01, -1.19E-01, -7.73E-02, -6.03E-02, -5.01E-02,
                      -4.20E-02, -3.66E-02, -3.20E-02, -2.88E-02, -2.56E-02, -2.23E-02, -1.97E-02, -1.77E-02,
                      -1.56E-02, -1.33E-02, -1.13E-02, -9.35E-03, -7.26E-03, -4.70E-03,
                      ]

fig1 = plt.figure(figsize=(8, 8))
plt.scatter(prowim_x, prowim_zero_deg_y, label='PROWIM', color='black')
plt.plot(lili_x, lili_zero_deg_y, label='LiftingLine + XRotor')
plt.plot(openvsp_x, openvsp_zero_deg_y, label='Actuator Disk (VSPAero)')

plt.xlim(0.0, 1.0)
plt.ylim(-0.2, 1.2)

plt.title("0 degrees")
plt.xlabel('2y/b')
plt.ylabel('Cl')

plt.legend()
plt.grid(True)

# =====================================================================================================================
# 4deg
# =====================================================================================================================
prowim_4_deg_y = [0.362, 0.368, 0.378, 0.377, 0.43, 0.421, 0.41, 0.345, 0.246, 0.247, 0.234, 0.226,
                  0.267, 0.261, 0.247, 0.227, 0.196, 0.163
                  ]
lili_4_deg_y = [0.357616, 0.357868, 0.358397, 0.35926, 0.360559, 0.362462, 0.365271, 0.369553, 0.377084, 0.433785,
                0.511336, 0.505536, 0.466733, 0.398224, 0.337857, 0.308944, 0.280918, 0.260114,
                0.248878, 0.243327, 0.246409, 0.230179, 0.216493, 0.215657, 0.209825, 0.200435,
                0.187534, 0.170612, 0.148378, 0.11862, 0.0608879,
                ]
openvsp_4deg = [3.74E-01, 3.75E-01, 3.76E-01, 3.77E-01, 3.78E-01, 3.81E-01, 3.84E-01, 3.91E-01,
                3.98E-01, 4.14E-01, 4.89E-01, 5.24E-01, 5.37E-01, 5.32E-01, 5.06E-01, 3.90E-01,
                2.85E-01, 2.49E-01, 2.17E-01, 2.00E-01, 1.94E-01, 1.92E-01, 2.10E-01, 2.20E-01,
                2.22E-01, 2.22E-01, 2.18E-01, 2.14E-01, 2.07E-01, 2.00E-01, 1.92E-01, 1.83E-01,
                1.72E-01, 1.60E-01, 1.46E-01, 1.30E-01, 1.13E-01, 9.10E-02, 6.10E-02,
                ]

fig2 = plt.figure(figsize=(8, 8))
plt.scatter(prowim_x, prowim_4_deg_y, label='PROWIM', color='black')
plt.plot(lili_x, lili_4_deg_y, label='LiftingLine + XRotor')
plt.plot(openvsp_x, openvsp_4deg, label='Actuator Disk (VSPAero)')

plt.xlim(0.0, 1.0)
plt.ylim(-0.2, 1.2)

plt.title("4 degrees")
plt.xlabel('2y/b')
plt.ylabel('Cl')

plt.legend()
plt.grid(True)

# =====================================================================================================================
# 4deg no prop
# =====================================================================================================================
prowim_x_noprop = [0.0979, 0.175, 0.255, 0.315, 0.377, 0.408, 0.531, 0.563, 0.623,
                   0.686, 0.748, 0.811, 0.872, 0.919
                   ]
prowim_4_deg_y_noprop = [0.333, 0.334, 0.335, 0.329, 0.315, 0.307, 0.284, 0.289, 0.283, 0.277,
                         0.249, 0.23, 0.197, 0.163
                         ]
lili_4_deg_y_noprop = [0.333018, 0.332819, 0.332418, 0.331812, 0.330998, 0.329967, 0.328711,
                       0.32722, 0.325481, 0.323477, 0.321191, 0.3186, 0.31568, 0.312399, 0.308721,
                       0.304605, 0.300001, 0.294848, 0.289075, 0.282595, 0.275303, 0.267066, 0.257719,
                       0.24705, 0.234775, 0.220509, 0.203693, 0.183464, 0.158277, 0.125699, 0.0642124,
                       ]
openvsp_4deg_noprop = [3.37E-01, 3.37E-01, 3.36E-01, 3.36E-01, 3.35E-01, 3.34E-01, 3.33E-01,
                       3.32E-01, 3.31E-01, 3.29E-01, 3.27E-01, 3.25E-01, 3.22E-01, 3.20E-01, 3.17E-01,
                       3.14E-01, 3.10E-01, 3.07E-01, 3.02E-01, 2.97E-01, 2.92E-01, 2.86E-01, 2.80E-01,
                       2.74E-01, 2.66E-01, 2.59E-01, 2.50E-01, 2.41E-01, 2.31E-01, 2.21E-01, 2.10E-01,
                       1.99E-01, 1.86E-01, 1.72E-01, 1.56E-01, 1.39E-01, 1.19E-01, 9.58E-02, 6.41E-02,
                       ]

fig3 = plt.figure(figsize=(8, 8))
plt.scatter(prowim_x_noprop, prowim_4_deg_y_noprop, label='PROWIM')
plt.plot(lili_x, lili_4_deg_y_noprop, label='LiftingLine')
plt.plot(openvsp_x, openvsp_4deg_noprop, label='Actuator Disk (VSPAero)')

plt.title("4 degrees with no Prop!")
plt.xlabel('2y/b')
plt.ylabel('Cl')

plt.xlim(0.0, 1.0)
plt.ylim(-0.2, 1.2)

plt.legend()
plt.grid(True)

# =====================================================================================================================
# 4deg reversed
# =====================================================================================================================
prowim_4deg_y_reversed = [0.314, 0.316, 0.307, 0.317, 0.265, 0.263, 0.263, 0.257, 0.301,
                          0.375, 0.385, 0.382, 0.333, 0.303, 0.285, 0.254, 0.218, 0.182,
                          ]
lili_4_deg_y_reversed = [0.308429, 0.307778, 0.306448, 0.304374, 0.301448, 0.297486, 0.29217,
                         0.284913, 0.273906, 0.281314, 2.92E-01, 2.76E-01, 2.69E-01, 2.70E-01, 2.81E-01,
                         3.00E-01, 3.20E-01, 3.70E-01, 4.25E-01, 4.50E-01, 4.42E-01, 3.61E-01, 2.99E-01,
                         2.78E-01, 2.60E-01, 2.41E-01, 2.20E-01, 1.96E-01, 1.68E-01, 1.33E-01, 6.75E-02,
                         ]
vsp_4deg_reversed = [3.00E-01, 2.99E-01, 2.97E-01, 2.95E-01, 2.92E-01, 2.88E-01, 2.82E-01,
                     2.74E-01, 2.63E-01, 2.44E-01, 2.21E-01, 2.11E-01, 2.08E-01, 2.19E-01, 2.45E-01,
                     2.53E-01, 3.80E-01, 4.73E-01, 4.86E-01, 4.80E-01, 4.56E-01, 4.13E-01, 3.50E-01,
                     3.28E-01, 3.11E-01, 2.96E-01, 2.82E-01, 2.69E-01, 2.57E-01, 2.44E-01, 2.30E-01,
                     2.16E-01, 2.01E-01, 1.85E-01, 1.68E-01, 1.49E-01, 1.28E-01, 1.03E-01, 6.87E-02,
                     ]

fig4 = plt.figure(figsize=(8, 8))
plt.scatter(prowim_x, prowim_4deg_y_reversed, label='PROWIM')
plt.plot(lili_x, lili_4_deg_y_reversed, label='LiftingLine + XRotor')
plt.plot(openvsp_x, vsp_4deg_reversed, label='Actuator Disk (VSPAero)')

plt.xlim(0.0, 1.0)
plt.ylim(-0.2, 1.2)

plt.title("4 degrees reversed")
plt.xlabel('2y/b')
plt.ylabel('Cl')

plt.legend()
plt.grid(True)

# ALL TOGETHER
# fig4 = plt.figure(figsize=(8, 8))
# plt.scatter(prowim_x, prowim_zero_deg_y, label='PROWIM', color='black')
# plt.plot(lili_x, lili_zero_deg_y, label='LiftingLine + XRotor')
# plt.plot(openvsp_x, openvsp_zero_deg_y, label='Actuator Disk (VSPAero)')
#
# plt.scatter(prowim_x, prowim_4_deg_y, label='PROWIM', color='black')
# plt.plot(lili_x, lili_4_deg_y, label='LiftingLine + XRotor')
# plt.plot(openvsp_x, openvsp_4deg, label='Actuator Disk (VSPAero)')
#
# plt.title("ALL together")
# plt.xlabel('2y/b')
# plt.ylabel('Cl')
#
# plt.xlim(0.0, 1.0)
# plt.ylim(-0.2, 1.2)
#
# plt.legend()
# plt.grid(True)


# =====================================================================================================================
# This section is used for CL_alpha comparison J=0.811
# =====================================================================================================================
alpha = [0, 2, 4, 6, 8, 10]
prowim_prop_on = [0, 0.166, 0.324, 0.474, 0.621, 0.768]
lili_prop_on = [0.00654358, 0.145449 + 0.00486, 0.283934 + 0.01, 0.421569 + 0.0146, 0.55793 + 0.0195, 0.6926 + 0.024]

prowim_prop_off = [0, 0.139, 0.269, 0.394, 0.514]
lili_prop_off = [0, 0.129955, 0.259518, 0.388303, 0.515927]

fig10 = plt.figure(figsize=(8, 8))
plt.plot(alpha, prowim_prop_on, 'x', color='red', label='PROWIM prop on')
plt.plot(alpha, lili_prop_on, '-o', color='red', label='LiftingLine prop on')

plt.plot(alpha[0:-1], prowim_prop_off, 'x', color='blue', label='PROWIM prop off')
plt.plot(alpha[0:-1], lili_prop_off, '-o', color='blue', label='LiftingLine prop off')

plt.title("CL Alpha (J=0.811)")
plt.xlabel('Alpha [deg]')
plt.ylabel('CL')

plt.xlim(0.0, 10)
plt.ylim(0, 0.8)
plt.legend()
plt.grid(True)

plt.show()
