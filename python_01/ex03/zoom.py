from PIL import Image
import numpy as np
from load_image import ft_load
import matplotlib.pyplot as plt


def image_gray(image: np.array) -> np.array:
    """Convert an RGB image array to a 2D grayscale array (uint8)."""
    img_array_uint8 = image.astype(np.uint8)
    pil_img = Image.fromarray(img_array_uint8)
    gray_pil_img = pil_img.convert("L")
    return np.array(gray_pil_img)


def image_zoom(image: np.array, x_start: int, x_end: int,
               y_start: int, y_end: int):
    """Crop the grayscale image to rows x_start:x_end and columns
    y_start:y_end, print its shape and pixels, then display it."""
    gray = image_gray(image)
    zoom_img = gray[x_start:x_end, y_start:y_end, np.newaxis]
    print(f"New shape after slicing: {zoom_img.shape}")
    print(zoom_img)
    plt.imshow(zoom_img.squeeze(), cmap="gray")
    plt.show()


def main():
    """Load animal.jpeg, zoom into a 400x400 region and show it."""
    try:
        image = ft_load("animal.jpeg")
        image_zoom(image, 100, 500, 450, 850)

    except Exception as error:
        print(error)


if __name__ == '__main__':
    main()
