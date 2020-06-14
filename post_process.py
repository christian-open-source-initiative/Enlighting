import numpy as np
import os
import glob
from matplotlib import image

IMG_RENDER_FOLDER = "img_render"
IMG_FOLDER = "img_post"

if not os.path.exists(IMG_FOLDER):
    os.mkdir(IMG_FOLDER)

CUT_OFFSET_PX = 375
for jpg in glob.glob("{}/*.jpg".format(IMG_RENDER_FOLDER)):
    img = image.imread(jpg)
    max_y = img.shape[1]
    result = img[:, CUT_OFFSET_PX : max_y - CUT_OFFSET_PX, :]
    img_name = os.path.split(jpg)[-1]
    image.imsave("{}/{}".format(IMG_FOLDER, img_name), result)