import numpy as np
from PIL import Image
import os


def check_file(path: str) -> None:
    """Raise an error if path is not an existing, readable file."""
    if not isinstance(path, str) or not path:
        raise ValueError("path must be a non-empty string")
    if not os.path.exists(path):
        raise FileNotFoundError(f"no such file: {path}")
    if not os.path.isfile(path):
        raise IsADirectoryError(f"not a file: {path}")
    if not os.access(path, os.R_OK):
        raise PermissionError(f"permission denied: {path}")


def ft_load(path: str) -> np.array:
    """Load a JPEG image and return its RGB pixels as a numpy array."""
    check_file(path)
    image = Image.open(path)
    if image.format != 'jpg' and image.format != 'JPEG':
        raise TypeError("image type only jpg or jpeg")
    np_image = np.array(image.convert("RGB"))
    print(f"The shape of image is: {np_image.shape}")
    return np_image


def main():
    """Load animal.jpeg and print its pixels."""
    try:
        print(ft_load("animal.jpeg"))
    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
