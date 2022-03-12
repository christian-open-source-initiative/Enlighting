"""
Enlightening, an inspirational quote generator.
"""
# std
import argparse

# enlight
import enlight.utils as utils
from enlight.render import render

def parse_args():
    parser = argparse.ArgumentParser(description="Generates quotes to images.")

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
                        default="full",
                        help="Type of render style. Auto defaults to csv encoding, otherwise uses AI.",
                        choices=utils.RENDER_STYLE)

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    render(
        args.images_fpath,
        args.output_fpath,
        args.fonts_fpath,
        args.input_csv,
        args.render_style,
        args.escape_string,
        args.font,
        args.font_size,
        args.tab_width,
        args.force
    )
