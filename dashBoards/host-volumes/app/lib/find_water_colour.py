import numpy as np
import pandas as pd
from PIL import Image
from lib.wacodi_core import wacodi_core
import lib.config

# def loadSWITCH():
#     # function to define a set of standard processing options
#     # This function can be optimized in further tests
#     # Note that now only a limited set of parameters is applied
#     #
#     # input:    NONE
#     # output:   parameters with settings and fill of global FLAG vector
#     # Parameter  0 to 19 contain the processing settings
#     # Parameter 20 to 39 could contain the observation metadata
#     # Parameter 40 to 59 contain the results of the processing

#     """ This should all be either constants pre-defined in config, or metadata
#         provided with/attached to the images, or even some command line args
#         FLAG[n] is not very descriptive, separating into names is much better
#         Perhaps a dictionary if everything needs to be grouped in FLAG, ie:
#         cfg.FLAG = { SET : 1, GAI : 2.4, SUM : 6, SUN : 8}, etc...
#         Then, to output: pd.DataFrame(list(cfg.FLAG.items())).to_csv(...)
#     """

#     """ Processing options for the functions """
#     #0 Option to index the setting of processing
#     ##cfg.FLAG[0] = SET = 1
#     #1 Gamma index is standard 2.4
#     cfg.FLAG[1] = GAI = 2.4
#     #2 Number of subimages taken in he vertical direction (6) standard
#     cfg.FLAG[2] = SUM = 4
#     #3 Number of subimages taken in he horizontal direction (8) standard
#     cfg.FLAG[3] = SUN = 4
#     #4 half size in pixels of the subimages, integer
#     cfg.FLAG[4] = HSQ = 20
#     #5 Displacement of subimages, could be random, integer
#     cfg.FLAG[5] = DIS = 0
#     #6 Illumination correction, 1 if a dedicated correction is done
#     cfg.FLAG[6] = ILL = 0
#     #7 use of colour adaptation matrix (1=linear, 2=Bradford)
#     cfg.FLAG[7] = Mset = 1
#     #8 maximum in degrees that the values may deviate (4)
#     cfg.FLAG[8] = delta = 4
#     #9 evade artificial objects and errors in processing
#     cfg.FLAG[9] = noise = 0.8
#     #10 find solutions with maximum colour expression % was 0.055
#     cfg.FLAG[10] = satmin = 0.02
#     #11 lower angle expected for that location
#     cfg.FLAG[11] = Under = 21
#     #12 upper angle expected for that location
#     cfg.FLAG[12] = Upper = 230

#     """ Meta data from the APP on observing conditions """
#     #19 is 1 if meta data is read from the XML file
#     cfg.FLAG[19] = XML = 0
#     #20 Date_time
#     #21 Location_lat_lon
#     #22 device_name (convert name to numer)
#     BRA = 'SAMSUNG'
#     cfg.FLAG[22] = 1
#     #23 FU_value (integer)
#     cfg.FLAG[23] = FUApp = 5
#     #24 viewing_angle (degrees)
#     cfg.FLAG[24] = NVA = 30.0
#     #25 azimuth_angle (degrees)
#     cfg.FLAG[25] = AVA = 135.0
#     #26 solar_zenith_angle (degrees)
#     cfg.FLAG[26] = SZA = 60.0
#     #27 Cloud_Fraction - in the sky, float, between 0 (no clouds) and 1
#     cfg.FLAG[27] = CLO = 0
#     #28 Rain - Boolean, 1 if it is raining
#     cfg.FLAG[28] = RAI= 0
#     #29 Wind - Wind conditions, integer, Beaufort
#     cfg.FLAG[29] = BFT = 3
#     #30 Bottom - Water plants or the bottom view, Boolean, 1 if bottom is seen
#     cfg.FLAG[30] = BOV = 0
#     #31 UserHasSecchiDisk - Boolean, 1 if a Secchi disk is used
#     cfg.FLAG[31] = SDU = 0
#     #32 UserHasPlasticFUscale
#     cfg.FLAG[32] = FUpla = 0
#     #33 Shadow - Water surface is in the shadow, Boolean, 1 if there is shaddow
#     cfg.FLAG[33] = SHA = 0
#     #34 ROI - Only processing Region of Interest, Boolean, 1 is process roi
#     cfg.FLAG[34] = ROI = 0
#     #35 WhiteBalance (convert options to number)
#     WBA= 'auto'
#     cfg.FLAG[35] = 1
#     #36 IntegrationTime - actual integration time of the picture in seconds
#     cfg.FLAG[36] = INT = 0.0
#     #37 FocalLength
#     cfg.FLAG[37] = FOL = 4.0
#     #38 PictureFormat (check depth of colour information)
#     cfg.FLAG[38] = DEP = 256
#     #39 PixelToAngle
#     cfg.FLAG[39] = PTA = 0.05

