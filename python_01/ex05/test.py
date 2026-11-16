import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import contextlib  # noqa: E402
import io  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import numpy as np  # noqa: E402
import ast  # noqa: E402
import inspect  # noqa: E402
import pimp_image  # noqa: E402
from pimp_image import (ft_invert, ft_red, ft_green,  # noqa: E402
                        ft_blue, ft_grey)
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


FILTERS = (ft_invert, ft_red, ft_green, ft_blue, ft_grey)
ALLOWED = {
    "ft_invert": {"+", "-", "*"},
    "ft_red": {"*"},
    "ft_green": {"-"},
    "ft_blue": set(),
    "ft_grey": {"/"},
}
SYMBOL = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
          ast.FloorDiv: "//", ast.Mod: "%", ast.Pow: "**",
          ast.USub: "-", ast.UAdd: "+", ast.Invert: "~",
          ast.BitAnd: "&", ast.BitOr: "|", ast.BitXor: "^",
          ast.LShift: "<<", ast.RShift: ">>", ast.MatMult: "@"}


def run(fn, arg):
    """Call fn(arg), capture stdout. Returns (result, out, exc)."""
    buf = io.StringIO()
    result, exc = None, None
    shown.clear()
    with contextlib.redirect_stdout(buf):
        try:
            result = fn(arg)
        except Exception as e:
            exc = e
    return result, buf.getvalue(), exc


def operators_used(fn) -> set:
    """Arithmetic operators written in the body of fn."""
    tree = ast.parse(inspect.getsource(fn))
    ops = set()
    for node in ast.walk(tree):
        op = getattr(node, "op", None)
        if isinstance(node, (ast.BinOp, ast.AugAssign, ast.UnaryOp)):
            ops.add(SYMBOL.get(type(op), type(op).__name__))
    return ops


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        animal = ft_load(ANIMAL)
    original = animal.copy()
    px = np.array([[[10, 20, 30], [0, 128, 255]],
                   [[255, 255, 255], [1, 2, 3]]], dtype=np.uint8)
    expected = {
        "ft_invert": 255 - px.astype(int),
        "ft_red": px * np.array([1, 0, 0]),
        "ft_green": px * np.array([0, 1, 0]),
        "ft_blue": px * np.array([0, 0, 1]),
    }

    # ---------------------------------------------------------------
    section("Every filter on animal.jpeg")
    for fn in FILTERS:
        name = fn.__name__
        result, out, exc = run(fn, animal)
        if exc is not None:
            report(name, False, f"-> {type(exc).__name__}: {exc}")
            continue
        report(f"{name} keeps shape {animal.shape} and uint8",
               isinstance(result, np.ndarray)
               and result.shape == animal.shape
               and result.dtype == np.uint8,
               f"-> {getattr(result, 'shape', None)} "
               f"{getattr(result, 'dtype', None)}")
        report(f"{name} shows the result once",
               len(shown) == 1 and shown[0] is not None
               and np.array_equal(shown[0], result),
               f"-> {len(shown)} time(s)")
        report(f"{name} prints nothing", out == "", f"-> {out[:60]!r}")
        report(f"{name} does not modify the input",
               np.array_equal(animal, original))

    # ---------------------------------------------------------------
    section("Pixel values (small 2x2 image)")
    for fn in FILTERS:
        name = fn.__name__
        result, _, exc = run(fn, px)
        if exc is not None:
            report(name, False, f"-> {type(exc).__name__}: {exc}")
        elif name in expected:
            report(f"{name} values", np.array_equal(result, expected[name]),
                   f"-> {result.tolist()}")
        else:
            grey = all(len(set(p)) == 1 for row in result.tolist()
                       for p in row)
            report("ft_grey: R == G == B on every pixel", grey,
                   f"-> {result.tolist()}")
            report("ft_grey: white stays white, gray levels ordered",
                   result[1, 0, 0] == 255
                   and result[1, 1, 0] < result[0, 0, 0],
                   f"-> {result.tolist()}")
    result, _, _ = run(ft_invert, px)
    if isinstance(result, np.ndarray):
        twice, _, _ = run(ft_invert, result)
        report("invert twice gives back original",
               np.array_equal(twice, px))
    result, _, _ = run(ft_invert, np.zeros((1, 1, 3), np.uint8))
    report("invert black -> white (1x1 image)",
           isinstance(result, np.ndarray)
           and result.tolist() == [[[255, 255, 255]]],
           f"-> {getattr(result, 'tolist', lambda: result)()}")

    # ---------------------------------------------------------------
    section("Allowed operators (subject restriction)")
    for fn in FILTERS:
        used = operators_used(fn)
        bad = used - ALLOWED[fn.__name__]
        allowed = ", ".join(sorted(ALLOWED[fn.__name__] | {"="}))
        report(f"{fn.__name__} uses only {allowed}", not bad,
               f"-> also uses {sorted(bad)}")

    # ---------------------------------------------------------------
    section("Error - invalid input (every filter)")
    bad_inputs = (
        ("None", None),
        ("list", px.tolist()),
        ("str", "animal.jpeg"),
        ("2D array", px[:, :, 0]),
        ("4 channels", np.zeros((2, 2, 4), np.uint8)),
        ("empty", np.zeros((0, 0, 3), np.uint8)),
        ("float array", px.astype(float)),
        ("int64 array", px.astype(np.int64)),
    )
    for fn in FILTERS:
        ok, details = True, []
        for label, value in bad_inputs:
            _, out, exc = run(fn, value)
            if not isinstance(exc, HANDLED) or out or shown:
                ok = False
                details.append(f"{label}: {exc!r}")
        report(f"{fn.__name__} rejects {len(bad_inputs)} bad inputs "
               f"with TypeError/ValueError", ok, "-> " + "; ".join(details))

    # ---------------------------------------------------------------
    section("Script runs")
    env = dict(os.environ, MPLBACKEND="Agg", PYTHONWARNINGS="ignore")
    for script in ("pimp_image.py", "tester.py"):
        if not os.path.exists(os.path.join(HERE, script)):
            continue
        proc = subprocess.run([sys.executable, script], cwd=HERE, env=env,
                              capture_output=True, text=True)
        lines = proc.stdout.splitlines()
        report(f"{script}: first line is ft_load shape",
               lines[:1] == ["The shape of image is: (768, 1024, 3)"],
               f"-> {lines[:1]!r}")
        report(f"{script}: last line is ft_invert docstring",
               lines[-1:] == [ft_invert.__doc__], f"-> {lines[-1:]!r}")
        report(f"{script}: exit code 0, no stderr",
               proc.returncode == 0 and proc.stderr == "",
               f"-> code {proc.returncode}, "
               f"stderr {proc.stderr[-200:]!r}")

    # ---------------------------------------------------------------
    section("Docstrings / signature")
    for fn in FILTERS:
        ann = fn.__annotations__
        report(f"{fn.__name__} has __doc__ and return hint",
               bool((fn.__doc__ or "").strip()) and "return" in ann,
               f"-> doc {fn.__doc__!r}, hints {ann}")
    src = open(pimp_image.__file__).read()
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
