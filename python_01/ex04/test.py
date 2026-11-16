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
import inspect  # noqa: E402
import rotate  # noqa: E402
from rotate import rotate_image, transpose_image  # noqa: E402
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
    """Call rotate_image(*args), capture stdout. Returns (result, out, exc)."""
    buf = io.StringIO()
    result, exc = None, None
    shown.clear()
    with contextlib.redirect_stdout(buf):
        try:
            result = rotate_image(*args)
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
    cut = gray_of(animal)[100:500, 450:850]

    # ---------------------------------------------------------------
    section("Subject example (animal.jpeg, 100:500, 450:850)")
    result, out, exc = run(animal, 100, 500, 450, 850)
    lines = out.splitlines()
    report("no exception", exc is None, f"-> {exc!r}")
    want = "The shape of image is: (400, 400, 1) or (400, 400)"
    report("first line is cut shape", lines[:1] == [want],
           f"-> {lines[:1]!r}")
    report("prints cut data", str(cut[:, :, np.newaxis]) in out)
    want = "New shape after Transpose: (400, 400)"
    report("prints transpose shape line", want in lines,
           f"-> expected {want!r}")
    report("returns (400, 400) ndarray",
           isinstance(result, np.ndarray) and result.shape == (400, 400),
           f"-> {getattr(result, 'shape', result)}")
    report("dtype uint8", getattr(result, "dtype", None) == np.uint8,
           f"-> {getattr(result, 'dtype', None)}")
    if isinstance(result, np.ndarray):
        report("result is the transpose of the cut",
               np.array_equal(result, cut.T))
        report("prints transposed data", str(result) in out)
        report("first row of transpose = first column of cut",
               result[0, :3].tolist() == cut[:3, 0].tolist(),
               f"-> {result[0, :3].tolist()} vs {cut[:3, 0].tolist()}")
    report("plt.show called once", len(shown) == 1,
           f"-> {len(shown)} time(s)")
    if shown and shown[0] is not None:
        report("displayed image is the transpose",
               np.array_equal(shown[0], cut.T))
    report("input image not modified", np.array_equal(animal, original))

    # ---------------------------------------------------------------
    section("transpose_image")
    cases = {
        "square 3x3": np.arange(9, dtype=np.uint8).reshape(3, 3),
        "rectangle 2x5": np.arange(10, dtype=np.uint8).reshape(2, 5),
        "single row 1x4": np.arange(4, dtype=np.uint8).reshape(1, 4),
        "single pixel 1x1": np.array([[7]], dtype=np.uint8),
    }
    for name, arr in cases.items():
        try:
            got = transpose_image(arr)
            report(f"{name} -> {arr.shape[::-1]}",
                   np.array_equal(got, arr.T) and got.dtype == arr.dtype,
                   f"-> {got.tolist()}")
        except Exception as e:
            report(name, False, f"-> {type(e).__name__}: {e}")
    try:
        sq = cases["square 3x3"]
        report("transpose twice gives back original",
               np.array_equal(transpose_image(transpose_image(sq)), sq))
    except Exception as e:
        report("transpose twice", False, f"-> {e!r}")
    for name, bad in (("3D input", np.zeros((2, 2, 1), np.uint8)),
                      ("list input", [[1, 2], [3, 4]])):
        try:
            transpose_image(bad)
            report(f"{name} rejected", False, "-> no error")
        except (TypeError, ValueError) as e:
            report(f"{name} rejected  ({type(e).__name__}: {e})", True)
    src = inspect.getsource(transpose_image)
    code = src.split('"""')[-1]
    banned = [b for b in (".T", "transpose(", "rot90", "swapaxes",
                          "moveaxis", "flip") if b in code]
    report("no library transpose used", not banned, f"-> uses {banned}")

    # ---------------------------------------------------------------
    section("Small synthetic image")
    small = np.arange(4 * 5 * 3, dtype=np.uint8).reshape(4, 5, 3)
    for args, shape in (((1, 3, 2, 5), (3, 2)), ((0, 4, 0, 5), (5, 4)),
                        ((3, 4, 4, 5), (1, 1))):
        result, _, exc = run(small, *args)
        report(f"cut {args} -> {shape}",
               exc is None and getattr(result, "shape", None) == shape,
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
    section("Script run (python rotate.py)")
    env = dict(os.environ, MPLBACKEND="Agg", PYTHONWARNINGS="ignore")
    proc = subprocess.run([sys.executable, "rotate.py"], cwd=HERE, env=env,
                          capture_output=True, text=True)
    lines = proc.stdout.splitlines()
    want = "The shape of image is: (400, 400, 1) or (400, 400)"
    report("first line is cut shape (like subject)", lines[:1] == [want],
           f"-> {lines[:1]!r}")
    report("prints transpose shape line",
           "New shape after Transpose: (400, 400)" in lines)
    report("exit code 0, no stderr",
           proc.returncode == 0 and proc.stderr == "",
           f"-> code {proc.returncode}, stderr {proc.stderr[-200:]!r}")

    # ---------------------------------------------------------------
    section("Docstrings / signature")
    for fn in (rotate_image, transpose_image):
        report(f"{fn.__name__} has __doc__", bool((fn.__doc__ or "").strip()))
    ann = rotate_image.__annotations__
    report("bounds hinted as int",
           all(ann.get(k) is int
               for k in ("x_start", "x_end", "y_start", "y_end")),
           f"-> {ann}")
    report("return type hint present", "return" in ann, f"-> {ann}")
    src = open(rotate.__file__).read()
    report("module guarded by if __name__ == \'__main__\'",
           "__name__ == \'__main__\'" in src
           or "__name__ == \"__main__\"" in src)

    # ---------------------------------------------------------------
    total = passed + failed
    color = GREEN if failed == 0 else RED
    print(f"\n{color}Result: {passed}/{total} passed, "
          f"{failed} failed{RESET}")


if __name__ == "__main__":
    main()
