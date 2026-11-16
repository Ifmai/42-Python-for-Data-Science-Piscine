import numpy as np
import matplotlib.pyplot as plt
from load_image import ft_load


def check_array(array: np.ndarray) -> None:
    """Raise an error if array is not a non-empty (H, W, 3) uint8 image."""
    if not isinstance(array, np.ndarray):
        raise TypeError("array must be a numpy array")
    if array.ndim != 3 or array.shape[2] != 3:
        raise ValueError(f"array must have shape (H, W, 3), "
                         f"got {array.shape}")
    if array.size == 0:
        raise ValueError("array is empty")
    if array.dtype != np.uint8:
        raise TypeError(f"array dtype must be uint8, got {array.dtype}")


def show(array: np.ndarray, title: str) -> None:
    """Display the image with a title."""
    plt.imshow(array)
    plt.title(title)
    plt.axis("off")
    plt.show()


def ft_invert(array: np.ndarray) -> np.ndarray:
    """Inverts the color of the image received."""
    check_array(array)
    result = 255 - array
    show(result, "Invert")
    return result


def ft_red(array: np.ndarray) -> np.ndarray:
    """Keeps only the red channel of the image received."""
    check_array(array)
    result = array * np.array([1, 0, 0], dtype=np.uint8)
    show(result, "Red")
    return result


def ft_green(array: np.ndarray) -> np.ndarray:
    """Keeps only the green channel of the image received."""
    check_array(array)
    result = array.copy()
    result[:, :, 0] = result[:, :, 0] - result[:, :, 0]
    result[:, :, 2] = result[:, :, 2] - result[:, :, 2]
    show(result, "Green")
    return result


def ft_blue(array: np.ndarray) -> np.ndarray:
    """Keeps only the blue channel of the image received."""
    check_array(array)
    result = array.copy()
    result[:, :, 0] = 0
    result[:, :, 1] = 0
    show(result, "Blue")
    return result


def ft_grey(array: np.ndarray) -> np.ndarray:
    """Converts the image received to greyscale (shape is kept)."""
    check_array(array)
    result = array.copy()
    result[:, :, 0] = array[:, :, 1]
    result[:, :, 2] = array[:, :, 1]
    show(result, "Grey")
    return result


def main():
    """Load animal.jpeg and apply every filter to it."""
    try:
        array = ft_load("animal.jpeg")
        print(array)
        show(array, "Original")
        ft_invert(array)
        ft_red(array)
        ft_green(array)
        ft_blue(array)
        ft_grey(array)
        print(ft_invert.__doc__)
    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
