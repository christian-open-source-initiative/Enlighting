#############################################
# Project: Enlighting
# File: src\enlighten\render_html.py
# By: ProgrammingIncluded
# Website: ProgrammingIncluded.com
# Description: Converts a CSV of quotes and names
#     into a folder of html with the quotes in front.
#############################################

# std
import os
import re
import json
import uuid
import shutil
import random
import hashlib
import argparse
from os import listdir
from os.path import isfile, join
from textwrap import dedent

# ext
import pandas as pd
import numpy as np
from skimage.filters import gaussian
from PIL import Image
from faker import Faker

# argparse defaults
IMG_FOLDER = "images"
BLURRED_IMG_FOLDER = "blurred"
RENDER_FOLDER = "render_html"
COMMENT_COLUMN_IDX = 2
NAME_COLUMN_IDX = 1
IMAGE_COLUMN_IDX = 0

# EM measurements for rendering HTML
DEF_MAX_HEIGHT = 65
DEF_MIN_HEIGHT = 30
DEF_MAX_WIDTH = 65

# Different for each font
CHAR_CONVERSION_RATE_EM_TO_LEN = 2.0

# Image caching
IMAGE_HASH_MAPPING = {}

SAMPLE_FILE_NAME="sample.html"

def get_image_files(fpath=IMG_FOLDER):
    return [f for f in listdir(fpath) if isfile((join(fpath, f)))]

def gen_blurred_image(args, sigma=3):
    for non_blurred in get_image_files(fpath=args.raw_images):
        fpath = os.path.join("blurred", non_blurred)
        if not os.path.exists(fpath):
            image = Image.open(os.path.join(args.raw_images, non_blurred))
            im = np.array(image)
            im = im[:, :, ::-1]
            im = gaussian(im, sigma=sigma, multichannel=True)
            image.save(fpath)

def generate_dummy_data(fname, max_count=100):
    fake = Faker()

    def get_paragraph():
        return fake.text() + " " + fake.text() if random.randint(0, 1) == 0 else " ".join([fake.text() for i in range(3)])

    dummy = {
        "email": ["{}@gmail.com".format(fake.name().replace(" ", "")) for x in range(max_count)],
        "name": [fake.name() for x in range(max_count)],
        "text": [get_paragraph() for x in range(max_count)]
    }

    df = pd.DataFrame(dummy)
    with open(fname, "w") as f:
        df.to_csv(f, index=False)

def read_or_create_properties_json(hashmapping):
    """Properties are used to tag images with certain attributes to be rendered"""
    prop_filename = "properties.json"
    file_exists = os.path.exists("properties.json")
    is_mod = False
    with open(prop_filename, "r" if file_exists else "w") as f:
        if not file_exists:
            json.dump(hashmapping, f, indent=4, sort_keys=True)
            return hashmapping

        result = dict(json.load(f))
        print(hashmapping)
        for k, h in hashmapping.items():
            if h["filename"] not in result:
                result[k] = {"filename": h["filename"]}
                is_mod = True
    if is_mod:
        with open(prop_filename, "w") as f:
            json.dump(hashmapping, f, indent=4, sort_keys=True)
    return result

def hash_name(img_name):
    return hashlib.md5(img_name.encode()).hexdigest()[0:10]

def get_display_tag(index, name, text):

    if name is None:
        name = ""
    else:
        names = name.split()
        name = " ".join([n[0].upper() + n[1:] for n in names])
        name = "<br /><br />" + name

    result = """\
        <div class='content' id='{0}'>
            <div class='translucent'>
                {2}
                {1}
            </div>
        </div>
    """.format(index, name, text)
    return dedent(result)

