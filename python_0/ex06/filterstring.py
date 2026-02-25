import sys
from ft_filter import ft_filter


def filter_string(input_string, n) -> list:
    """
    Return words from input_string whose length is greater than n.

    Args:
        input_string: String to split and filter.
        n: Minimum length threshold (exclusive).

    Returns:
        A list of words with len(word) > n.
    """
    return list(ft_filter(lambda x: len(x) > n, input_string.split()))


def main():
    """
    Validate arguments, filter words by length, and print the result.
    """
    try:
        assert len(sys.argv) == 3, "the arguments are bad"
        input_string = sys.argv[1]
        n = int(sys.argv[2])
        assert isinstance(input_string, str), "the arguments are bad"
        assert isinstance(n, int), "the arguments are bad"
        result = filter_string(input_string, n)
        print(result)
    except AssertionError as e:
        print(f"AssertionError: {e}")
        return
    except ValueError:
        print("AssertionError: the arguments are bad")
        return
    except Exception as e:
        print(f"Error: {e}")
        return


if __name__ == "__main__":
    main()
