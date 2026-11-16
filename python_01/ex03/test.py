import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import contextlib  # noqa: E402
import io  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
import zoom  # noqa: E402
from zoom import image_zoom  # noqa: E402
from load_image import ft_load  # noqa: E402

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

passed = 0
failed = 0

HERE = os.path.dirname(os.path.abspath(__file__))
ANIMAL = os.path.join(HERE, "animal.jpeg")
HANDLED = (TypeError, ValueError)
shown = []


def fake_show(*args, **kwargs) -> None:
    """Replace plt.show: remember what was drawn instead of opening a
    window."""
    images = plt.gca().get_images()
    shown.append(np.asarray(images[-1].get_array()) if images else None)
    plt.close("all")


plt.show = fake_show


def report(name: str, ok: bool, detail: str = "") -> None:
    """Print a single test result and update counters."""
    global passed, failed
    if ok:
        passed += 1
        print(f"{GREEN}[OK]{RESET}   {name}")
    else:
        failed += 1
        print(f"{RED}[FAIL]{RESET} {name}  {detail}")


def section(title: str) -> None:
    print(f"\n{YELLOW}=== {title} ==={RESET}")


def run(*args):
    """Call image_zoom(*args), capture stdout. Returns (result, out, exc)."""
    buf = io.StringIO()
    result, exc = None, None
    shown.clear()
    with contextlib.redirect_stdout(buf):
        try:
            result = image_zoom(*args)
        except Exception as e:
            exc = e
    return result, buf.getvalue(), exc


def expect_error(name: str, *args) -> None:
    """Bad input must raise TypeError/ValueError, print nothing and show
    nothing."""
    result, out, exc = run(*args)
    if isinstance(exc, HANDLED):
        report(f"{name}  ({type(exc).__name__}: {exc})",
               out == "" and not shown,
               f"-> printed {out[:60]!r} / showed {len(shown)} image(s)")
    elif exc is not None:
        report(name, False, f"-> raised {type(exc).__name__}: {exc}, "
                            f"expected TypeError/ValueError")
    else:
        report(name, False, f"-> no error, returned "
                            f"{type(result).__name__}")


