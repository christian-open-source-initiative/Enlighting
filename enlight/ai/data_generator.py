"""
Generates training data for our CSV file.
"""

import os
import random
import hashlib

from abc import ABC, abstractmethod
from contextlib import contextmanager
from types import GeneratorType

# pandas
import pandas as pd

# enlight
import enlight.utils as utils

class EnlightCSVDataGenerator(ABC):
    """
    Generates data from the CSV file. Requires a text generator
    class that yields text. Generator can either go indefinitely.
    """

    fields = [
        "image",
        "quote_source",
        "quote",
        "style"
    ]

    def __init__(self,
                 text_generator: GeneratorType,
                 img_folder: str,
                 max_data: int = 256):
        """
        text_generator: A generator that returns tuples of (quote_source:str, quote:str).
        img_folder: Folder to the image folder required by enlighten.
        max_data: max amount of sample quotes to generate.
        """
        self.text_generator = text_generator
        self.image_folder = img_folder
        self.max_data = max_data

    def generate(self):
        """
        Returns a list of tuples with generated data.
        """

        # grab image lists
        img_names = utils.load_image_names(self.image_folder)
        img_names = [os.path.split(p)[1] for p in img_names]
        hash_lookup_img_names = {k: None for k in img_names}

        results = []
        for idx, (quote_source, quote) in enumerate(self.text_generator()):
            if idx > self.max_data:
                break

            image_name = self.image_select(img_names, quote_source, quote)
            style = self.style_select(img_names, quote_source, quote)

            if image_name is None:
                image_name = img_names[random.randint(0, len(img_names) - 1)]

            assert image_name in hash_lookup_img_names, "Provided image is not a valid image name."
            results.append(dict(zip(self.fields, (image_name, quote_source, quote, style))))
        return pd.DataFrame.from_records(results)

    def generate_csv(self, output_fpath):
        """
        Generates the csv file with max_data specified in class.
        """
        result = self.generate()
        result.to_csv(output_fpath, index=False)

    @abstractmethod
    def image_select(self, img_list, quote_source, quote):
        """Select an image from the list of images given a quote."""

    @abstractmethod
    def style_select(self, img_list, quote_source, quote):
        """Selects a style."""

class PseudoRandomImageCSVDataGenerator(EnlightCSVDataGenerator):
    """
    Selects a random image given a quote.
    Using the seed, a quote + quote source will always provide the same image.

    Best use-case is to instantiate a new class instance every N generator data
    with a new-seed to ensure true randomness.
    """

    def __init__(self, seed: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Starting seed
        self.seed = seed
        self._internal_seed = seed

    @contextmanager
    def new_seed(self, seed=0):
        """
        Returns new seed and then updates internal state.
        Can also seed the seed as it generates for more randomness.
        """
        random.seed(seed)
        yield
        # set the next state of the seed as part of the value
        self._internal_seed = int(random.random() * 10**32)

    def image_select(self, img_list, quote_source, quote):
        """
        Random selects an image
        """

        # The internal seed is from the prior random value
        # this gurantees that a new generator class created
        # will always be the same sequence of values for any given session.
        final_str = quote_source + quote + str(self._internal_seed)

        hash_val = hashlib.sha256(final_str.encode("utf-8")).hexdigest()

        # Consistent hash across python instances
        with self.new_seed(int(hash_val, 16) % 10 **32):
            rand_index = random.randint(0, len(img_list) - 1)
            selected_img = img_list[rand_index]

        return selected_img

    def style_select(self, img_list, quote_source, quote):
        # The internal seed is from the prior random value
        # this gurantees that a new generator class created
        # will always be the same sequence of values for any given session.
        final_str = quote_source + quote + str(self._internal_seed)

        # Consistent hash across python instances
        hash_val = hashlib.sha256(final_str.encode("utf-8")).hexdigest()

        # Consistent hash across python instances
        with self.new_seed(int(hash_val, 16) % 10 **32):
            rand_index = random.randint(0, len(utils.RENDER_STYLE) - 2)
            selected_style = utils.RENDER_STYLE[rand_index]

        return selected_style
