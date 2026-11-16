from array2D import slice_me
import array2D
import contextlib
import io
import subprocess
import sys
import os

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

passed = 0
failed = 0

FAMILY = [[1.80, 78.4],
          [2.15, 102.7],
          [2.10, 98.5],
          [1.88, 75.2]]


def report(name: str, ok: bool, detail: str = "") -> None:
    """Print a single test result and update counters."""
    global passed, failed
    if ok:
        passed += 1
        print(f"{GREEN}[OK]{RESET}   {name}")
    else:
        failed += 1
        print(f"{RED}[FAIL]{RESET} {name}  {detail}")


def run(args: tuple):
    """Call slice_me(*args), capture stdout. Returns (result, out, exc)."""
    buf = io.StringIO()
    result, exc = None, None
    with contextlib.redirect_stdout(buf):
        try:
            result = slice_me(*args)
        except Exception as e:
            exc = e
    return result, buf.getvalue(), exc


def shape_lines(old: tuple, new: tuple) -> str:
    return f"My shape is : {old}\nMy new shape is : {new}\n"


def expect_slice(name: str, args: tuple, expected: list,
                 old_shape: tuple, new_shape: tuple) -> None:
    """Check returned value, its type and the printed shapes."""
    result, out, exc = run(args)
    if exc is not None:
        report(name, False, f"-> unexpected {type(exc).__name__}: {exc}")
        return
    ok_val = result == expected and type(result) is list
    report(f"{name} (return)", ok_val,
           f"-> got {result!r} ({type(result).__name__}), "
           f"expected {expected!r}")
    want = shape_lines(old_shape, new_shape)
    report(f"{name} (output)", out == want,
           f"\n       got:      {out!r}\n       expected: {want!r}")


def expect_error(name: str, args: tuple) -> None:
    """Bad input must be handled: TypeError/ValueError raised (no crash
    from deep inside numpy with another type, no silent success)."""
    result, out, exc = run(args)
    if isinstance(exc, (TypeError, ValueError)):
        report(f"{name}  ({type(exc).__name__}: {exc})", True)
    elif exc is not None:
        report(name, False, f"-> raised {type(exc).__name__}: {exc}, "
                            f"expected TypeError/ValueError")
    else:
        report(name, False, f"-> no error, returned {result!r}")


def section(title: str) -> None:
    print(f"\n{YELLOW}=== {title} ==={RESET}")


