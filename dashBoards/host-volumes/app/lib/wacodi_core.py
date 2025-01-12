import numpy as np
import pandas as pd

def GammaI(sRGB, BRA, GAI):
    # % function to do the Gamma correction for Images
    # % makes the transform from sRGB to XYZ coordinates
    # % This function can be optimized for camera settings
    # %
    # % input: sRGB The subimage that is transformed to linear scale
    # %        BRA  Brand of the smart phone to update GAI index
    # %        GAI  Standard Gamma index defined in loadSWITCH.m
    # % output: XYX linearized subimage
    # %         dp  dot product of the colour vector with white vector
    # %         av= Cosine of the angle between the white and colour vector.

    # % prepare the space for the new image
    M, N ,C = sRGB.shape # % the real size of the processing
    XYZ = np.zeros(sRGB.shape)
    # % update the information on the Gamma index
    if BRA == "SAMSUNG":
        GAI= 2.2 # % check 2.2 basically

    # % Do the Gamma correction here
    # % first do a normalisation of the interval [0-255] to [0 1]
    nsRGB = sRGB/255.0

    # Make a Gamma transform to enhance range in the sensitive part of the eye
    # index = np.all(nsRGB <= 0.04045)
    # if index:
    #     GnsRGB = nsRGB/12.92
    # else:
    #     GnsRGB = ((nsRGB+0.055)/1.055)**GAI
    GnsRGB = np.zeros(sRGB.shape)
    index = nsRGB <= 0.04045
    GnsRGB[index] = nsRGB[index]/12.92
    GnsRGB[index==False] = ((nsRGB[index==False]+0.055)/1.055)**GAI

    """ This constant should probably be in config """
    # % Do the transformation from the sRGB colour definition to XYZ here
    # % define the transformation matrix from sRGB to XYX
    TM = np.array([[0.4125, 0.3576, 0.1804],
                   [0.2127, 0.7152, 0.0722],
                   [0.0193, 0.1192, 0.9503]])
    # % make the colour transformation
    for i in range(M):
        for j in range(N):
            pix = GnsRGB[i, j, : ]
            XYZpix = TM.dot(pix)
            XYZ[i, j, : ] = XYZpix

    # % calculate some properties of the nsRGB colour matrix.
    wv = np.array([1, 1, 1]) # % define the white vector
    r = np.mean(np.mean(nsRGB[ : , : , 0]))
    g = np.mean(np.mean(nsRGB[ : , : , 1]))
    b = np.mean(np.mean(nsRGB[ : , : , 2]))
    cv = np.array([r, g, b]) # % vector of the mean colours in the subimage
    dp = cv.dot(wv) # % dot product of the colour vector with white vector
    # %the cosine of the angle to the white.
    av = dp/(np.sqrt(3)*np.sqrt(r*r+g*g+b*b))
    # % return these numbers as a quality flag in the output

    return XYZ, dp, av

def Colouradapt(ws, wd, crm):
    # %Function to calculate the colour adaptation matrix
    # %Check very carefully how source and destination are determined !
    # %
    # %   input: ws source white vector
    # %          wd destination white vector
    # %          crm choice for cone response matrix
    # %   output: MACA matrix for Colour Adaptation to illumination

    if crm == 1: # % XYZ Scaling
        MA = np.array([[1, 0, 0],
                       [0, 1, 0],
                       [0, 0, 1]])
        IMA = np.linalg.inv(MA)
    else: #        % Bradford
        MA = np.array([[0.8951, 0.2664, -0.1614],
                       [-0.7502, 1.7135, 0.0367],
                       [0.0389, -0.0685, 1.0296]])
        IMA = np.linalg.inv(MA)

    CONEdes =  MA.dot(wd) #   % destination vector
    CONEsou =  MA.dot(ws) #   % source vector
    a = CONEdes[0]/CONEsou[0]
    b = CONEdes[1]/CONEsou[1]
    c = CONEdes[2]/CONEsou[2]

    XYZM = np.array([[a, 0, 0],
                     [0, b, 0],
                     [0, 0, c]])
    MACA = IMA.dot(XYZM).dot(MA)

    return MACA

def LuminI(XYZ, Eill, Mset):
    # % function to do the illumination correction on an image
    # % This function can be optimized for particular illumination
    # %
    # % input : XYZ the subimage that is transformed to linear scale
    # %       : Eill the special Eill matrix for that observation/station
    # %       : Mset colour adaptation matrix (1=linear, 2=Bradford)
    # % output: EXYX subimage that is transformed to white light illumination

    # % do the illumination transformation (Bradford or scaling matrix)
    # % get the illumination matrix from FU_transform.m

    # % some standard vectors
    E   = np.array([1, 1, 1]) # % coordinates of white point in E
    D65 = np.array([0.95047, 1.00000, 1.08883]) # % standard D65 illumination

    # % set the first the standard illumniation right
    Mscaling = Colouradapt(D65, E, Mset)

    # % Calculate the transformation matrix
    Mill = Colouradapt(Eill, E, Mset)

    M, N, C = XYZ.shape # % the real size of the processing
    EXYZ = np.zeros(XYZ.shape)

    for i in range(M): #=1:M;
        for j in range(N): #=1:N;
            pix = XYZ[i, j, : ]
            EXYZpix = Mscaling.dot(pix) # % First the D65 transformation
            EXYZpix = Mill.dot(EXYZpix) # % Then the illumination correction
            EXYZ[i, j, : ] = EXYZpix

    return EXYZ

def XYZ2alpha(Esuim):
    # % function to do the transformation from X,Y,Z to hue colour angle
    # %
    # % input : EXYZ the subimage that is transformed to white illumination
    # % output: na array with the colour angles of all pixels
    # %       : ns array with the colour saturation of all pixels

    M, N ,C = Esuim.shape # % the real size of the processing
    rshf = M*N # % the size of all the elements

    EX = Esuim[ : , : , 0]
    EY = Esuim[ : , : , 1]
    EZ = Esuim[ : , : , 2]
    ES = EX+EY+EZ
    Ex = EX/ES
    Ey = EY/ES

    """ If we are using E or D65 should not be hard-coded by commenting out
        one line like this
    """
    # % The whole matrix is now given in the colour angle relative to white
    xw = Ex-0.33333
    yw = Ey-0.33333 # % White point in E
    # %xw=Ex-0.31280
    # yw=Ey-0.3290; % White point in D65

    sat = np.sqrt(xw*xw+yw*yw) # %saturation: distance from the white point

    angle = np.arctan2(yw, xw)
    angle = angle*(180/np.pi)

    for i in range(M): #=1:M;
        for j in range(N): #=1:N;
            if angle[i,j] < 0.0:
                angle[i,j] = angle[i,j]+360

    na = angle.reshape((rshf,), order="F") # % reshape image of angle to vector
    ns = sat.reshape((rshf,), order="F") # % reshape image of saturation to vector

    return na, ns

def wacodi_core(sRGB, eill_vector, p, FLAG):
    # %     Transform from sRGB to XYZ coordinates
    XYZ, dp, av = GammaI(sRGB,FLAG["brand"],FLAG["gamma"])

    # %     Do the correction for illumination and sky correction
    EXYZ = LuminI(XYZ, eill_vector, FLAG["cmatrix"])

    # %     Do the transformation from XYZ coordinates to angle and saturation
    na, ns = XYZ2alpha(EXYZ)

    # %     Calculate the percentiles of the colour angle distribution
    hue_angle = np.percentile(na, p)
    saturation = np.percentile(ns, p)

    # %     End processing of the sub-image

    return (dp, av, hue_angle, saturation)
