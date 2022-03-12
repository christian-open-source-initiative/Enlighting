"""
Tests the data generator class and uses render() as subroutine so implicitly tests
render function.
"""

import os
import random

from conftest import GENERATE_IMAGE_COUNT

# pytest
import pytest

# pandas
import pandas as pd

# faker
from faker import Faker

# enlight
from enlight.ai.data_generator import PseudoRandomImageCSVDataGenerator

@pytest.fixture(scope="session")
def basic_text_generator(seed):
    print(f"faker generator seed: {seed}")
    def generator():
        fake = Faker()
        Faker.seed(seed)
        def _impl():
            for _ in range(5):
                name = f"{fake.first_name()} {fake.last_name()}"
                yield (name, fake.paragraph(nb_sentences=3))
        return _impl
    return generator

@pytest.fixture(scope="session")
def seed():
    """
    Testing seed for the given session.
    """
    seed = random.randint(0, 10**32)
    print(f"SESSION SEED: {seed}")
    return seed

def test_pseudo_random_generator(enlighten_render_csv, basic_text_generator, workspace_fpath, image_folder, seed):
    """
    Tests the PseudoRandomImageCSVDataGenerator class.
    """
    max_data = 256
    output_filenames = ["prg_one.csv", "prg_two.csv", "once_more.csv"]
    output_filenames = [os.path.join(workspace_fpath, fpath) for fpath in output_filenames]

    frames = []
    for filename in output_filenames:
        csv_generator = PseudoRandomImageCSVDataGenerator(seed, basic_text_generator(), image_folder, max_data)
        csv_generator.generate_csv(filename)
        csv_file = pd.read_csv(filename)
        print(csv_file)
        frames.append(csv_file)

    for idx, df in enumerate(frames):
        for df_t in frames[idx:]:
            assert df.equals(df_t), "Not all CSV files are the same for same seeds."

    # Load one of the files and generate some sample output
    output_path = os.path.join(workspace_fpath, "psuedo_random_generator_output")
    os.mkdir(output_path)
    enlighten_render_csv(output_filenames[0], output_path)

def test_image_folder_count(image_folder):
    assert GENERATE_IMAGE_COUNT == len(os.listdir(image_folder))
