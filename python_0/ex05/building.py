import sys


def handle_building(s_text: str) -> None:
    """
    Counts the number of uppercase letters, lowercase letters,
    punctuation marks, spaces, and digits in the given text.
    Args:        s_text (str): The input text to analyze.
    Returns:     None
    """
    PUNCT = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    counts = {
        "upper": 0,
        "lower": 0,
        "punctuation": 0,
        "spaces": 0,
        "digits": 0
    }
    for char in s_text:
        if char.isupper():
            counts["upper"] += 1
        elif char.islower():
            counts["lower"] += 1
        elif char in PUNCT:
            counts["punctuation"] += 1
        elif char.isspace():
            counts["spaces"] += 1
        elif char.isdigit():
            counts["digits"] += 1

    print(f"The text contains {len(s_text)} characters:")
    print(f"{counts['upper']} upper letters")
    print(f"{counts['lower']} lower letters")
    print(f"{counts['punctuation']} punctuation marks")
    print(f"{counts['spaces']} spaces")
    print(f"{counts['digits']} digits")


def main():
    """
    Main function to handle user input and call the text analysis function.
    It checks for command-line arguments and
    processes the input text accordingly.
    If no argument is provided or if the argument is an empty string,
    it prompts the user for input.
    It also handles various exceptions that may occur during input processing.
    """
    argv_count = len(sys.argv)
    input_text = ""
    try:
        assert argv_count <= 2, "more than one argument is provided"

        if argv_count < 2 or sys.argv[1] == "":
            input_text = input("What is the text to count?\n")
            input_text += "\n"
        else:
            input_text = sys.argv[1]
        handle_building(input_text)
    except AssertionError as e:
        print(f"AssertionError: {e}")
        return
    except EOFError:
        input_text = ""
        handle_building(input_text)
        return
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f"Error: {e}")
        return


if __name__ == "__main__":
    main()