def main():
    # ---------------------------------------------------------------
    section("Subject example")
    print(slice_me(FAMILY, 0, 2))
    print(slice_me(FAMILY, 1, -2))
    print("Expected:\nMy shape is : (4, 2)\nMy new shape is : (2, 2)\n"
          "[[1.8, 78.4], [2.15, 102.7]]\nMy shape is : (4, 2)\n"
          "My new shape is : (1, 2)\n[[2.15, 102.7]]")
    expect_slice("subject 0:2", (FAMILY, 0, 2),
                 [[1.8, 78.4], [2.15, 102.7]], (4, 2), (2, 2))
    expect_slice("subject 1:-2", (FAMILY, 1, -2),
                 [[2.15, 102.7]], (4, 2), (1, 2))

    # ---------------------------------------------------------------
    section("Script run (python array2D.py)")
    here = os.path.dirname(os.path.abspath(__file__))
    proc = subprocess.run([sys.executable, "array2D.py"], cwd=here,
                          capture_output=True, text=True)
    want = ("My shape is : (4, 2)\nMy new shape is : (2, 2)\n"
            "[[1.8, 78.4], [2.15, 102.7]]\nMy shape is : (4, 2)\n"
            "My new shape is : (1, 2)\n[[2.15, 102.7]]\n")
    report("main() output matches subject", proc.stdout == want,
           f"\n       got:      {proc.stdout!r}\n       expected: {want!r}")
    report("exit code 0, no stderr",
           proc.returncode == 0 and proc.stderr == "",
           f"-> code {proc.returncode}, stderr {proc.stderr!r}")

    # ---------------------------------------------------------------
    section("Slicing - valid input")
    expect_slice("full slice 0:4", (FAMILY, 0, 4), FAMILY, (4, 2), (4, 2))
    expect_slice("end past length 0:100", (FAMILY, 0, 100), FAMILY,
                 (4, 2), (4, 2))
    expect_slice("negative start -2:4", (FAMILY, -2, 4),
                 [[2.10, 98.5], [1.88, 75.2]], (4, 2), (2, 2))
    expect_slice("both negative -3:-1", (FAMILY, -3, -1),
                 [[2.15, 102.7], [2.10, 98.5]], (4, 2), (2, 2))
    expect_slice("single row 3:4", (FAMILY, 3, 4), [[1.88, 75.2]],
                 (4, 2), (1, 2))
    expect_slice("empty start==end 2:2", (FAMILY, 2, 2), [],
                 (4, 2), (0, 2))
    expect_slice("empty start>end 3:1", (FAMILY, 3, 1), [],
                 (4, 2), (0, 2))
    expect_slice("start past length 10:20", (FAMILY, 10, 20), [],
                 (4, 2), (0, 2))
    expect_slice("ints only", ([[1, 2], [3, 4], [5, 6]], 1, 3),
                 [[3, 4], [5, 6]], (3, 2), (2, 2))
    expect_slice("wider rows (3 cols)",
                 ([[1, 2, 3], [4, 5, 6]], 0, 1), [[1, 2, 3]],
                 (2, 3), (1, 3))
    expect_slice("single column", ([[1], [2], [3]], 0, 2), [[1], [2]],
                 (3, 1), (2, 1))
    expect_slice("one row list", ([[7.5, 8.5]], 0, 1), [[7.5, 8.5]],
                 (1, 2), (1, 2))

    inp = [row[:] for row in FAMILY]
    run((inp, 0, 2))
    report("input list not modified", inp == FAMILY)
    res, _, _ = run((FAMILY, 0, 2))
    report("result is a list of lists",
           type(res) is list and all(type(r) is list for r in res),
           f"-> {type(res).__name__}")
    report("elements are python float (not numpy)",
           res is not None and
           all(type(x) is float for r in res for x in r),
           f"-> {[[type(x).__name__ for x in r] for r in res or []]}")
    res, _, _ = run(([[1, 2], [3, 4]], 0, 2))
    report("int elements are python int (not numpy)",
           res is not None and
           all(type(x) is int for r in res for x in r),
           f"-> {[[type(x).__name__ for x in r] for r in res or []]}")
    res, _, _ = run((FAMILY, 0, 2))
    if res:
        res[0][0] = 999
    report("result is a copy (changing it doesn't touch input)",
           FAMILY[0][0] == 1.80)

    # ---------------------------------------------------------------
    section("Error - family is not a list")
    expect_error("family is None", (None, 0, 2))
    expect_error("family is a string", ("hello", 0, 2))
    expect_error("family is an int", (42, 0, 2))
    expect_error("family is a tuple", (((1, 2), (3, 4)), 0, 1))
    expect_error("family is a dict", ({"a": 1}, 0, 1))
    expect_error("family is 1D list", ([1, 2, 3], 0, 2))
    expect_error("rows are tuples, not lists", ([(1, 2), (3, 4)], 0, 1))
    expect_error("one row is a string", ([[1, 2], "ab"], 0, 1))

    # ---------------------------------------------------------------
    section("Error - rows not the same size")
    expect_error("ragged 2 vs 3", ([[1, 2], [3, 4, 5]], 0, 1))
    expect_error("ragged 2 vs 1", ([[1.8, 78.4], [2.15]], 0, 1))
    expect_error("empty row among others", ([[1, 2], []], 0, 1))
    expect_error("ragged at the end", (FAMILY + [[1.0]], 0, 2))

    # ---------------------------------------------------------------
    section("Other element types (any type allowed)")
    expect_slice("all-string array",
                 ([["a", "b"], ["c", "d"], ["e", "f"]], 1, 3),
                 [["c", "d"], ["e", "f"]], (3, 2), (2, 2))
    expect_slice("all-bool array", ([[True, False], [False, True]], 0, 1),
                 [[True, False]], (2, 2), (1, 2))
    expect_error("nested deeper (3D)", ([[[1], [2]], [[3], [4]]], 0, 1))

    # ---------------------------------------------------------------
    section("Error - start / end not int")
    expect_error("start is float", (FAMILY, 0.5, 2))
    expect_error("end is float", (FAMILY, 0, 2.0))
    expect_error("start is string", (FAMILY, "0", 2))
    expect_error("end is None", (FAMILY, 0, None))
    expect_error("start is list", (FAMILY, [0], 2))

    # ---------------------------------------------------------------
    section("Edge - empty family")
    result, out, exc = run(([], 0, 1))
    report("empty list handled (returns [] or raises Type/ValueError)",
           result == [] or isinstance(exc, (TypeError, ValueError)),
           f"-> result {result!r}, exc {exc!r}")

    # ---------------------------------------------------------------
    section("Docstrings / signature")
    report("slice_me has __doc__", bool(slice_me.__doc__))
    ann = slice_me.__annotations__
    report("type hints (family: list, start: int, end: int) -> list",
           ann.get("family") is list and ann.get("start") is int
           and ann.get("end") is int and ann.get("return") is list,
           f"-> {ann}")
    report("module guarded by if __name__ == '__main__'",
           "__name__ == \"__main__\"" in open(array2D.__file__).read()
           or "__name__ == '__main__'" in open(array2D.__file__).read(),
           "-> use ==, not 'in'")

    # ---------------------------------------------------------------
    total = passed + failed
    color = GREEN if failed == 0 else RED
    print(f"\n{color}Result: {passed}/{total} passed, "
          f"{failed} failed{RESET}")


if __name__ == "__main__":
    main()
