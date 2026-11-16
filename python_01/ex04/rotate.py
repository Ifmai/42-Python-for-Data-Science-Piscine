import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from load_image import ft_load


def image_gray(image: np.array) -> np.array:
    """Convert an RGB image array to a 2D grayscale array (uint8)."""
    img_array_uint8 = image.astype(np.uint8)
    pil_img = Image.fromarray(img_array_uint8)
    gray_pil_img = pil_img.convert("L")
    return np.array(gray_pil_img)

def transpose_image(image: np.array) -> np.array:
    h = len(image)
    w = len(image[0])
    result = []
    for j in range(w -1, -1, -1):
        new_row = []
        for i in range(h):
            new_row.append(image[i][j])
        result.append(new_row)
    return np.array(result)


def rotate_image(image: np.array, x_start: int, x_end: int,
               y_start: int, y_end: int):
    """Crop the grayscale image to rows x_start:x_end and columns
    y_start:y_end, print its shape and pixels, then display it."""
    print(image)
    gray = image_gray(image)
    gray = gray[x_start:x_end, y_start:y_end, np.newaxis]
    transpose_img = transpose_image(gray)
    print(f"New shape after Transpose: {transpose_img.shape}")
    print(transpose_img)
    plt.imshow(transpose_img.squeeze(), cmap="gray")
    plt.show()


def main():
    try:
        image = ft_load("animal.jpeg")
        rotate_image(image, 100, 500, 450, 850)

    except Exception as error:
        print(error)


if __name__ == '__main__':
    main()