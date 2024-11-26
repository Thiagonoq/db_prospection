import colorsys
import re

import webcolors


def is_hex(color):
    return re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)

def is_css_rgb(color):
    return re.match(r'^rgb\((\d{1,3}), (\d{1,3}), (\d{1,3})\)$', color)

def extract_rgb_from_css(color):
    return tuple(map(int, re.match(r'^rgb\((\d{1,3}), (\d{1,3}), (\d{1,3})\)$', color).groups()))

def to_hsl(color):
    rgb = None

    if is_hex(color):
        rgb = tuple(webcolors.hex_to_rgb(color))

    if is_css_rgb(color):
        rgb = extract_rgb_from_css(color)

    if re.match(r'^[a-zA-Z]+$', color):
        rgb = tuple(webcolors.name_to_rgb(color))

    if rgb is None:
        raise ValueError('Invalid color')

    h, s, v = colorsys.rgb_to_hsv(*tuple(map(lambda x: x / 255, rgb)))

    return round(h * 360), round(s * 100), round(v * 100)
