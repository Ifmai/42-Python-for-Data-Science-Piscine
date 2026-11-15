from give_bmi import give_bmi, apply_limit
import math

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

passed = 0
failed = 0


def report(name: str, ok: bool, detail: str = "") -> None:
    """Print a single test result and update counters."""
    global passed, failed
    if ok:
        passed += 1
        print(f"{GREEN}[OK]{RESET}   {name}")
    else:
        failed += 1
        print(f"{RED}[FAIL]{RESET} {name}  {detail}")


def expect_equal(name: str, func, args: tuple, expected) -> None:
    """Run func(*args) and compare the result with expected."""
    try:
        result = func(*args)
    except Exception as e:
        report(name, False, f"-> unexpected {type(e).__name__}: {e}")
        return
    if isinstance(expected, list) and expected and \
            isinstance(expected[0], float):
        ok = (isinstance(result, list) and len(result) == len(expected)
              and all(math.isclose(r, e) for r, e in zip(result, expected)))
    else:
        ok = result == expected
    ok = ok and type(result) is type(expected)
    report(name, ok, f"-> got {result!r} ({type(result).__name__}), "
                     f"expected {expected!r}")


def expect_raise(name: str, func, args: tuple, exc: type) -> None:
    """Run func(*args) and check that it raises exc."""
    try:
        result = func(*args)
    except exc as e:
        report(f"{name}  ({exc.__name__}: {e})", True)
        return
    except Exception as e:
        report(name, False, f"-> raised {type(e).__name__}: {e}, "
                            f"expected {exc.__name__}")
        return
    report(name, False, f"-> no error, returned {result!r}")


def section(title: str) -> None:
    print(f"\n{YELLOW}=== {title} ==={RESET}")


def main():
    # ---------------------------------------------------------------
    section("Subject example")
    height = [2.71, 1.15]
    weight = [165.3, 38.4]
    bmi = give_bmi(height, weight)
    print(bmi, type(bmi))
    print(apply_limit(bmi, 26))
    print("Expected:\n[22.507863455018317, 29.0359168241966] <class 'list'>"
          "\n[False, True]")
    expect_equal("subject give_bmi", give_bmi, (height, weight),
                 [22.507863455018317, 29.0359168241966])
    expect_equal("subject apply_limit", apply_limit, (bmi, 26),
                 [False, True])

    # ---------------------------------------------------------------
    section("give_bmi - valid input")
    expect_equal("ints only", give_bmi, ([2, 1], [100, 50]),
                 [25.0, 50.0])
    expect_equal("mixed int / float", give_bmi, ([1.80, 2], [81, 80.0]),
                 [25.0, 20.0])
    expect_equal("single element", give_bmi, ([1.75], [70]),
                 [70 / 1.75 ** 2])
    expect_equal("empty lists", give_bmi, ([], []), [])
    expect_equal("very small values", give_bmi, ([0.01], [0.0001]), [1.0])
    expect_equal("large values", give_bmi, ([1000], [1e9]), [1000.0])
    many_h = [1.5 + i * 0.01 for i in range(100)]
    many_w = [50 + i for i in range(100)]
    expect_equal("100 elements", give_bmi, (many_h, many_w),
                 [w / h ** 2 for h, w in zip(many_h, many_w)])
    h_in, w_in = [1.80, 1.60], [80, 60]
    give_bmi(h_in, w_in)
    report("input lists not modified",
           h_in == [1.80, 1.60] and w_in == [80, 60])
    res = give_bmi([2], [100])
    report("result elements are python float (not numpy)",
           all(type(x) is float for x in res),
           f"-> {[type(x).__name__ for x in res]}")

    # ---------------------------------------------------------------
    section("give_bmi - wrong types")
    expect_raise("string in height", give_bmi, ([1.8, "a"], [80, 70]),
                 TypeError)
    expect_raise("string in weight", give_bmi, ([1.8, 1.7], [80, "70"]),
                 TypeError)
    expect_raise("None in list", give_bmi, ([1.8, None], [80, 70]),
                 TypeError)
    expect_raise("bool in list (True)", give_bmi, ([True], [80]),
                 TypeError)
    expect_raise("complex in list", give_bmi, ([1 + 2j], [80]), TypeError)
    expect_raise("nested list", give_bmi, ([[1.8]], [80]), TypeError)
    expect_raise("height is a string", give_bmi, ("1.8", [80]), TypeError)
    expect_raise("height is an int", give_bmi, (1.8, [80]), TypeError)
    expect_raise("height is None", give_bmi, (None, [80]), TypeError)

    # ---------------------------------------------------------------
    section("give_bmi - wrong values")
    expect_raise("different lengths", give_bmi, ([1.8, 1.7], [80]),
                 ValueError)
    expect_raise("one empty, one not", give_bmi, ([], [80]), ValueError)
    expect_raise("zero height", give_bmi, ([0], [80]), ValueError)
    expect_raise("zero weight", give_bmi, ([1.8], [0]), ValueError)
    expect_raise("negative height", give_bmi, ([-1.8], [80]), ValueError)
    expect_raise("negative weight", give_bmi, ([1.8], [-80]), ValueError)
    expect_raise("NaN height", give_bmi, ([float("nan")], [80]),
                 ValueError)
    expect_raise("inf height", give_bmi, ([float("inf")], [80]),
                 ValueError)

    # ---------------------------------------------------------------
    section("apply_limit - valid input")
    expect_equal("basic", apply_limit, ([20.0, 30.0, 25.0], 25),
                 [False, True, False])
    expect_equal("equal to limit is False", apply_limit, ([26, 26.0], 26),
                 [False, False])
    expect_equal("int bmi values", apply_limit, ([10, 40], 26),
                 [False, True])
    expect_equal("empty list", apply_limit, ([], 26), [])
    expect_equal("limit 0", apply_limit, ([0.1, 5], 0), [True, True])
    expect_equal("negative limit", apply_limit, ([1, 2], -5), [True, True])
    res = apply_limit([30.0], 25)
    report("result elements are python bool (not numpy)",
           all(type(x) is bool for x in res),
           f"-> {[type(x).__name__ for x in res]}")

    # ---------------------------------------------------------------
    section("apply_limit - wrong input")
    expect_raise("float limit", apply_limit, ([20.0], 25.5), TypeError)
    expect_raise("string limit", apply_limit, ([20.0], "25"), TypeError)
    expect_raise("None limit", apply_limit, ([20.0], None), TypeError)
    expect_raise("bool limit", apply_limit, ([20.0], True), TypeError)
    expect_raise("string in bmi", apply_limit, ([20.0, "x"], 25),
                 TypeError)
    expect_raise("bmi is a string", apply_limit, ("20", 25), TypeError)
    expect_raise("bmi is None", apply_limit, (None, 25), TypeError)

    # ---------------------------------------------------------------
    section("Docstrings")
    report("give_bmi has __doc__", bool(give_bmi.__doc__))
    report("apply_limit has __doc__", bool(apply_limit.__doc__))

    # ---------------------------------------------------------------
    total = passed + failed
    color = GREEN if failed == 0 else RED
    print(f"\n{color}Result: {passed}/{total} passed, "
          f"{failed} failed{RESET}")


if __name__ == "__main__":
    main()
