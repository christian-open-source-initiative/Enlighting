"""
General utilities for the program.
"""

import os
import glob

SUPPORTED_IMAGE_FORMATS = ["jpg", "png"]
SUPPORTED_FONT_FORMATS = ["ttf"]
RENDER_STYLE = ["full",
                "bottom",
                "top",
                "left",
                "right",
                "quarter-top-left",
                "quarter-top-right",
                "quarter-bottom-right",
                "quarter-bottom-left",
                "auto"] # auto must be last

def load_image_names(images_fpath, supported_formats=SUPPORTED_IMAGE_FORMATS):
    results = []
    for format in supported_formats:
        results += list(glob.glob(os.path.join(images_fpath, f"*.{format}")))
    return results
