"""
Adds image helper tools.
"""

from PIL import Image, ImageFont, ImageDraw

class Box:
    """Helper class for drawing boxes."""
    def __init__(self, x, y, x2, y2):
        assert x < x2
        assert y < y2

        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2

    def overlaps(self, other):
        x_overlaps = self.x2 >= other.x and other.x2 >= self.x
        y_overlaps = self.y2 >= other.y and other.y2 >= self.y
        return x_overlaps and y_overlaps

    def contains(self, other):
        x_contains = self.x2 > other.x2 and self.x < other.x
        y_contains = self.y2 > other.y2 and self.y < other.y
        return x_contains and y_contains

    def width(self):
        return self.x2 - self.x

    def height(self):
        return self.y2 - self.y

    def center(self):
        return (self.x + self.width() / 2, self.y + self.height() / 2)

    def clone(self):
        return Box(self.x, self.y, self.x2, self.y2)

    def region_half_x(self):
        """Returns two boxes half the X values"""
        min_x = self.clone()
        min_x.x2 = (min_x.x2 / 2.0)

        max_x = self.clone()
        max_x.x = (max_x.x2 / 2.0)

        return (min_x, max_x)

    def region_half_y(self):
        """Returns two boxes half the Y values"""
        min_y = self.clone()
        min_y.y2 = (min_y.y2 / 2.0)

        max_y = self.clone()
        max_y.y = (max_y.y2 / 2.0)

        return (min_y, max_y)

# Helpers to calculate box render regions #
def calculate_margin_percentage(box: Box, percent: float) -> Box:
    assert percent >= 0 and percent <= 1.0
    margin_x = int(box.width() * percent)
    margin_y = int(box.height() * percent)
    return calculate_margin(box, margin_x, margin_y)

def calculate_margin(box: Box, margin_x: int, margin_y: int) -> Box:
    """Calculates margin box from given main box."""
    margin_box = Box(box.x + margin_x,
                     box.y + margin_y,
                     box.x2 - margin_x,
                     box.y2 - margin_y)
    assert box.contains(margin_box)
    return margin_box

# Draw helpers #
def draw_rect(img: Image, box: Box, color: tuple, transparency: float):
    """Draws rect at specified location. Assumes img is RGBA."""
    assert transparency >= 0 and transparency <= 1.0
    for i in color:
        assert i >= 0 and i <= 255

    # Require alpha_compositing to support JPG
    # https://stackoverflow.com/questions/43618910/pil-drawing-a-semi-transparent-square-overlay-on-image#43620169
    overlay = Image.new("RGBA", img.size, color + (0, ))
    opacity = int(255 * transparency)
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle((box.x, box.y, box.x2, box.y2), fill=color + (opacity, ))
    return Image.alpha_composite(img, overlay)

def draw_text_box(
    img: Image,
    box: Box,
    text: str,
    font_fpath: str,
    target_percentage: float = 0.034,
    tab_space: int = 4,
    color: tuple = (255, 255, 255),
    font_range: tuple = (1,1000)):
    """Draws text, as big as possible, in given textbox, unless font_size is specified."""

    for i in color:
        assert i >= 0 and i <= 255

    def _get_font_width_height(font, text):
        l, t, r, b = font.getbbox(text)
        w = r - l
        h = b - t
        return (w, h)

    def _largest(arr):
        maxv = ""
        for i in arr:
            if len(i) > len(maxv):
                maxv = i
        return maxv

    # First calculate smaller box that adheres to width constraints as possible
    # Operate in a fixed type font size by looking at percentage
    # Obtain a viable font.
    target_font = None
    for size in range(*font_range):
        target_font = ImageFont.FreeTypeFont(font_fpath, size=size)
        w, h = _get_font_width_height(target_font, "c")

        if w > box.width() * target_percentage or h > box.height() * target_percentage:
            target_font = ImageFont.FreeTypeFont(font_fpath, size=(size-1))
            break

    # Just a single letter to guestimate
    w, _ = _get_font_width_height(target_font, "c")

    # Insert newlines by guestimating
    words = text.split(" ")
    buffer = words.pop(0)
    lines = []
    while len(words) != 0:
        new_word = words.pop(0)
        has_newline = "\n" in new_word
        new_buffer = buffer + " " + new_word
        if (len(new_buffer) * w) > box.width() or has_newline:
            lines.append(buffer if has_newline else buffer + "\n")
            buffer = new_word
        else:
            buffer = new_buffer
    lines.append(buffer)
    modified_text = " " * tab_space
    modified_text += "".join(lines)
    max_line = _largest(lines)

    # Finally render inside everything inside the box.
    font = None
    for size in range(*font_range):
        font = ImageFont.FreeTypeFont(font_fpath, size=size)
        w, h = _get_font_width_height(font, max_line)

        if w > box.width() or h > box.height():
            font = ImageFont.FreeTypeFont(font_fpath, size=(size-1))
            break

    d = ImageDraw.Draw(img)
    d.text(box.center(), modified_text, fill=color, anchor="mm", font=font)
