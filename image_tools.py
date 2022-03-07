"""
Adds image helper tools.
"""

from PIL import Image, ImageFont, ImageDraw

class Box:
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

# Helpers to calculate box render regions
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