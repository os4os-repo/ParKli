import numpy as np
# Note that FLAG is a GLOBAL parameter and thus available at every level
FLAG = {}

FLAG["SET"] = 1     # Option to index the setting of processing
FLAG["gamma"] = 2.4   # Gamma index is standard 2.4
FLAG["subImVert"] = 4     # Number of subimages taken in he vertical direction (6) standard
FLAG["subImHorz"] = 4     # Number of subimages taken in he horizontal direction (8) standard
FLAG["illum"] = 0     # Illumination correction, 1 if a dedicated correction is done
FLAG["cmatrix"] = 1    # use of colour adaptation matrix (1=linear, 2=Bradford)
FLAG["delta"] = 4   # maximum in degrees that the values may deviate (4)
FLAG["noise"] = 0.8 # evade artificial objects and errors in processing
FLAG["satmin"] = 0.02 # find solutions with maximum colour expression, was 0.055
FLAG["Under"] = 21 # lower angle expected for that location
FLAG["Upper"] = 230 # upper angle expected for that location
# Meta data from the APP on observing conditions
FLAG["brand"] = 1 # device_name (convert name to numer) #BRA = 'SAMSUNG'
FLAG["cloudfrac"] = 0 # Cloud_Fraction - in the sky, float, between 0 (no clouds) and 1
FLAG["secchidisk"] = 0 # UserHasSecchiDisk - Boolean, 1 if a Secchi disk is used

# [FU number, x-value, y-value, hue angle]
FUE = np.array([
    [1, 0.191, 0.167, 229.591],
    [2, 0.199, 0.2, 224.786],
    [3, 0.21, 0.24, 217.12],
    [4, 0.227, 0.288, 202.807],
    [5, 0.246, 0.335, 178.703],
    [6, 0.266, 0.376, 147.45],
    [7, 0.291, 0.411, 118.535],
    [8, 0.315, 0.44, 99.532],
    [9, 0.337, 0.461, 88.479],
    [10, 0.363, 0.476, 78.132],
    [11, 0.386, 0.486, 70.934],
    [12, 0.402, 0.481, 64.906],
    [13, 0.416, 0.473, 59.383],
    [14, 0.431, 0.465, 53.395],
    [15, 0.446, 0.457, 47.842],
    [16, 0.461, 0.449, 42.331],
    [17, 0.475, 0.441, 37.125],
    [18, 0.489, 0.433, 32.607],
    [19, 0.503, 0.424, 28.199],
    [20, 0.516, 0.416, 24.418],
    [21, 0.528, 0.408, 21.024]
])

EILL_VECTOR = {
    "overcast": np.array([0.96, 1.00, 0.99]),
    "sunny": np.array([0.98, 1.00, 1.05])
}
