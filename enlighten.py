# std
import os
import sys
import glob
import argparse


# Pillow
from PIL import ImageFont, ImageDraw

# Pandas
import pandas as pd

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
        image_fpath = row[image_column]


if __name__ == '__main__':
    main()