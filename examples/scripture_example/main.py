"""
Converts a csv of scripture references into quote images.
Uses Enlighten as a subroutine.
"""

import os
import sys
import re
import argparse

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT_DIR, os.pardir, os.pardir))

# enlighten
from enlight.render import render

# scripture_example
from converter import convert

def parse_args():
    parser = argparse.ArgumentParser(description="Generates scripture quotes to images using AI.")

    parser.add_argument("--output-csv", help="Output to enlighten csv file.", default="enlighten.csv")

    parser.add_argument("--input-csv", help="Input to scripture csv file.", default="input.csv")
    parser.add_argument("--output-fpath", default="output", help="Output folder.")
    parser.add_argument("--images-fpath", help="Default images folder", default="images")
    parser.add_argument("--fonts-fpath", default="fonts", help="Folder container valid fonts.")

    parser.add_argument("--force", action="store_true", default=False, help="Force overwrite output files.")

    return parser.parse_args()

def sanitize_output(v):
    v = re.sub(" +", " ", v)
    v = v.replace("\n", "")
    v = re.sub(";\w+", "; ", v)
    return v

def main():
    args = parse_args()
    df = convert(args.input_csv, args.output_csv)

    # remove redundant spaces
    df["quote"] = df["quote"].map(sanitize_output)

    render(
        args.images_fpath,
        args.output_fpath,
        args.fonts_fpath,
        None,
        df=df,
        force=args.force
    )

if __name__ == "__main__":
    main()
