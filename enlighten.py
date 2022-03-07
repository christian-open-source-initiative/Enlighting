# std
import os
import glob
import argparse
from hashlib import md5

from random import randint

# Pillow
from PIL import Image, ImageFont, ImageDraw

# Pandas
import pandas as pd

# Enlighten
import image_tools as itools

SUPPORTED_IMAGE_FORMATS = ["jpg", "png"]
SUPPORTED_FONT_FORMATS = ["ttf"]

def parse_args():
    parser = argparse.ArgumentParser(description="Generates quotes to images.")

    # Folders
    parser.add_argument("--fonts-fpath", default="fonts", help="Folder container valid fonts.")
    parser.add_argument("--output-fpath", default="output", help="Output folder.")
    parser.add_argument("--images-fpath", default="images", help="Default images folder.")

    # Files
    parser.add_argument("--input-csv", "-i", default="input.csv", help="Input CSV to generate file.")
    parser.add_argument("--escape-string", "-x", default="\\", help="CSV file valid escape character.")

    # Font loading
    parser.add_argument("--font", "-f", default="ArchivoBlack-Regular.ttf", help="Default font to use.")
    parser.add_argument("--font-size", default=100, help="Default font size.", type=int)

    # Overwrite output files
    parser.add_argument("--force", action="store_true", default=False, help="Force overwrite output files.")

    return parser.parse_args()

def create_folder_or_get_path(fpath):
    if not os.path.exists(fpath):
        os.makedirs(fpath)

    return fpath

def load_image_names(images_fpath, supported_formats=SUPPORTED_IMAGE_FORMATS):
    results = []
    for format in supported_formats:
        results += list(glob.glob(os.path.join(images_fpath, f"*.{format}")))
    return results

def load_fonts(font_fpath, supported_formats=SUPPORTED_FONT_FORMATS):
    results = []
    for format in supported_formats:
        results += list(glob.glob(os.path.join(font_fpath, f"*.{format}")))
    return results

def main():
    args = parse_args()

    # Generate folder if not already
    create_folder_or_get_path(args.images_fpath)
    create_folder_or_get_path(args.output_fpath)
    create_folder_or_get_path(args.fonts_fpath)

    # Image loading
    image_names = load_image_names(args.images_fpath)
    print(f"Images loaded {len(image_names)}")

    if len(image_names) == 0:
        print(f"Unable to find supported images. Image files supported: {SUPPORTED_IMAGE_FORMATS}")
        raise RuntimeError(f"No images loaded in: {args.images_fpath}")

    # Font loading
    fonts = load_fonts(args.fonts_fpath)

    if len(fonts) == 0:
        print(f"Unable to find valid fonts. Font files supported: {SUPPORTED_FONT_FORMATS}")
        raise RuntimeError(f"Provided path contains no valid fonts: {args.fonts_fpath}")

    if not any(args.font == os.path.split(f)[1] for f in fonts):
        raise RuntimeError(f"No specified font in font path: {args.font}")

    # Load CSV file
    input_data = pd.read_csv(args.input_csv, escapechar=args.escape_string)

    print("Loaded CSV file:")
    print(input_data)

    if len(input_data) == 0:
        raise RuntimeError(f"No valid CSV loaded in: {args.input_csv}")

    # Generate the image
    quotes_column = 2
    source_column = 1
    image_column = 0
    for _, row in input_data.iterrows():
        quote = row[quotes_column]
        source = row[source_column]
        image_fpath = os.path.join(args.images_fpath, row[image_column])

        if image_fpath is None or len(image_fpath) == 0:
            image_fpath = image_names[randint(0, len(image_names - 1))]

        img = Image.open(image_fpath)
        img = img.convert("RGBA")
        img_size = img.size
        img_box = itools.Box(0, 0, img_size[0], img_size[1])

        # Generate unique output fpath
        uid = md5((quote + source).encode()).hexdigest()[0:6]
        output_fpath = os.path.join(args.output_fpath, uid + ".jpg")
        if os.path.exists(output_fpath) and not args.force:
            raise RuntimeError(f"Output already exists for {output_fpath}. Consider use --force to overwrite.")

        # Processing
        font = ImageFont.truetype(os.path.join(args.fonts_fpath, args.font), size=args.font_size)
        draw = ImageDraw.Draw(img)

        margin_region = itools.calculate_margin_percentage(img_box, 0.05)
        img = itools.draw_rect(img, margin_region, color=(0, 0, 0), transparency=0.4)

        # Save final result
        img = img.convert("RGB")
        img.save(output_fpath)

if __name__ == '__main__':
    main()