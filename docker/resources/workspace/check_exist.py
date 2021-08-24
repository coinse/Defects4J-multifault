import os
import argparse

def has_test_execution_error(path_to_dir):
    # return True if there is an test execution error
    for filename in os.listdir(path_to_dir):
        if filename.endswith('error'):
            print(filename)
            return True
    return False

def is_overlapping(path_to_dir):
    return os.path.exists(os.path.join(path_to_dir, '.overlapping'))

def compare_failing_tests(path_to_dir, expected="tests.trigger.expected", actual="tests.trigger.actual", verbose=False):
    # check if all fault revealing test cases fail
    with open(os.path.join(path_to_dir, expected), 'r') as f:
        expected_failings = set(f.read().splitlines())
    with open(os.path.join(path_to_dir, actual), 'r') as f:
        actual_failings = set(f.read().splitlines())
    actual_failings &= expected_failings # intersection
    if verbose:
        print(f"Expected: {expected_failings}")
        print(f"Actual: {actual_failings}")
        print(f"Do all fault-revealing test cases fail?: {expected_failings == actual_failings}")
    return expected_failings == actual_failings

def compare_error_messages(path_to_dir, expected="tests.trigger.expected", actual="tests.trigger.actual", verbose=False):
    # return True
    # if the error messages are the same in failing_tests.expected and failing_tests.actual
    # for the fault-revealing test cases in tests.trigger.expected
    expected_messages = ""
    actual_messages = ""
    tests = []
    with open(os.path.join(path_to_dir, expected), 'r', encoding='utf-8') as f:
        for l in f:
            if l.startswith('---'):
                tests.append(l.strip().split()[1])
            if not l.strip().startswith('at') and l.strip() != "":
                expected_messages += l
    with open(os.path.join(path_to_dir, actual), 'r', encoding='utf-8') as f:
        append = False
        for l in f:
            if l.startswith('---'):
                test = l.strip().split()[1]
                append = test in tests
            if append and not l.strip().startswith('at') and l.strip() != "":
                actual_messages += l
    if verbose:
        print(f"Expected: {repr(expected_messages)}")
        print(f"Actual: {repr(actual_messages)}")
        print(f"Are the error messages the same?: {expected_messages == actual_messages}")
    return expected_messages == actual_messages

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('path_to_dir', type=str)
  parser.add_argument('--verbose', '-v', action='store_true')
  args = parser.parse_args()

  path_to_dir = args.path_to_dir
  path_to_error_log = os.path.join(path_to_dir, ".not_exist")

  exists = False
  error_log = open(path_to_error_log, 'w')

  f_e = "tests.trigger.expected"
  f_a = "tests.trigger.actual"
  f_af = "tests.trigger.actual.fixed"
  m_e = "failing_tests.expected"
  m_a = "failing_tests.actual"
  m_af = "failing_tests.actual.fixed"

  if has_test_execution_error(path_to_dir):
      error_log.write("error while test transplanation or execution")
  elif not compare_failing_tests(path_to_dir, expected=f_e, actual=f_a, verbose=args.verbose):
      error_log.write(f"{f_e} is not a subset of {f_a}")
  elif not compare_error_messages(path_to_dir, expected=m_e, actual=m_a, verbose=args.verbose):
      error_log.write(f"{m_e} != {m_a} for tests in {f_e}")
  elif is_overlapping(path_to_dir) \
    and not compare_failing_tests(path_to_dir, expected=f_e, actual=f_af, verbose=args.verbose):
      error_log.write(f"overlapping: {f_e} is not a subset of {f_af}")
  elif is_overlapping(path_to_dir) \
    and not compare_error_messages(path_to_dir, expected=m_e, actual=m_af, verbose=args.verbose):
      error_log.write(f"{m_e} != {m_af} for tests in {f_e}")
  else:
    exists = True

  error_log.close()
  if exists:
    os.remove(path_to_error_log)
    print(f"* {path_to_dir}: The fault is revealed.")
  else:
    print(f"* {path_to_dir}: The fault is not revealed. Checkout {path_to_error_log}")
