import os

import imgkit
import glob

RENDER_FOLDER = "render_html"
IMG_FOLDER = os.path.join("img_render")

if not os.path.exists(IMG_FOLDER):
    os.mkdir(IMG_FOLDER)

for html in glob.glob("{}/*.html".format(RENDER_FOLDER)):
    raw_filename = os.path.split(html)[-1]
    filename = os.path.splitext(raw_filename)[0]
    if filename == "sample":
        continue
    print(filename + ".jpg")
    option = {
        "width": 1920,
        "encoding": "utf-8",
        "enable-local-file-access": None
    }
    imgkit.from_file(html, os.path.join(IMG_FOLDER, filename + ".jpg"), options=option)