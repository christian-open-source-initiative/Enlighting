"""Main render function."""

import os
import glob

from hashlib import md5
from random import randint


# Pillow
from PIL import Image, ImageOps

# pandas
import pandas as pd

# enlight
import enlight.utils as utils
import enlight.image_tools as itools

SUPPORTED_IMAGE_FORMATS = ["jpg", "png"]
SUPPORTED_FONT_FORMATS = ["ttf"]
DEFAULT_FONT = "ArchivoBlack-Regular.ttf"

def create_folder_or_get_path(fpath):
    if not os.path.exists(fpath):
        os.makedirs(fpath)

    return fpath

def load_fonts(font_fpath, supported_formats=SUPPORTED_FONT_FORMATS):
    results = []
    for format in supported_formats:
        results += list(glob.glob(os.path.join(font_fpath, f"*.{format}")))
    return results

def render(
    images_fpath: str,
    output_fpath: str,
    fonts_fpath: str,
    input_csv: str,
    render_style: str = "auto",
    escape_string: str = "\\",
    font: str = DEFAULT_FONT,
    font_size: int = 200,
    tab_width: int = 4,
    force: bool = False
):
    # Generate folder if not already
    create_folder_or_get_path(images_fpath)
    create_folder_or_get_path(output_fpath)
    create_folder_or_get_path(fonts_fpath)

    # Image loading
    image_names = utils.load_image_names(images_fpath)
    print(f"Images loaded {len(image_names)}")

    if len(image_names) == 0:
        print(f"Unable to find supported images. Image files supported: {SUPPORTED_IMAGE_FORMATS}")
        raise RuntimeError(f"No images loaded in: {images_fpath}")

    # Font loading
    fonts = load_fonts(fonts_fpath)

    if len(fonts) == 0:
        print(f"Unable to find valid fonts. Font files supported: {SUPPORTED_FONT_FORMATS}")
        raise RuntimeError(f"Provided path contains no valid fonts: {fonts_fpath}")

    if not any(font == os.path.split(f)[1] for f in fonts):
        raise RuntimeError(f"No specified font in font path: {font}")

    # Load CSV file
    input_data = pd.read_csv(input_csv, escapechar=escape_string)

    print("Loaded CSV file:")
    print(input_data)

    if len(input_data) == 0:
        raise RuntimeError(f"No valid CSV loaded in: {input_csv}")

    # Generate the image
    style_column = 3
    quotes_column = 2
    source_column = 1
    image_column = 0
    font_fpath = os.path.join(fonts_fpath, font)
    for _, row in input_data.iterrows():
        quote = row[quotes_column].replace("\\n", "\n")
        source = row[source_column]
        style = row[style_column] if render_style == "auto" else render_style
        image_fpath = str(row[image_column])

        # Sanitize and use random otherwise
        if image_fpath is None or image_fpath == "nan" or len(image_fpath) == 0:
            image_fpath = image_names[randint(0, len(image_names) - 1)]
        else:
            image_fpath = os.path.join(images_fpath, image_fpath)

        if style is None or style == "nan" or len(style) == 0:
            style = utils.RENDER_STYLE[:-1][randint(0, len(utils.RENDER_STYLE) - 2)]

        img = Image.open(image_fpath)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGBA")
        img_size = img.size
        img_box = itools.Box(0, 0, img_size[0], img_size[1])

        # Generate unique output fpath
        uid = md5(source.encode()).hexdigest()[0:6]
        output_fpath_mod = os.path.join(output_fpath, uid + ".jpg")
        if os.path.exists(output_fpath_mod) and not force:
            raise RuntimeError(f"Output already exists for {output_fpath_mod}. Consider use --force to overwrite.")

        # Generate transparent overlay
        overlay_region = itools.calculate_margin_style(img_box, style, 0.05)
        img = itools.draw_rect(img, overlay_region, color=(0, 0, 0), transparency=0.45)

        # Generate text
        text_region = itools.calculate_margin_percentage(overlay_region, 0.1)
        itools.draw_text_box(img,
                             text_region,
                             quote + " \n\n" + source,
                             font_fpath,
                             target_percentage=0.055,
                             tab_space = tab_width,
                             font_range=(0, font_size))

        # Save final result
        img = img.convert("RGB")
        img.save(output_fpath_mod)