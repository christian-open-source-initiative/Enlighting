"""
Generates training data for our CSV file.
"""

import csv
import random
import hashlib

from types import GeneratorType
from abc import ABC, abstractmethod

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

    def generate_csv(self, output_fpath):
        """
        Generates the csv file with max_data specified in class.
        """
        # grab image lists
        img_names = utils.load_image_names(self.image_folder)
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
            results.append((image_name, quote_source, quote, style))

        with open(output_fpath, "w") as f:
            csv_writer = csv.DictWriter(f, fieldnames=self.fields, delimiter=",")
            csv_writer.writeheader()
            for r in results:
                csv_writer.writerow(dict(zip(self.fields, r)))

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

    def image_select(self, img_list, quote_source, quote):
        """
        Random selects an image
        """

        # The internal seed is from the prior random value
        # this gurantees consecutive calls to the same generator seed
        # produces the same values.
        final_str = quote_source + quote + str(self._internal_seed)

        # Consistent hash across python instances
        hash_val = hashlib.sha256(final_str.encode("utf-8")).hexdigest()
        random.seed(int(hash_val, 16) % 10**32)

        rand_index = random.randint(0, len(img_list) - 1)
        selected_img = img_list[rand_index]

        # set the next state of the seed as part of the value
        self._internal_seed = int(random.random() * 10**32)

        return selected_img

    def style_select(self, img_list, quote_source, quote):
        # The internal seed is from the prior random value
        # this gurantees consecutive calls to the same generator seed
        # produces the same values.
        final_str = quote_source + quote + str(self._internal_seed)

        # Consistent hash across python instances
        hash_val = hashlib.sha256(final_str.encode("utf-8")).hexdigest()
        random.seed(int(hash_val, 16) % 10**32)
        rand_index = random.randint(0, len(utils.RENDER_STYLE) - 2)
        selected_style = utils.RENDER_STYLE[rand_index]

        # set the next state of the seed as part of the value
        self._internal_seed = int(random.random() * 10**32)

        return selected_style