#     # % Flags 40 to 49 are still empty
#     # % Flags 50 to 59 contain a summary of the output
#     # % 50 Best estimate Hue angle in degrees
#     # % 51 Saturation distance for the best solution in x,y coordinates
#     # % 52
#     # % 53 subsection number in the x-direction
#     # % 54 subsection number in the y-direction
#     # % 55 FU scale belonging to the best hue angle
#     # % 56
#     # % 57 FU number based on the emperical method from Marcel Wernand


#     return SDU, BRA, GAI, SUM, SUN, HSQ, DIS, ILL, CLO, XML, Mset

# def loadNAMES(args):
#     # % function to load the list with names of images
#     # %
#     # % output:   A_names is a list with names of the images
#
#     # Use file(s) specified by command line argument
#     if len(args) > 1:
#         name_array = args[1:]
#     else: # 1 station from the article to test the software
#         name_array = ['S16W.jpg']
#
#     return name_array

# def create_Eill(station):
#     # % function to calculate the the illumination vector from measurements
#     # % The programme assumes that the Lsfc, Lsky and Es are already mapped on
#     # % the same wavelength grid. In the example all TriOS spectra are given on
#     # % the standard grid between 350 and 950 nm in 1 nm steps.
#     # %
#     # % input:   station is a string that contains the relevant sheet with data
#     # % output:  vector with the three component for chromatic adaptation
#
#     """ This should probably be replaced by metadata related to the images """
#     # %% Open the excel file and read the data
#     # % This file contains a selctionof spectra collected by S. Novoa
#     filename = 'par/Test_spectra.xlsx'
#     all = pd.read_excel(filename, station)
#
#     # % extract all the spectra from the information
#     lam = all.values[ : , 0] # % lambda 350-950 nm, 1 nm resolution
#     Lsfc = all.values[ : , 1] # % surface radiance
#     Lsky = all.values[ : , 2] # % Sky radiance
#     Es = all.values[ : , 3] # % downward irradiance
#     fres = all.values[0, 4] # % adopted fresnel reflection
#
#     # %% calculate the illumination correction spectrum
#     Eill = (Es*Lsfc)/(Lsfc-fres*Lsky)
#
#     """ This should maybe be from config (not sure if this varies though) """
#     # %% read the Cie curves and prepare in 1 nm grid
#     cie5 = pd.read_excel(filename, 'CIE_2_degrees')
#     # % CIE 1931 RGB curves is d in cie5 matrix
#     # % 0=lambda, 1,2,3,= R,G,B
#
#     # remove junk rows and change dtype
#     cie5 = cie5.values[3:].astype(np.float64)
#
#     # % wavelength grid of CMF values (380-780, 5nm)
#     LambdaCIE = cie5[ : , 0]
#     # % create 1 nm grid for more accurate calculations
#     Lambda1nm = np.array(range(380,781))
#
#     # %    do interpolation of CIE curves on the 1 nm grid
#     CMF = np.empty((401,4))
#     CMF[ : , 0] = Lambda1nm # % the wavelegth grid
#     CMF[ : , 1] = np.interp(Lambda1nm, LambdaCIE, cie5[ : , 1]) # % Red on 1 nm
#     CMF[ : , 2] = np.interp(Lambda1nm, LambdaCIE, cie5[ : , 2]) # % Green on 1 nm
#     CMF[ : , 3] = np.interp(Lambda1nm, LambdaCIE, cie5[ : , 3]) # % Blue on 1 nm
#
#     TriCMF = Eill[30:431] # % take all illuminations spectra over 380-780 nm
#     # More readable:
#     # TriCMF = Eill[np.logical_and(lam >= 380.0, lam <= 381.0)]
#
#     # %   do the chromaticity calculation
#     X = TriCMF.dot(CMF[ : , 1])
#     Y = TriCMF.dot(CMF[ : , 2])
#     Z = TriCMF.dot(CMF[ : , 3])
#     # % normalize to the Y= 1.00 as is standard in chrmoticity calculations
#     Xn = X/Y
#     Yn = 1.000
#     Zn = Z/Y
#     # % combine for output
#     fresh_Eill = [Xn, Yn, Zn]
#
#     return fresh_Eill
#
# def loadEill(ILL, CLO):
#     # % function to load the set of relevant illumination values
#     # %
#     # % input:  ILL Illumination correction, 1 if a dedicated correction is done
#     # % output: 2D-matrix with (station number, Eill vectors)
#     # %
#     # % The option 1 is presently used to make a reference processing
#     # % the data come the August 2013 Campaign in The Netherlands
#     # % The option 2 is presently used to make a reference processing
#     # % of the data collaected at the North Sea
#
#     """ This should be connected to metadata for each image
#         The number of stations in total (ie, number of rows in `vector`) should
#         not be hard-coded in this function. Instead it should be determined
#         by what images are in the in/ directory
#     """
#
#     # Initialise vector
#     vector = np.empty((2,3))
#
#     if ILL == 1: # % fill here the dedicated illumination corrections
#         # % get illumination correction vector, normalized to the Green band
#         # % select for each station the best illumination matrix
#         # % In this case we selected the Eill for station 14 and 16
#         # % The next lines contain the resulting vectors as explanation
#         # % Vector(1,:)= [1.07242763726754 1 1.71638044811958]; %
#         # % Vector(2,:)= [1.01897663834903 1 1.39047450082973]; %
#          vector[0] = create_Eill('Station1')
#          vector[1] = create_Eill('Station2')
#     else:
#         # % Case for ILL=0; just one fixed illumination per condition
#         overcast = np.array([0.96, 1.00, 0.99])
#         sunny = np.array([0.98, 1.00, 1.05])
#
#         vector[0] = sunny #;% overcast; %sunny; test with the overcast correction
#         vector[1] = sunny #;% overcast; %sunny; test with the overcast correction
#
#     return vector

