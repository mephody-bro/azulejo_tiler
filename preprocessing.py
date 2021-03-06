import os

from PIL import Image
import numpy as np

from azulejo import TILE_SIZE, DATA_DIR, CACHE_DIR


def preprocess():
    """Resize all images to same size and save it to"""
    show_dimensions()
    remove_duplicates()
    file_names = os.listdir(DATA_DIR)
    for image_name in reversed(sorted(file_names)):
        image = Image.open(DATA_DIR + image_name)
        resized = image.resize(TILE_SIZE)
        resized.save(CACHE_DIR + image_name)
    print(f"{len(file_names)} images converted to {TILE_SIZE[0]}x{TILE_SIZE[1]}")


def remove_duplicates():
    """Remove duplicates based on euristic rule"""
    prev_image = None
    for image_name in reversed(sorted(os.listdir(DATA_DIR))):
        image = Image.open(DATA_DIR + image_name)

        if prev_image is None:
            prev_image = image
            continue

        if image.size == prev_image.size:
            diff = np.array(image) - np.array(prev_image)
            if not np.any(diff):
                os.remove(DATA_DIR + image_name)
                print(image_name, "deleted")

        prev_image = image


def show_dimensions():
    """Print biggest and smallest image dimensions"""
    min_d = (10e6, 10e6)
    max_d = (0, 0)
    for image_name in os.listdir(DATA_DIR):
        image = Image.open(DATA_DIR + image_name)
        height, width = image.size

        if height*width > max_d[0]*max_d[1]:
            max_d = (height, width)
        if height*width < min_d[0]*min_d[1]:
            min_d = (height, width)

    print("Minimal dimensions", min_d)
    print("Maximal dimensions", max_d)


if __name__ == "__main__":
    preprocess()
