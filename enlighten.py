"""
Enlightening, an inspirational quote generator.
"""
# std
import os
import glob
import math
import random
import argparse

# enlight
import enlight.utils as utils

from enlight.image_tools import Box
from enlight.render import render

# PIL
from PIL import Image

def parse_args():
    parser = argparse.ArgumentParser(description="Generates quotes to images.")

    # Collage mode
    parser.add_argument("--collage", action="store_true", help="Generates a collage ontop of the general output.")
    parser.add_argument("--collage-scale", default=0.2, help="How large the collage should be relative to original images.", type=float)

    # Folders
    parser.add_argument("--fonts-fpath", default="fonts", help="Folder container valid fonts.")
    parser.add_argument("--output-fpath", default="output", help="Output folder.")
    parser.add_argument("--images-fpath", default="images", help="Default images folder.")

    # Files
    parser.add_argument("--input-csv", "-i", default="input.csv", help="Input CSV to generate file.")
    parser.add_argument("--escape-string", "-x", default="\\", help="CSV file valid escape character.")

    # Font loading
    parser.add_argument("--font", "-f", default="ArchivoBlack-Regular.ttf", help="Default font to use.")
    parser.add_argument("--font-size", default=200, help="Default font size, used as max value, not guranteed.", type=int)

    # Overwrite output files
    parser.add_argument("--force", action="store_true", default=False, help="Force overwrite output files.")

    # Auto tab
    parser.add_argument("--tab-width", default=4, help="Tab width (in spaces) for quotes. Set to 0 for no tabs.", type=int)

    # Style
    parser.add_argument("--render-style", "-r",
                        default="auto",
                        help="Type of render style. Auto defaults to csv encoding, otherwise uses AI.",
                        choices=utils.RENDER_STYLE)

    # AI files
    parser.add_argument("--ai-model-file",
                        default="models/svm_linear_train_in_group_only.pickle",
                        help="The model used for AI inference.")

    return parser.parse_args()

def collage(output_fpath, scale=0.2):
    """A quick and dirty way to build a collage. Useful for gauging how the AI is doing."""
    filename = "collage.jpg"

    generated_images = list(glob.glob(os.path.join(output_fpath, "*.jpg")))
    generated_images = [g for g in generated_images if filename not in g]
    load_images = [Image.open(i) for i in generated_images]
    image_sizes = [i.size for i in load_images]

    # Calculate nearest square
    square_sizes = int(max([max(*s) for s in image_sizes]) * scale)
    resized_images = [i.resize((square_sizes, square_sizes), resample=Image.NEAREST) for i in load_images]

    # Shuffle to make it more spicy
    random.shuffle(resized_images)

    # Generate phantom squares
    num_boxes = len(resized_images)
    dim = int(math.ceil(num_boxes**(1/2)))
    final_image = Image.new("RGBA", (square_sizes * dim, square_sizes * dim))
    leave_loop = False
    for x in range(dim):
        for y in range(dim):
            if x * dim + y >= num_boxes:
                leave_loop = True
                break
            img = resized_images[x * dim + y].convert("RGBA")
            final_image.paste(img, (x * square_sizes, y * square_sizes), img)

        if leave_loop:
            break

    final_image.convert("RGB").save(os.path.join(output_fpath, filename))

if __name__ == '__main__':
    args = parse_args()
    render(
        args.images_fpath,
        args.output_fpath,
        args.fonts_fpath,
        args.input_csv,
        args.ai_model_file,
        args.render_style,
        args.escape_string,
        args.font,
        args.font_size,
        args.tab_width,
        args.force,
        None
    )

    if args.collage:
        collage(args.output_fpath, args.collage_scale)