def loadIMAGE(image_path):
    # function to load the image and relevant parameters
    # at present the images are read in .jpg format
    #
    # input:    image_name is the filename of the image to load
    # output:   numpy array of image data
    #           X and Y dimensions of the array (pixel dimensions of the image)
    #

    # NOTE: PIL should probably be used if exif data is required
    # This expects the image to be in the relative directory 'in/'
    # TODO: this should be more generalised
    # image_array = plt.imread('in/' + image_name) # % load the full image
    image_array = np.array(Image.open(image_path))

    X, Y, C = image_array.shape # % determine the size of the image
    if C != 3:
        try:
            image_array = image_array[:, :, :3]
        except:
            raise Exception("RGB must be n by m by 3")

    return (image_array, X, Y)

def Go4True(dop, anp, FLAG):
    # % function to derive the best estimate of the true colour of the water
    # %
    # % input : pa  The matrix that contains the angle percentiles per subsection
    # %         ps  The matrix that contains the saturation percentiles per subsection
    # %         dop The matrix that contains the inproduct per subsection
    # %         anp The matrix that contains the cosine to the white vector
    # % output: best, the angle that is the best approximation of the colour
    # %         product of that selection
    # %         angle of that selection
    # %
    # % Check the percentile distribution on the following
    # % Be sure that we only cover water
    # % 5%% must be larger than the minimum colour angle = 21.0 degrees
    # % 95%% must be less than the maximum angle= 230 degrees
    # %
    # % The true colour is best derived from a coherent patch of water
    # % so a narrow distribution of the colour angles
    # % The 10 and 90 %% must be within Delta percent of the median angle
    # %
    # % We assume that the lowest angle is least influence by sky refelction
    # % Take the smallest median value from the remaining squares

    # Start with the maximum angle
    best_estimate = 230.0

    pa = FLAG["hueAnglePercentiles"]
    ps = FLAG["saturPercentiles"]

    # Loop through subsections to find best estimate of water colour
    for k in range(FLAG["subImVert"]):
        for l in range(FLAG["subImHorz"]):
            if (
                    pa[k,l,0] > FLAG["Under"]
                    and pa[k,l,6] < FLAG["Upper"]
                    and pa[k,l,3] < best_estimate
                    and (pa[k,l,5]-pa[k,l,1]) > FLAG["noise"]
                    and (pa[k,l,5]-pa[k,l,1]) < FLAG["delta"]
                    and ps[k,l,3] > FLAG["satmin"]
            ):
                best_estimate = pa[k, l, 3] # Median again
                wk, wl = k, l # Set water value and coordinates

    try:
        best = pa[wk, wl, 3] # %   3=50 percentile

        closest = lib.config.FUE[ : , 3] - best # % calculate distance of all FU angles
        mini = np.absolute(closest).min() # % calculate the minimum distance
        # % find index where distance is minimum
        FUidx, = np.where(np.absolute(closest) == mini)[0]
        FUima = int(lib.config.FUE[FUidx, 0])

        product = dop[wk, wl]
        angle = anp[wk,wl]
        saturation = ps[wk, wl, 3] # %3=the median of the saturation value

        success = True
    except NameError:
        best = None
        FUima = None
        product = None
        angle = None
        saturation = None
        wk = None
        wl = None
        success = False

    # Assign best subimage to FLAG
    FLAG["subNumX"] = wk
    FLAG["subNumY"] = wl

    # Simple calculation of the sections in the centre
    MSUM = int(FLAG["subImVert"]/2)-1
    MSUN = int(FLAG["subImHorz"]/2)-1
    central_mean = 0.25 * (pa[MSUM, MSUN, 3] + pa[MSUM+1, MSUN, 3]
                           + pa[MSUM, MSUN+1, 3] + pa[MSUM+1, MSUN+1, 3])

    # Assign all important values to FLAG
    FLAG["FUvalue"] = FUima
    FLAG["hueAngleDeg"] = best
    FLAG["saturDist"] = saturation
    FLAG["centralMean"] = central_mean
    FLAG["dotProduct"] = product
    FLAG["cosAngle"] = angle
    FLAG["success"] = success

