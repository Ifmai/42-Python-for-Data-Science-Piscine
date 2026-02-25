import sys


MORSE_DICT = {
    " ": "/",
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
}


def encode_morse(text):
    """
    Encode the given text into Morse code.
    Parameters:
        text (str): The text to be encoded. It should be alphanumeric.
    Returns:
        str: The Morse code representation of the input text, 
            with each character's Morse code separated by a space.
    """
    assert isinstance(text, str), "the arguments are bad"
    encoded = []
    for char in text.upper():
        if char not in MORSE_DICT:
            raise AssertionError("the arguments are bad")
        encoded.append(MORSE_DICT[char])
    return ' '.join(encoded)


def main():
    """
    Validate the command-line arguments and encode the input text into Morse code.
    The program expects exactly one argument (the text to be encoded).
    If the argument is valid, it prints the Morse code representation of the text.
    If the argument is invalid, it prints an error message.
    """

    try:
        assert len(sys.argv) == 2, "the arguments are bad"
        text = sys.argv[1]
        assert text.isalnum() or ' ' in text, "the arguments are bad"
        morse_text = encode_morse(text)
        print(morse_text)

    except AssertionError as e:
        print("AssertionError:", e)
    except Exception as e:
        print("AssertionError:", e)



if __name__ == "__main__":
    main()