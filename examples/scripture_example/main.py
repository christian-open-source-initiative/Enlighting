"""
Converts a csv of scripture references into quote images.
Uses Enlighten as a subroutine.
"""

import os
import sys
import re
import random
import argparse
import tempfile

# faker
from faker import Faker

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT_DIR, os.pardir, os.pardir))

# enlighten
from enlight.render import render
from enlight.ai.data_generator import PseudoRandomImageCSVDataGenerator

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

    parser.add_argument("--train", action="store_true", default=False, help="Check to see if in training mode.")
    parser.add_argument("--load-model", default="svm.pickle", help="Load model for inference.")
    parser.add_argument("--save-model", default="svm.pickle", help="Save model output location if in training mode.")

    return parser.parse_args()

def sanitize_output(v):
    v = re.sub(" +", " ", v)
    v = v.replace("\n", "")
    v = re.sub(";\w+", "; ", v)
    return v

def fake_text(batch, sentence_length, seed):
    fake = Faker()
    Faker.seed(seed)
    def _impl():
        for _ in range(256):
            name = f"{fake.first_name()} {fake.last_name()}"
            yield (name, fake.paragraph(nb_sentences=3))
    return _impl

def main():
    args = parse_args()

    # Render result and exit
    if not args.train:
        df = convert(args.input_csv, args.output_csv)

        # remove redundant spaces
        df["quote"] = df["quote"].map(sanitize_output)
        render(
            args.images_fpath,
            args.output_fpath,
            args.fonts_fpath,
            None,
            None,
            df=df,
            force=args.force
        )
        return

    # Start interactive session and train
    # This is training image dataset
    batch = 2
    seed = int(random.random() * 10**32)
    text_gen = fake_text(batch, 3, seed)
    generator = PseudoRandomImageCSVDataGenerator(int(random.random() * 10**32), text_gen, args.images_fpath, batch)
    data_df = generator.generate()

    # generate a folder with all the temp values
    with tempfile.TemporaryDirectory() as temp_dir:
        # Render
        names = render(
            args.images_fpath,
            temp_dir,
            args.fonts_fpath,
            None,
            None,
            df=data_df
        )

        filenames = [os.path.split(n)[1] for n in names]
        data_df.loc[:, "filenames"] = filenames

        print("A list of images have been generated at:")
        print(temp_dir)
        print("Delete the ones you don't want.")

        confirm = None
        while confirm != "y":
            confirm = input("Type y, e to exit and save: ")
            if confirm == "e":
                exit()

        new_files = os.listdir(temp_dir)
        data_df = data_df[data_df["filenames"].isin(new_files)]




if __name__ == "__main__":
    main()