def find_water_colour(image_path, illum):
    # Make a copy of the config FLAG variable
    FLAG = lib.config.FLAG.copy()

    # Read the image and extract the information
    full, x_width, y_height  = loadIMAGE(image_path)

    # Start here the loop over the sections in the image and retrieve stats
    # Determine the width & height of the subimages in pixels
    x_sub_width = x_width // FLAG["subImVert"]
    y_sub_height = y_height // FLAG["subImHorz"]

    dop = np.zeros((FLAG["subImVert"], FLAG["subImHorz"]))
    anp = np.zeros((FLAG["subImVert"], FLAG["subImHorz"]))

    # Vector with percentile values
    p = np.array([5, 10, 25, 50, 75, 90, 95])
    pa = np.zeros((FLAG["subImVert"], FLAG["subImHorz"], len(p)))
    ps = np.zeros((FLAG["subImVert"], FLAG["subImHorz"], len(p)))

    # Loop over subimages
    for sx in range(FLAG["subImVert"]): # Subsections in the x-direction
        for sy in range(FLAG["subImHorz"]): # Subsections in the y-direction
            # Calculate the corners
            xlo = sx * x_sub_width
            xhi = ((sx + 1) * x_sub_width) - 1
            ylo = sy * y_sub_height
            yhi = ((sy + 1) * y_sub_height) - 1
             # Subselect the sub image
            sRGB = full[xlo:xhi+1, ylo:yhi+1, :]
            # Determine the length of the vector and angle relative to white vector
            (dp, av, hue_angle, saturation) = wacodi_core(
                                                sRGB,
                                                lib.config.EILL_VECTOR[illum],
                                                p,
                                                FLAG)

            dop[sx, sy] = dp
            anp[sx, sy] = av

            # Calculate the percentiles of the colour angle distribution
            pa[sx, sy, : ] = hue_angle
            ps[sx, sy, : ] = saturation

    # Put the percentiles of hue angle and saturations in FLAG
    FLAG["hueAnglePercentiles"] = pa
    FLAG["saturPercentiles"] = ps

    # Select the best colour based on the histograms
    Go4True(dop, anp, FLAG)

    # Return the FLAG variable
    return FLAG