def get_height_properties(text, css_custom):
    regex_max = re.search("max-height:\s*([0-9]+)\s*em;", css_custom)
    regex_min = re.search("min-height:\s*([0-9]+)\s*em;", css_custom)

    class HeightProp:
        def __init__(self, regex_min, regex_max):
            char_per_row = (DEF_MAX_WIDTH // CHAR_CONVERSION_RATE_EM_TO_LEN) + 1
            self.image_height = int((len(text) // char_per_row) * CHAR_CONVERSION_RATE_EM_TO_LEN) + 20
            self.max_height = int(regex_max.group(1)) if regex_max else DEF_MAX_HEIGHT
            self.min_height = int(regex_min.group(1)) if regex_min else DEF_MIN_HEIGHT

        def max_okay(self):
            return self.image_height < self.max_height

        def min_okay(self):
            return self.min_height <= self.image_height


    return HeightProp(regex_min, regex_max)


def get_custom_properties_for_image(img_name, prop):
    h = hash_name(img_name)
    css_custom = "\n".join(prop[h].get("css", []))

    return css_custom

def set_custom_properties_for_image(css, img_name, prop):
    h = hash_name(img_name)
    prop[h]["css"] = css
    return prop

def render(args):
    df = pd.read_csv(args.input_csv)

    template_file = ""
    with open(args.template_html) as f:
        template_file = f.read()

    with open(os.path.join(args.html_render_folder, SAMPLE_FILE_NAME), "wb") as f:
        # Grab the text column
        column_data_as_html = []
        names_data = []
        total_index = 0
        image_file_mapping = []
        for _, row in df.iterrows():
            uid = str(uuid.uuid1())[0:8]
            text = row[args.quote_column_idx]
            preprocess_text = text.strip().strip("\n")

            # If the text is too long, split the file into two slides or more
            max_slide_text = 512

            image_file_mapping.append(row[args.image_column_idx])
            slide_count = len(preprocess_text) // max_slide_text + 1
            if slide_count > 1:
                multi_slide_text = []
                buf = preprocess_text.split()
                slide = []
                count = 0

                # Split the text by spaces
                while len(buf) != 0:
                    word = buf.pop(0)
                    count += len(word)
                    slide.append(word)

                    if count >= max_slide_text:
                        multi_slide_text.append(" ".join(slide))
                        slide = []
                        count =  0

                # Add last element
                if len(slide) != 0:
                    multi_slide_text.append(" ".join(slide))

                # Process each slide as unique slide and add to lists
                for slide_text, idx in zip(multi_slide_text, range(len(multi_slide_text))):
                    html_text = get_display_tag(total_index, None if len(multi_slide_text) != (idx + 1) else row[args.name_column_idx], slide_text)
                    column_data_as_html.append(html_text.replace("\n", "<br />").strip())
                    names_data.append(row[args.name_column_idx] + "_{}_{}".format(uid, idx))
                    total_index += 1
            else:
                html_text = get_display_tag(total_index, row[args.name_column_idx], preprocess_text)
                column_data_as_html.append(html_text.replace("\n", "<br />").strip())
                names_data.append(row[args.name_column_idx] + "_{}".format(uid))
                total_index +=1

        image_files = get_image_files()
        image_files_hash = {hashlib.md5(k.encode()).hexdigest()[0:10]: {"filename": k} for k in image_files}
        # Generate special properties file if applicable
        prop = read_or_create_properties_json(image_files_hash)

        # For each text, specify a specific img
        for i in range(len(column_data_as_html)):
            if image_file_mapping[i] is None or image_file_mapping[i] == "":
                image_file_mapping[i] = random.choice(image_files)


        img_css_inject = []
        for i in range(len(image_file_mapping)):
            img_folder = IMG_FOLDER if random.randint(0, 1) == 0 else BLURRED_IMG_FOLDER
            css_custom = get_custom_properties_for_image(image_file_mapping[i], prop)

            # Set the custom properties once more only if it is not a duplicate
            cur_text = column_data_as_html[i]
            img_file = None
            html_column_data = None
            if (i - 1) >= 0 and names_data[i-1][:-11] in names_data[i]:
                img_file = image_file_mapping[i-1]
                image_file_mapping = image_file_mapping[:i] + [img_file] + image_file_mapping[i:]
                html_column_data = column_data_as_html[i-1]
            else:
                img_file = image_file_mapping[i]
                html_column_data = column_data_as_html[i]

                # Check if there is a max-height constraint
                # divide by 40 which is just grid column 65 - 20
                height_prop = get_height_properties(cur_text, css_custom)
                while not(height_prop.max_okay() and height_prop.min_okay()):
                    print("{} has a problem with its height when paired with given text".format(image_file_mapping[i]))
                    if not height_prop.max_okay():
                        print("\testimated height {}em but is programmed to have max height {}em".format(height_prop.image_height, height_prop.max_height))
                    if not height_prop.min_okay():
                        print("\testimated height {}em but is programmed to have min height {}em".format(height_prop.image_height, height_prop.min_height))

                    # Repick another image and try again
                    image_file_mapping[i] = random.choice(image_files)
                    print("\trepicked image to be {}".format(image_file_mapping[i]))
                    print("\n")
                    css_custom = get_custom_properties_for_image(image_file_mapping[i], prop)
                    height_prop = get_height_properties(cur_text, css_custom)

            re_height_prop = get_height_properties(html_column_data, get_custom_properties_for_image(img_file, prop))
            min_height_css = "min-height:{}em;".format(re_height_prop.min_height)
            max_height_css = "max-height:{}em;".format(re_height_prop.max_height)
            prop = set_custom_properties_for_image([min_height_css, max_height_css], img_file, prop)
            css_custom = get_custom_properties_for_image(img_file, prop)

            img_path = "file:///" + os.path.join(os.getcwd(), img_folder).replace("\\", "/")
            css_id = """\
                [id='#ID'] {
                    background-image: url(#IMG_FOLDER/#IMG_FILE);
                    background-size: 100% 100%;
                    background-repeat: no-repeat;
                    #CUSTOM
                }
            """.replace("#ID", str(i)).replace("#IMG_FOLDER", img_path).replace("#IMG_FILE", img_file).replace("#CUSTOM", css_custom)
            img_css_inject.append(dedent(css_id))


            # Write an individual html file for this specific image
            with open(os.path.join(args.html_render_folder, names_data[i].strip().replace(":", "_").replace(" ", "_") + ".html"), "w+b") as ind_f:
                ind_template_file = template_file.replace("#REPLACE_ME", "\n".join([column_data_as_html[i]]))
                ind_template_file = ind_template_file.replace("#ROW_COUNT", str(1))
                ind_template_file = ind_template_file.replace("#CUSTOM_ID_IMAGE", "\n".join([img_css_inject[i]]))
                ind_f.write(ind_template_file.encode("utf-8"))

        # Modify final template file
        final_template_file = template_file.replace("#REPLACE_ME", "\n".join(column_data_as_html))
        final_template_file = final_template_file.replace("#ROW_COUNT", str(len(column_data_as_html) // 2 + 1))
        final_template_file = final_template_file.replace("#CUSTOM_ID_IMAGE", "\n".join(img_css_inject))
        f.write(final_template_file.encode("utf-8"))

        # Copy the image folders into render_html
        if os.path.exists(os.path.join(args.html_render_folder, "blurred")):
            shutil.rmtree(os.path.join(args.html_render_folder, "blurred"))
        if os.path.exists(os.path.join(args.html_render_folder, "images")):
            shutil.rmtree(os.path.join(args.html_render_folder, "images"))

        shutil.copytree("blurred", os.path.join(args.html_render_folder, "blurred"))
        shutil.copytree("images", os.path.join(args.html_render_folder, "images"))

def get_argument_parser(parser=argparse.ArgumentParser(prog="render", description="Renders CSV data into HTML files.")):
    parser.add_argument("--raw-images", help="File containing various raw images.", default=IMG_FOLDER)
    parser.add_argument("--html-render-folder", help="Path to the image renderer", default=RENDER_FOLDER)
    parser.add_argument("--template-html", help="Path to the template HTML for rendering", default="templates/template.html")
    parser.add_argument("--input-csv", help="Path to the CSV file containing quotes and names", default="input.csv")
    parser.add_argument("--name-column-idx", help="The default index of column in CSV that contains the names", default=NAME_COLUMN_IDX, type=int)
    parser.add_argument("--quote-column-idx", help="The defualt index of the column in CSV that contains the quotes", default=COMMENT_COLUMN_IDX, type=int)
    parser.add_argument("--image-column-idx", help="Specific a specific image for this render.", default=IMAGE_COLUMN_IDX, type=int)
    return parser

def parse_args():
    return get_argument_parser().parse_args()

def create_output_folder(args):
    # Clean the output folder and create it if it doesn't exist
    if os.path.exists(args.html_render_folder):
        shutil.rmtree(args.html_render_folder)
        os.mkdir(args.html_render_folder)

def main():
    script_path = os.path.dirname(os.path.abspath(__file__))

    # Set the CWD to the scripts folder.
    os.chdir(script_path)
    args = parse_args()

    # Generate all the necessary output folders
    create_output_folder(args)

    # Generate blurred images
    gen_blurred_image(args)

    # You can optinoally use generate_dummy_data to generate dummy data before rendering
    # generate_dummy_data("input.csv")
    render(args.input_csv, args)

if __name__ == "__main__":
    main()
