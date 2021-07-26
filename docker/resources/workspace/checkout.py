import os
import logging
import time
import shutil
import argparse


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('identifier', type=str)
  parser.add_argument('-w', type=str, default=None, help="path to check out the program")
  parser.add_argument('--fault_dir', '-d', type=str, default='/root/fault_data/multi')
  parser.add_argument('--verbose', '-v', action='store_true')
  args = parser.parse_args()

  fault_dir = os.path.abspath(args.fault_dir)

  logging.basicConfig(
      format = '%(asctime)s:%(levelname)s:%(message)s',
      datefmt = '%Y-%m-%d %H:%M:%S',
      level=logging.DEBUG if args.verbose else logging.INFO
  )

  identifier = args.identifier
  if args.w is not None:
    checkout_path = args.w
  else:
    checkout_path = os.path.join('/tmp', identifier)

  pid = identifier.split('-')[0]
  faults = list(map(int, identifier.split('-')[1:]))

  tmp_path = f'/tmp/{str(int(time.time()))}'

  assert list(sorted(faults)) == faults

  base = faults[-1]

  if os.path.exists(checkout_path):
    raise Exception(f"{checkout_path} already exists")

  os.system(f"defects4j checkout -p {pid} -v {base}b -w {checkout_path}")
  os.chdir(checkout_path)
  with os.popen("defects4j export -p dir.src.tests") as pipe:
    test_src = pipe.read().strip()
  os.system(f"defects4j export -p tests.trigger -o tests.trigger.{base}")

  for fault in reversed(faults[:-1]):
    path_to_tests = os.path.join(fault_dir, f"{pid}-{fault}-{base}/tests.trigger.expected")
    if not os.path.exists(path_to_tests):
      raise Exception(f"List of fault revealing-tests does not exist: {path_to_tests}. They may not successfully run on {pid}-{base}.")

    logging.info(f"===============================================")
    logging.info(f"Move tests from {pid}-{fault}b to {pid}-{base}b")

    os.system(f"defects4j checkout -p {pid} -v {fault}b -w {tmp_path}")
    os.chdir(tmp_path)
    with os.popen("defects4j export -p dir.src.tests") as pipe:
      tmp_test_src = pipe.read().strip()

    with open(path_to_tests, 'r') as f:
      tests = f.read().splitlines()

    for test in tests:
      # test: org.apache.commons.lang3.LocaleUtilsTest::testLang865
      test_file = test.split('::')[0].replace('.', '/') + '.java'
      test_name = test.split('::')[1]
      source = os.path.join(tmp_path, tmp_test_src, test_file)
      dest = os.path.join(checkout_path, test_src, test_file)
      os.system(f"python3.6 /root/workspace/copy_test.py {source} {dest} {test_name}")
    shutil.copy(path_to_tests, os.path.join(checkout_path, f"tests.trigger.{fault}"))
    os.chdir(checkout_path)
    shutil.rmtree(tmp_path)

  logging.info(f"===============================================")
  logging.info(f"Checked out {identifier} to {checkout_path}")
