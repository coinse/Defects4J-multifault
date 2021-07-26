import argparse
import os

RANGE_ANALYZER = os.environ["RANGE_ANALYZER"]

def get_method_ranges(file_path):
    source_root = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    ranges = {}
    with os.popen(f"java -jar {RANGE_ANALYZER} {source_root} {file_name}") as f:
      for l in f:
        if l.startswith("[method]"):
          signature, begin_line, end_line = tuple(l.strip().split('|')[1:])
          begin_index, end_index = int(begin_line)-1, int(end_line)-1
          method_name = signature.split('(')[0]
          ranges[method_name] = (begin_index, end_index)
    return ranges

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=str)
    parser.add_argument("dest", type=str)
    parser.add_argument("method", type=str)
    args = parser.parse_args()

    source_root = os.path.dirname(args.src)
    file_name = os.path.basename(args.src)

    src_ranges = get_method_ranges(args.src)
    if args.method not in src_ranges:
        raise Exception(f"{args.method} not in {args.src}")
    begin_index, end_index = src_ranges[args.method]
    with open(args.src, 'r') as f:
        method_snippet = f.readlines()[begin_index:end_index+1]

    with open(args.dest, 'r') as f:
      test_file = f.readlines()

    dest_ranges = get_method_ranges(args.dest)
    if args.method in dest_ranges:
        begin_index, end_index = dest_ranges[args.method]
        is_same = method_snippet == test_file[begin_index:end_index+1]
        test_file = test_file[:begin_index] + test_file[end_index + 1:]
        insert_index = begin_index

        if is_same:
            print(f"--- Exist: {args.method}")
        else:
            print(f"--- Overwrite: {args.method}")
    else:
        print(f"--- Insert: {args.method}")
        # the index of last method line
        insert_index = max([dest_ranges[method][1] for method in dest_ranges]) + 1

    test_file = test_file[:insert_index] + method_snippet + test_file[insert_index:]

    with open(args.dest, 'w') as f:
      f.writelines(test_file)
