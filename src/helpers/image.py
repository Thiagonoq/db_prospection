import colorsys
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
import rembg
import requests
from PIL import Image as PILImage

import src.helpers.color as colorutils
from src.helpers.is_ import Is as is_

rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)


class ImageEffects(object):
    def __init__(self, image):
        self.image = image

    def colorize(self, color, shape="false"):
        try:
            hue, sout, _ = colorutils.to_hsl(color)
        except ValueError as e:
            if str(e) == "Invalid color":
                return self.image

        img = self.image.convert("RGBA")
        arr = np.array(np.asarray(img).astype("float"))

        hue = hue / 360
        sout = sout / 100

        r, g, b, a = np.rollaxis(arr, axis=-1)
        h, s, v = rgb_to_hsv(r, g, b)

        h = hue

        if shape == "true":
            s = sout

        r, g, b = hsv_to_rgb(h, s, v)

        new_img = PILImage.fromarray(np.dstack((r, g, b, a)).astype("uint8"), "RGBA")

        return new_img


class ImageTransformations(object):
    def __init__(self, image):
        self.image = image

    def removebg(self):
        self.image = rembg.remove(self.image)
        return self

    def crop(self):
        self.image = self.image.crop(self.image.getbbox())
        return self


class Image(object):
    def __init__(self, image):
        self.open(image)

        self.effects = ImageEffects(self.image)
        self.transformations = ImageTransformations(self.image)

    def _parse(self):
        if isinstance(self.image, PILImage.Image):
            return

        if isinstance(self.image, Path):
            self.image = PILImage.open(self.image)
            return

        if isinstance(self.image, str):
            if is_.url(self.image):
                req = requests.get(self.image)
                mime_type = req.headers["content-type"]

                if mime_type not in ["image/png", "image/jpeg"]:
                    return None

                self.image = PILImage.open(BytesIO(req.content))
            else:
                path = Path(self.image)

                if path.exists():
                    self.image = PILImage.open(self.image)

            return

        if isinstance(self.image, bytes) or isinstance(self.image, BytesIO):
            self.image = PILImage.open(self.image)
            return

        if isinstance(self.image, np.ndarray):
            self.image = PILImage.fromarray(self.image)
            return

        if isinstance(self.image, tuple):
            self.image = PILImage.fromarray(self.image)
            return

    def open(self, image):
        self.image = image
        self._parse()

        if not isinstance(self.image, PILImage.Image):
            raise TypeError("Image error - invalid type")

    @staticmethod
    def is_equal(image, filepath):
        original_image = cv2.imread(str(image))
        cached_image = cv2.imread(str(filepath))

        if original_image.shape == cached_image.shape:
            diff = cv2.subtract(original_image, cached_image)

            b, g, r = cv2.split(diff)

            if not (
                cv2.countNonZero(b) == 0
                and cv2.countNonZero(g) == 0
                and cv2.countNonZero(r) == 0
            ):
                return False
        else:
            return False

        return True

    @staticmethod
    def create_mask(processed_image):
        img = cv2.imread(str(processed_image), cv2.IMREAD_UNCHANGED)

        img[np.where((img[:, :, 3] >= 200))] = [255, 255, 255, 255]
        img[np.where((img[:, :, 3] < 200))] = [0, 0, 0, 255]

        return Image(img)

    @staticmethod
    def removebg_with_mask(original, mask):
        original_image = cv2.imread(str(original), cv2.IMREAD_UNCHANGED)
        mask_image = cv2.imread(str(mask), cv2.IMREAD_UNCHANGED)

        original_image[np.all(mask_image == [0, 0, 0, 255], axis=-1)] = [0, 0, 0, 0]

        return Image(original_image)

    @staticmethod
    def apply_blur_to_edges(image):
        original = cv2.imread(str(image), cv2.IMREAD_UNCHANGED)
        image = cv2.imread(str(image), cv2.IMREAD_UNCHANGED)

        kernelSizes = [(41, 41)]

        for kx, ky in kernelSizes:
            blurred = cv2.GaussianBlur(image, (kx, ky), 0)

            mask = np.zeros(image.shape, dtype=np.uint8)

            cv2.circle(
                mask,
                (int(image.shape[1] / 2), int(image.shape[0] / 2)),
                200,
                (255, 255, 255),
                -1,
                cv2.LINE_AA,
            )

            mask = cv2.GaussianBlur(mask, (kx, ky), 0)

            image = blurred * (mask / 255) + image * (1 - mask / 255)

        image[0 : original.shape[0], 0 : original.shape[1]] = original

        return Image(image)

    def __getattr__(self, name):
        return getattr(self.image, name)


def get_pixel_with_neighbors(img_array, x, y):
    neighbors = []
    height, width, _ = img_array.shape

    for i in range(max(0, x - 1), min(height, x + 2)):
        for j in range(max(0, y - 1), min(width, y + 2)):
            if i != x or j != y:
                neighbors.append(img_array[i, j])

    return neighbors


def check_if_border_pixel_is_dark(img_path: str):
    img = np.array(PILImage.open(img_path).convert("RGBA"))

    count_rgb_pixels = 0
    sum_brightness_pixels = 0

    for x, row in enumerate(img):
        for y, pixel in enumerate(row):
            _, _, _, a = pixel

            if a != 0:
                neighbors = get_pixel_with_neighbors(img, x, y)
                without_transparency = list(
                    filter(lambda pixel: pixel[3] != 0, neighbors)
                )

                has_transparency = (
                    len(list(filter(lambda pixel: pixel[3] == 0, neighbors))) > 0
                )

                if not has_transparency:
                    continue

                brightness_pixels = list(
                    map(
                        lambda pixel: sum([pixel[0], pixel[1], pixel[2]]) / 3,
                        without_transparency,
                    )
                )

                count_rgb_pixels += len(brightness_pixels)
                sum_brightness_pixels += sum(brightness_pixels)

    return True if (sum_brightness_pixels / count_rgb_pixels) >= (255 / 2) else False
