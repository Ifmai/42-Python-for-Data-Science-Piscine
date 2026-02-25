import sys

argv_count = len(sys.argv)
try:
	if argv_count == 1:
		pass
	elif argv_count > 2:
		assert argv_count == 2, "more than one argument is provided"
	elif argv_count == 2:
		n = int(sys.argv[1])
		assert isinstance(n, int), "argument is not an integer"
		if n % 2 == 0:
			print("I'm Even.")
		else:
			print("I'm Odd.")
except AssertionError as e:
	print(f"AssertionError: {e}")
except ValueError as e:
	print("AssertionError: argument is not an integer")