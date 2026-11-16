import numpy as np


def slice_me(family: list, start: int, end: int) -> list:
    """Print the shape of a 2D list and return the rows from start to end."""
    check_family(family)
    check_index(start, end)
    np_family = np.array(family)
    new_family = np_family[start:end]
    print("My shape is :", np_family.shape)
    print("My new shape is :", new_family.shape)
    return new_family.tolist()


def check_family(family: list) -> None:
    """Check that family is a 2D list of numbers with equal-length rows."""
    if type(family) is not list:
        raise TypeError("family must be a list.")
    if not all(type(row) is list for row in family):
        raise TypeError("Every row of family must be a list.")
    if len(set(len(row) for row in family)) > 1:
        raise ValueError("All rows must have the same length.")
    if np.array(family).ndim != 2:
        raise ValueError("Array not 2D")


def check_index(start: int, end: int) -> None:
    """Check that start and end are integers."""
    if type(start) is not int or type(end) is not int:
        raise TypeError("start and end must be integers.")


def main():
    """Test slice_me and handle exceptions."""
    try:
        family = [[1.80, 78.4],
                  [2.15, 102.7],
                  [2.10, 98.5],
                  [1.88, 75.2]]
        print(slice_me(family, 0, 2))
        print(slice_me(family, 1, -2))
    except (TypeError, ValueError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
