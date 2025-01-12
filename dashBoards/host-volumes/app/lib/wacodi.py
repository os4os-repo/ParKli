import sys
from os import path
from glob import glob
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from lib.find_water_colour import find_water_colour

# % Main program
#  Application of the WACODI algorithm
#
# % ACKNOWLEDGEMENT
#
#  This software is an integral part of the article in L&O Methods.
#  Always acknowledge this article when using parts of this code.
#
#  Title:    WACODI: A generic algorithm to derive the intrinsic color of
#            natural waters from digital images
#  Authors: S. Novoa, M. Wernand and H.J. Van der Woerd
#
#  This software was written for the FP7 CITCLOPS project (2012-2015)
#  See more information on www.citclops.eu
#
#  Created by Hans van der Woerd on July 31 2014
#  Contact Hans via ResearchGate Hans J van der Woerd
#  Last Modification July 28 2015
#
# % Installation
#
#  Copy the WACODI.m code in your preferred directory
#  Create three sub directories : \in \out and \par
#  Copy the test images S14W and S16W to the \in directory
#  Copy the FUE.xls and Test_spectra.xlsx files into the \par directory
#  Copy all functions seperately as .m files to the main directory
#
#  run WACODI from the main directory
#  results will appear on screen and in the \out directory
#  The core output will be generated in the WACODI_dump.xlsx files
#  The best results are summarized in FLAG and written to WACODI_FLAG.xlsx
#
# % Functions called in order of appearance
#
#  loadSWITCH;   %Load the basic processing parameters
#  loadFUE;      %Load the x,y,z coordinates of the FU scale
#  loadNAMES     %Load the names of the images that should be processed
#  loadEill;     %Load the illumination vectors
#  Create_Eill   %Calculate the illumination vector from spectra
#  loadIMAGE     %Load the images from the jpg format
#  GammaI;       %Transform from sRGB to XYZ coordinates
#  LuminI;       %Correction for illumination and sky correction
#  Colouradapt;  %Accomplish the chromatic adaptation
#  XYZ2alpha;    %Transform from XYZ coordinates to the hue colour angle
#  Go4True;      %Selection of the true water colour
#  dumpDATA      %Write the results to an external file
#

# """ Load and define the basic data """
# % First the default values are loaded to be sure that the processing can
# % take place. The parameters, switches and flags are defined in here.
# % CAPITAL 3-letter acronyms are used for external setting parameters

# get the main processing parameters
#SDU, BRA, GAI, SUM, SUN, HSQ, DIS, ILL, CLO, XML, Mset = fs.loadSWITCH()

# load the x,y,z cooloadSWITCHrdinates of the Forel Ule (FU) scale
#This is in the config.py now, as a numpy array
#FUE = fs.loadFUE()

def dumpDATA(image_name, SDU, SUM, SUN, pa, ps, best,
             satur, product, angle, FUima, central_mean):
    # % function to write correctly the analysis
    # % This function can be much more extensive if required
    # %
    # % input:  imagename The name of the image
    # %         set The setting of the initial conditions
    # %         ....
    # %         pa  The percentiles wih colour angles of the subimages
    # %         ps  The percentiles wih distance from the white point of the subimages
    # %         best The true colour of the water
    # %         ....
    # % output: success Indicates if the analysis succeeded (1= YES)
    # %
    # % Here the output to the database with flagging

    # % Temporary output to excel, which makes it slow
    exit_data = np.zeros((20,40))
    exit_data[0, 0] = best
    exit_data[0, 1] = satur
    exit_data[1, 0] = product
    exit_data[2, 0] = angle
    exit_data[3, 0] = FUima
    exit_data[4, 0] = central_mean

    # % header of percentile blocks
    exit_data[0, 2] = 10
    exit_data[0, 12] = 50
    exit_data[0, 22] = 90

    # % percentile data of the colour angle
    exit_data[1:(SUM+1), 2:(SUN+2)] = pa[ : , : , 1] # % 10 percentile
    exit_data[1:(SUM+1), 12:(SUN+12)] = pa[ : , : , 3] # % 50 percentile
    exit_data[1:(SUM+1), 22:(SUN+22)] = pa[ : , : , 5] # % 90 percentile

    # % percentile data of the saturation
    exit_data[(SUM+1):(2*SUM+1), 2:(SUN+2)] = ps[ : , : , 1] # % 10 percentile
    exit_data[(SUM+1):(2*SUM+1), 12:(SUN+12)] = ps[ : , : , 3] # % 50 percentile
    exit_data[(SUM+1):(2*SUM+1), 22:(SUN+22)] = ps[ : , : , 5] # % 90 percentile
    # % header

    pd.DataFrame(exit_data).to_csv("out/{}_dump.csv".format(image_name))

