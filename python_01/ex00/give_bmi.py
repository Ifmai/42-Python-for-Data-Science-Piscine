import numpy as np


def give_bmi(height: list[int | float],
             weight: list[int | float]) -> list[int | float]:
    """Calculates the BMI for each pair of height and weight."""
    check_type(height)
    check_type(weight)
    np_height = np.array(height)
    np_weight = np.array(weight)
    check_values(np_height, np_weight)
    return (np_weight / (np_height ** 2)).tolist()


def apply_limit(bmi: list[int | float], limit: int) -> list[bool]:
    """Returns a list of booleans: True if BMI exceeds the limit."""
    check_type(bmi)
    if type(limit) is not int:
        raise TypeError("Limit must be an integer.")
    np_bmi = np.array(bmi)
    return (np_bmi > limit).tolist()


def check_type(input_list: list) -> None:
    """Checks if all values in the list are either integers or floats."""
    if not all(type(x) in (int, float) for x in input_list):
        raise TypeError("All values in the list must be integers or floats.")


def check_values(height: np.ndarray, weight: np.ndarray) -> None:
    """Checks same shape and that all values are finite and positive."""
    if height.shape != weight.shape:
        raise ValueError("Height and weight arrays must have the same shape.")
    if np.any(height <= 0) or np.any(weight <= 0):
        raise ValueError(
            "Height and weight values must be greater than zero.")
    if not np.all(np.isfinite(height)) or not np.all(np.isfinite(weight)):
        raise ValueError("Height and weight must be finite numbers.")


def main():
    """Test BMI functions and handle exceptions."""
    try:
        height = [2.71, 1.15]
        weight = [165.3, 38.4]

        bmi = give_bmi(height, weight)
        print(bmi)
        print(apply_limit(bmi, 26))

    except (TypeError, ValueError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
