import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
import logging
import sys


def create_logger(logfile=None):
    # create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    if logfile:
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def categorical_palette(num_cat=9, continuous=False, cmap="tab10", cmap_num_cat=5):
    """
    Author: ImportanceOfBeingEarnest
    Link: https://stackoverflow.com/a/47232942
    """

    num_sub_cat = 1

    # if there are more data categories than cmap categories
    if num_cat > cmap_num_cat:
        # Determine subcategories
        num_sub_cat = math.ceil(num_cat / cmap_num_cat)

    # Main palette for the categories
    cat_cmap = plt.get_cmap(cmap)

    if continuous:
        cat_colors = cat_cmap(np.linspace(0, 1, num_cat))
    else:
        cat_colors = cat_cmap(np.arange(num_cat, dtype=int))

    # Template out empty matrix to hold colors
    color_palette = np.zeros((num_cat * num_sub_cat, 3))

    # Iterate through the main colors
    for i, color in enumerate(cat_colors):

        # Convert the rgb color to hsv
        color_rgb = color[:3]
        color_hsv = colors.rgb_to_hsv(color_rgb)

        # Create the colors for the sub-categories
        color_hsv_subcat = np.tile(color_hsv, num_sub_cat).reshape(num_sub_cat, 3)

        # Keep hue the same
        # Decrease saturation to a minimum of 0.25
        saturation = np.linspace(color_hsv[1], 0.25, num_sub_cat)
        # Increase lightness to a maximum of 1.0
        lightness = np.linspace(color_hsv[2], 1, num_sub_cat)

        # Update the subcat hsv
        color_hsv_subcat[:, 1] = saturation
        color_hsv_subcat[:, 2] = lightness

        # Convert back to rgb
        rgb = colors.hsv_to_rgb(color_hsv_subcat)

        # Update the template color palette
        matrix_start = i * num_sub_cat
        matrix_end = (i + 1) * num_sub_cat
        color_palette[matrix_start:matrix_end, :] = rgb

    return color_palette