def gray_of(image: np.ndarray) -> np.ndarray:
    return np.array(Image.fromarray(image).convert("L"))


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        animal = ft_load(ANIMAL)
    original = animal.copy()

    # ---------------------------------------------------------------
    section("Subject example (animal.jpeg, 100:500, 450:850)")
    result, out, exc = run(animal, 100, 500, 450, 850)
    report("no exception", exc is None, f"-> {exc!r}")
    report("returns (400, 400, 1) ndarray",
           isinstance(result, np.ndarray) and result.shape == (400, 400, 1),
           f"-> {getattr(result, 'shape', result)}")
    report("dtype uint8", getattr(result, "dtype", None) == np.uint8,
           f"-> {getattr(result, 'dtype', None)}")
    want = "New shape after slicing: (400, 400, 1) or (400, 400)"
    report("prints new shape line", want in out,
           f"-> expected {want!r} in output")
    report("prints the original image first",
           out.startswith(str(animal)), f"-> starts {out[:40]!r}")
    if isinstance(result, np.ndarray):
        report("pixels = grayscale crop",
               np.array_equal(result[:, :, 0],
                              gray_of(animal)[100:500, 450:850]))
        report("printed zoom data", str(result) in out)
    report("plt.show called once", len(shown) == 1,
           f"-> {len(shown)} time(s)")
    if shown and shown[0] is not None:
        report("displayed image is 400x400", shown[0].shape == (400, 400),
               f"-> {shown[0].shape}")
    report("input image not modified", np.array_equal(animal, original))

    # ---------------------------------------------------------------
    section("Small synthetic image")
    small = np.arange(4 * 5 * 3, dtype=np.uint8).reshape(4, 5, 3)
    result, _, exc = run(small, 1, 3, 2, 5)
    report("crop 1:3, 2:5 -> (2, 3, 1)",
           exc is None and getattr(result, "shape", None) == (2, 3, 1),
           f"-> {exc!r} {getattr(result, 'shape', None)}")
    result, _, exc = run(small, 0, 4, 0, 5)
    report("full image crop -> (4, 5, 1)",
           exc is None and getattr(result, "shape", None) == (4, 5, 1),
           f"-> {exc!r} {getattr(result, 'shape', None)}")
    result, _, exc = run(small, 3, 4, 4, 5)
    report("1x1 crop at the corner",
           exc is None and getattr(result, "shape", None) == (1, 1, 1),
           f"-> {exc!r} {getattr(result, 'shape', None)}")

    # ---------------------------------------------------------------
    section("Error - image is not a valid array")
    expect_error("image is None", None, 0, 1, 0, 1)
    expect_error("image is a list", small.tolist(), 0, 1, 0, 1)
    expect_error("image is a str", "animal.jpeg", 0, 1, 0, 1)
    expect_error("2D image", small[:, :, 0], 0, 1, 0, 1)
    expect_error("4 channels", np.zeros((4, 4, 4), np.uint8), 0, 1, 0, 1)
    expect_error("1 channel 3D", np.zeros((4, 4, 1), np.uint8), 0, 1, 0, 1)
    expect_error("empty image", np.zeros((0, 0, 3), np.uint8), 0, 1, 0, 1)
    expect_error("float image", small.astype(float), 0, 1, 0, 1)

    # ---------------------------------------------------------------
    section("Error - bounds are not ints")
    expect_error("float bound", small, 0.0, 2, 0, 2)
    expect_error("str bound", small, 0, "2", 0, 2)
    expect_error("None bound", small, 0, 2, None, 2)
    expect_error("bool bound", small, 0, 2, 0, True)
    expect_error("numpy int bound", small, np.int64(0), 2, 0, 2)

    # ---------------------------------------------------------------
    section("Error - bounds out of range")
    expect_error("negative start", small, -1, 2, 0, 2)
    expect_error("x_end > height", small, 0, 5, 0, 2)
    expect_error("y_end > width", small, 0, 2, 0, 6)
    expect_error("x_start == x_end (empty)", small, 2, 2, 0, 2)
    expect_error("y_start > y_end", small, 0, 2, 3, 1)

    # ---------------------------------------------------------------
    section("Script run (python zoom.py)")
    env = dict(os.environ, MPLBACKEND="Agg", PYTHONWARNINGS="ignore")
    proc = subprocess.run([sys.executable, "zoom.py"], cwd=HERE, env=env,
                          capture_output=True, text=True)
    lines = proc.stdout.splitlines()
    report("first line is ft_load shape",
           lines[:1] == ["The shape of image is: (768, 1024, 3)"],
           f"-> {lines[:1]!r}")
    report("prints new shape line", any(
        "New shape after slicing: (400, 400, 1) or (400, 400)" == ln
        for ln in lines))
    report("exit code 0, no stderr",
           proc.returncode == 0 and proc.stderr == "",
           f"-> code {proc.returncode}, stderr {proc.stderr[-200:]!r}")

    # ---------------------------------------------------------------
    section("Docstrings / signature")
    report("image_zoom has __doc__", bool((image_zoom.__doc__ or "").strip()))
    ann = image_zoom.__annotations__
    report("bounds hinted as int",
           all(ann.get(k) is int
               for k in ("x_start", "x_end", "y_start", "y_end")),
           f"-> {ann}")
    report("return type hint present", "return" in ann, f"-> {ann}")
    src = open(zoom.__file__).read()
    report("module guarded by if __name__ == '__main__'",
           "__name__ == '__main__'" in src
           or "__name__ == \"__main__\"" in src)

    # ---------------------------------------------------------------
    total = passed + failed
    color = GREEN if failed == 0 else RED
    print(f"\n{color}Result: {passed}/{total} passed, "
          f"{failed} failed{RESET}")


if __name__ == "__main__":
    main()
