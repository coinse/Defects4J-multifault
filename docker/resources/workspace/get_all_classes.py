import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", type=str)
    parser.add_argument("target_dir", type=str)
    parser.add_argument("output_path", type=str)
    args = parser.parse_args()
    target_dir = os.path.join(args.project_dir, args.target_dir)
    with open(args.output_path, 'w') as output_file:
      for root, subdirs, files in os.walk(target_dir):
        package = os.path.relpath(root, target_dir).replace('/', '.')
        for f in files:
          if f[-6:] == '.class':
            classname = f[:-6]
            output_file.write(package + '.' + classname + '\n')
