"""
Generate general program sets.
"""

# std
import os
import sys
import uuid

from tempfile import TemporaryDirectory

import numpy as np

# Pillow
from PIL import Image, ImageOps

# perlin noise
from perlin_numpy import (
    generate_perlin_noise_2d
)

# pytest
import pytest

# Setup import path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(TEST_DIR, os.pardir))

GENERATE_IMAGE_COUNT = 5
GENERATE_IMG_RESOLUTION = (300, 400)

def pytest_addoption(parser):
    parser.addoption(
        "--workspace-fpath", default=None, help="Save and use provided workspace path."
    )

def generate_perlin_image(x, y):
    noise = generate_perlin_noise_2d((x, y), (10, 10))
    noise += 1
    noise *= 255 / 2
    noise = noise.astype(np.uint8)
    return Image.fromarray(noise, mode="L")

@pytest.fixture(scope="session")
def workspace_fpath(request):
    workspace = request.config.getoption("--workspace-fpath")
    if workspace is None:
        with TemporaryDirectory() as temp_dir:
            yield temp_dir
    else:
        if not os.path.exists(workspace):
            os.mkdir(workspace)
        else:
            assert len(os.listdir(workspace)) == 0, "Workspace folder should be empty."
        yield workspace

@pytest.fixture(scope="session")
def image_folder(workspace_fpath):
    image_fpath = os.path.join(workspace_fpath, "generated_images")
    os.mkdir(image_fpath)

    # Generate some random images with perlin noise
    for i in range(GENERATE_IMAGE_COUNT):
        img  = generate_perlin_image(*GENERATE_IMG_RESOLUTION)
        img_name = str(uuid.uuid1()) + ".jpg"
        img.save(os.path.join(image_fpath, img_name))

    yield image_fpath