# Run main program:
if __name__ == "__main__":
    # Process command line arguments
    args = sys.argv #array of command line arguments at runtime

    # Set illum to 'sunny' unless specified otherwise
    illum = "sunny"
    savedata = False
    for item in args:
        if "illum=" in item:
            illum = item.split("=")[-1]
            args.remove(item)
        if "savedata" in item:
            savedata = True
            args.remove(item)
        if ".csv" in item:
            csv = item
            args.remove(item)
        if path.isdir(item):
            args.remove(item)
            args.append(path.normpath(item + "*"))

    # Use file(s) specified by command line argument
    if len(args) > 1:
        image_path_array = []
        # Use glob if * did not expand
        for image in args[1:]:
            image_path_array.append(image)
            if "*" in image:
                image_path_array.remove(image)
                image_path_array.extend(glob(image))
    else: # All images
        image_path_array = glob("test_images/*.png")

    # Read in metadata for the 100 images with hue angle spectra
    if "test_images" in image_path_array[0]:
        image_data = pd.read_excel(
            "Hue_image connection.xlsx",
            sheet_name="list",
            skiprows=1,
            usecols=[0,2,4],
            names=["station", "hue_angle", "n_code"]
        ).fillna(method='ffill').set_index("n_code")

    # image_path_array is an array with names of the images
    # Loop over all the images
    for image_path in image_path_array:
        FLAG = find_water_colour(image_path, illum)

        image_filename = path.basename(image_path)
        image_name = path.splitext(image_filename)[0]

        try:
            # Add to fu_wacodi column of image_data if analysing the 100 images
            image_data.loc[int(image_name), "hue_wacodi"] = FLAG["hueAngleDeg"]
            image_data.loc[int(image_name), "central_mean"] = FLAG["centralMean"]
        except NameError:
            pass

        # Data are summarized at the screen, in a csv file and the FLAG results
        if savedata:
            # For developing purposes save some core output to a csv
            dumpDATA(image_name, FLAG["secchidisk"], FLAG["subImVert"],
                     FLAG["subImHorz"], FLAG["hueAnglePercentiles"],
                     FLAG["saturPercentiles"], FLAG["hueAngleDeg"],
                     FLAG["saturDist"], FLAG["dotProduct"], FLAG["cosAngle"],
                     FLAG["FUvalue"], FLAG["centralMean"])

            # Write the FLAG data to a csv
            pd.DataFrame.from_dict(
                FLAG,
                orient="index"
            ).to_csv("out/{}FLAG.csv".format(image_name))

        # Print basic results to the screen
        if FLAG["success"]:
            print("Image '{}' successfully processed:".format(image_filename))
            print("\tHue colour angle = {} degrees".format(FLAG["hueAngleDeg"]))
            print("\tFU index value = {}".format(FLAG["FUvalue"]))
        else:
            print("Image '{}' unsuccessfully processed".format(image_filename))
            print("")

        # Clear the Flag for the next image
        del FLAG

        # end of single image processing

    try:
        hue_plot = sns.scatterplot(
            data=image_data,
            x="hue_angle",
            y="hue_wacodi"
        )
        # plt.show()
        hue_plot.get_figure().savefig("out/hue_angle.png")
        plt.close()

        central_mean_plot = sns.scatterplot(
            data=image_data,
            x="hue_angle",
            y="central_mean"
        )
        # plt.show()
        central_mean_plot.get_figure().savefig("out/central_mean.png")
        plt.close()
    except NameError:
        print("No image metadata to compare to.")
