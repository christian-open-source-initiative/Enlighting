"""
Converts a csv of scripture references into quote images.
Uses Enlighten as a subroutine.

Also provides an interactive "generate" mode which allows for marking and training of data
for this domain.
"""

import os
import sys
import re
import pickle
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

# pandas
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description="Generates scripture quotes to images using AI.")

    parser.add_argument("--output-csv", help="Output to enlighten csv file.", default="enlighten.csv")

    parser.add_argument("--input-csv", help="Input to scripture csv file.", default="input.csv")
    parser.add_argument("--output-fpath", default="output", help="Output folder.")
    parser.add_argument("--images-fpath", help="Default images folder", default="images")
    parser.add_argument("--fonts-fpath", default="fonts", help="Folder container valid fonts.")
    parser.add_argument("--force", action="store_true", default=False, help="Force overwrite output files.")

    parser.add_argument("--generate", action="store_true", default=False, help="Interactive mode to train data.")
    parser.add_argument("--batch-size", "-b", default=256, help="Size of labels to generate at once.", type=int)

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
    if not args.generate:
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
    batch = args.batch_size

    look_up_table = None
    if os.path.exists("look_table.pickle"):
        with open("look_table.pickle", "r+b") as f:
            look_up_table = pickle.load(f)
            print(f"Lookup table loaded: {len(look_up_table)}")
    else:
        print("New lookup table.")
        look_up_table = {}

    # generate a folder with all the temp values
    feature_cache = {}
    while True:
        seed = int(random.random() * 10**32)
        text_gen = fake_text(batch, 3, seed)
        generator = PseudoRandomImageCSVDataGenerator(int(random.random() * 10**32), text_gen, args.images_fpath, batch - 1)
        generator._feature_cache = feature_cache
        data_df = generator.generate()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Render
            # Remove any we know to be valid
            data_df["drop"] = data_df["image"] + data_df["style"]
            not_sure_df = data_df[data_df["drop"].map(lambda v: v not in look_up_table or random.randint(0, 100) < 98)]
            sure_df = data_df[~data_df["drop"].isin(not_sure_df["drop"])]
            sure_no_df = sure_df[sure_df["drop"].map(lambda v: not look_up_table[v])]
            sure_yes_df = sure_df[sure_df["drop"].map(lambda v: look_up_table[v])]

            assert sure_no_df.shape[0] + sure_yes_df.shape[0] + not_sure_df.shape[0] == data_df.shape[0]
            print("Cache has eliminated: {}".format(sure_df.shape[0]))

            names = render(
                args.images_fpath,
                temp_dir,
                args.fonts_fpath,
                None,
                None,
                df=not_sure_df,
                force=True # incase there is collision
            )

            filenames = [os.path.split(n)[1] for n in names]
            not_sure_df.loc[:, "filenames"] = filenames

            print("A list of images have been generated at:")
            print(temp_dir)
            print("Delete the ones you don't want.")

            confirm = None
            while confirm != "y":
                confirm = input("Type y, e to exit: ")
                if confirm == "e":
                    exit()

            new_files = os.listdir(temp_dir)
            new_sure_df = not_sure_df[not_sure_df["filenames"].isin(new_files)]
            removed_not_sure_df = not_sure_df[~not_sure_df["drop"].isin(new_sure_df["drop"])]

            # Update lookup
            for _, row in new_sure_df.iterrows():
                look_up_table[row["drop"]] = True

            for _, row in removed_not_sure_df.iterrows():
                look_up_table[row["drop"]] = False

            data_df = pd.merge(new_sure_df, sure_df, how="outer")

            print()
            print("GENERATED: ")
            print(data_df)
            print()

            # Cannot train if only two result output for multiclass, must have atleast 3
            if data_df.size <= 2:
                continue

            # Write snapshot
            with open("look_table.pickle", "w+b") as f:
                pickle.dump(look_up_table, f)

            # Save feature cache across sessions
            feature_cache = generator._feature_cache

if __name__ == "__main__":
    main()
