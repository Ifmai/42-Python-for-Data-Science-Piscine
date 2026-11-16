from load_image import ft_load
import load_image
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import numpy as np
from PIL import Image

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

passed = 0
failed = 0

HERE = os.path.dirname(os.path.abspath(__file__))
LANDSCAPE = os.path.join(HERE, "landscape.jpg")
HANDLED = (OSError, TypeError, ValueError)


def report(name: str, ok: bool, detail: str = "") -> None:
    """Print a single test result and update counters."""
    global passed, failed
    if ok:
        passed += 1
        print(f"{GREEN}[OK]{RESET}   {name}")
    else:
        failed += 1
        print(f"{RED}[FAIL]{RESET} {name}  {detail}")


def run(path):
    """Call ft_load(path), capture stdout. Returns (result, out, exc)."""
    buf = io.StringIO()
    result, exc = None, None
    with contextlib.redirect_stdout(buf):
        try:
            result = ft_load(path)
        except Exception as e:
            exc = e
    return result, buf.getvalue(), exc


def expect_load(name: str, path, shape: tuple) -> None:
    """Check the returned array (type, shape, dtype) and printed shape."""
    result, out, exc = run(path)
    if exc is not None:
        report(name, False, f"-> unexpected {type(exc).__name__}: {exc}")
        return
    ok = isinstance(result, np.ndarray) and result.shape == shape
    report(f"{name} (return)", ok,
           f"-> got {type(result).__name__} "
           f"{getattr(result, 'shape', None)}, expected ndarray {shape}")
    report(f"{name} (dtype uint8)",
           getattr(result, "dtype", None) == np.uint8,
           f"-> got {getattr(result, 'dtype', None)}")
    want = f"The shape of image is: {shape}\n"
    report(f"{name} (output)", out == want,
           f"\n       got:      {out!r}\n       expected: {want!r}")


def expect_error(name: str, path) -> None:
    """Bad input must raise a clear OSError/TypeError/ValueError
    (no AttributeError from deep inside Pillow, no silent success)."""
    result, out, exc = run(path)
    if isinstance(exc, HANDLED):
        report(f"{name}  ({type(exc).__name__}: {exc})", True)
    elif exc is not None:
        report(name, False, f"-> raised {type(exc).__name__}: {exc}, "
                            f"expected OSError/TypeError/ValueError")
    else:
        report(name, False, f"-> no error, returned "
                            f"{type(result).__name__}")


def section(title: str) -> None:
    print(f"\n{YELLOW}=== {title} ==={RESET}")


def main():
    # ---------------------------------------------------------------
    section("Subject example")
    print(ft_load(LANDSCAPE))
    print("Expected:\nThe shape of image is: (257, 450, 3)\n"
          "[[[19 42 83]\n  [23 42 84]\n  [28 43 84]\n  ...")
    expect_load("subject landscape.jpg", LANDSCAPE, (257, 450, 3))
    res, _, _ = run(LANDSCAPE)
    if isinstance(res, np.ndarray):
        report("first pixels match subject",
               res[0, :3].tolist() == [[19, 42, 83], [23, 42, 84],
                                       [28, 43, 84]],
               f"-> got {res[0, :3].tolist()}")

    # ---------------------------------------------------------------
    section("Script run (python load_image.py)")
    proc = subprocess.run([sys.executable, "load_image.py"], cwd=HERE,
                          capture_output=True, text=True)
    first = proc.stdout.splitlines()[:2]
    want = ["The shape of image is: (257, 450, 3)", "[[[19 42 83]"]
    report("main() output starts like subject", first == want,
           f"\n       got:      {first!r}\n       expected: {want!r}")
    report("exit code 0, no stderr",
           proc.returncode == 0 and proc.stderr == "",
           f"-> code {proc.returncode}, stderr {proc.stderr!r}")

    with tempfile.TemporaryDirectory() as tmp:
        # -----------------------------------------------------------
        section("Valid JPEG variants")
        small = os.path.join(tmp, "small.jpg")
        Image.new("RGB", (4, 3), (255, 0, 0)).save(small)
        expect_load("small RGB jpg 4x3", small, (3, 4, 3))

        gray = os.path.join(tmp, "gray.jpg")
        Image.new("L", (2, 2), 128).save(gray)
        expect_load("grayscale jpg -> RGB", gray, (2, 2, 3))

        upper = os.path.join(tmp, "UPPER.JPEG")
        Image.new("RGB", (1, 1)).save(upper, "JPEG")
        expect_load("uppercase .JPEG extension", upper, (1, 1, 3))

        res, _, _ = run(small)
        report("pixel values are correct (red)",
               isinstance(res, np.ndarray)
               and abs(int(res[0, 0, 0]) - 255) <= 2
               and int(res[0, 0, 1]) <= 2 and int(res[0, 0, 2]) <= 2,
               f"-> got {None if res is None else res[0, 0].tolist()}")

        # -----------------------------------------------------------
        section("Error - path problems")
        expect_error("missing file", os.path.join(tmp, "nope.jpg"))
        expect_error("directory", tmp)
        expect_error("empty string", "")

        locked = os.path.join(tmp, "locked.jpg")
        Image.new("RGB", (2, 2)).save(locked)
        os.chmod(locked, 0)
        expect_error("no read permission", locked)
        os.chmod(locked, 0o644)

        # -----------------------------------------------------------
        section("Error - path is not a string")
        expect_error("path is None", None)
        expect_error("path is an int", 42)
        expect_error("path is a list", [LANDSCAPE])

        # -----------------------------------------------------------
        section("Error - not a JPEG")
        png = os.path.join(tmp, "image.png")
        Image.new("RGB", (2, 2)).save(png)
        expect_error("png file", png)

        png_as_jpg = os.path.join(tmp, "png_inside.jpg")
        Image.new("RGB", (2, 2)).save(png_as_jpg, "PNG")
        expect_error("png renamed to .jpg", png_as_jpg)

        txt = os.path.join(tmp, "notes.txt")
        with open(txt, "w") as f:
            f.write("this is not an image")
        expect_error("text file", txt)

        fake = os.path.join(tmp, "fake.jpg")
        with open(fake, "w") as f:
            f.write("text with a jpg extension")
        expect_error("text renamed to .jpg", fake)

        empty = os.path.join(tmp, "empty.jpg")
        open(empty, "w").close()
        expect_error("empty .jpg file", empty)

    # ---------------------------------------------------------------
    section("Docstrings / signature")
    report("ft_load has __doc__",
           bool(ft_load.__doc__ and ft_load.__doc__.strip()),
           f"-> {ft_load.__doc__!r}")
    ann = ft_load.__annotations__
    report("type hint path: str", ann.get("path") is str, f"-> {ann}")
    report("return type hint present", "return" in ann, f"-> {ann}")
    src = open(load_image.__file__).read()
    report("module guarded by if __name__ == '__main__'",
           "__name__ == \"__main__\"" in src
           or "__name__ == '__main__'" in src)

    # ---------------------------------------------------------------
    total = passed + failed
    color = GREEN if failed == 0 else RED
    print(f"\n{color}Result: {passed}/{total} passed, "
          f"{failed} failed{RESET}")


if __name__ == "__main__":
    main()
