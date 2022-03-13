"""
Generate general program sets.
"""

# std
import os
import sys
import uuid

from contextlib import contextmanager
from shutil import copytree
from tempfile import TemporaryDirectory

# numpy
import numpy as np

# Pillow
from PIL import Image

# perlin noise
from perlin_numpy import generate_perlin_noise_2d

# pytest
import pytest

# Setup import path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(TEST_DIR, os.pardir))

# enlight
from enlight.render import render

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
def workspace_cwd(workspace_fpath):
    @contextmanager
    def _workspace():
        old_dir = os.getcwd()
        try:
            os.chdir(os.path.abspath(workspace_fpath))
            yield
        finally:
            os.chdir(old_dir)

    return _workspace

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

@pytest.fixture(scope="session")
def output_folder(workspace_fpath):
    return os.path.join(workspace_fpath, "output")

@pytest.fixture(scope="session")
def ai_model_folder(workspace_fpath):
    return os.path.join(workspace_fpath, "model")

@pytest.fixture(scope="session")
def fonts_folder(workspace_fpath):
    dest =  os.path.join(workspace_fpath, "fonts")
    copytree(os.path.join(TEST_DIR, os.pardir, "fonts"), dest)
    return dest

@pytest.fixture(scope="session")
def enlighten_render_csv(image_folder, fonts_folder, ai_model_folder):
    """
    Helper wrapper function to wrap around render function.
    """
    def _render(input_csv, output_folder):
        render(
            image_folder,
            output_folder,
            fonts_folder,
            input_csv,
            os.path.join(ai_model_folder, "svm.pickle")
        )

    return _render
