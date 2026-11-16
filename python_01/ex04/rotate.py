import contextlib
import io
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from load_image import ft_load


def check_image(image: np.ndarray) -> None:
    """Raise an error if image is not a non-empty (H, W, 3) uint8 array."""
    if not isinstance(image, np.ndarray):
        raise TypeError("image must be a numpy array")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"image must have shape (H, W, 3), "
                         f"got {image.shape}")
    if image.size == 0:
        raise ValueError("image is empty")
    if image.dtype != np.uint8:
        raise TypeError(f"image dtype must be uint8, got {image.dtype}")


def check_area(image: np.ndarray, x_start: int, x_end: int,
               y_start: int, y_end: int) -> None:
    """Raise an error if the crop bounds are not ints inside the image."""
    bounds = {"x_start": x_start, "x_end": x_end,
              "y_start": y_start, "y_end": y_end}
    for name, value in bounds.items():
        if type(value) is not int:
            raise TypeError(f"{name} must be an int, "
                            f"got {type(value).__name__}")
    height, width = image.shape[:2]
    if not 0 <= x_start < x_end <= height:
        raise ValueError(f"rows must satisfy 0 <= x_start < x_end <= "
                         f"{height}, got {x_start}:{x_end}")
    if not 0 <= y_start < y_end <= width:
        raise ValueError(f"columns must satisfy 0 <= y_start < y_end <= "
                         f"{width}, got {y_start}:{y_end}")


def image_gray(image: np.ndarray) -> np.ndarray:
    """Convert an RGB image array to a 2D grayscale array (uint8)."""
    return np.array(Image.fromarray(image).convert("L"))


def transpose_image(image: np.ndarray) -> np.ndarray:
    """Return the transpose of a 2D array, built by hand
    (no numpy transpose / .T / rot90)."""
    if not isinstance(image, np.ndarray) or image.ndim != 2:
        raise ValueError("transpose_image expects a 2D numpy array")
    height, width = image.shape
    result = np.empty((width, height), dtype=image.dtype)
    for i in range(height):
        for j in range(width):
            result[j, i] = image[i, j]
    return result


def rotate_image(image: np.ndarray, x_start: int, x_end: int,
                 y_start: int, y_end: int) -> np.ndarray:
    """Cut rows x_start:x_end and columns y_start:y_end of the grayscale
    image, transpose it, print shapes and pixels, display and return it."""
    check_image(image)
    check_area(image, x_start, x_end, y_start, y_end)
    cut = image_gray(image)[x_start:x_end, y_start:y_end]
    print(f"The shape of image is: {cut[:, :, np.newaxis].shape} "
          f"or {cut.shape}")
    print(cut[:, :, np.newaxis])
    transposed = transpose_image(cut)
    print(f"New shape after Transpose: {transposed.shape}")
    print(transposed)
    plt.imshow(transposed, cmap="gray")
    plt.show()
    return transposed


def main():
    """Load animal.jpeg, cut a 400x400 square, transpose and show it."""
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            image = ft_load("animal.jpeg")
        rotate_image(image, 100, 500, 450, 850)
    except Exception as error:
        print(f"Error: {error}")


if __name__ == '__main__':
    main()
