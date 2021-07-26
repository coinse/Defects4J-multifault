import os
import argparse
import time
import shutil

NUM_FAULTS = {
  "Lang": 65,
  "Time": 27,
  "Chart": 26,
  "Math": 106,
  "Closure": 106
}

DEPRECATED = {
  'Lang': [2],
  'Time': [21],
  'Chart': [],
  'Math': [],
  'Closure': [63, 93]
}

def does_not_exist(path_to_dir):
  return os.path.exists(os.path.join(path_to_dir, '.not_exist'))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('projects', type=str)
  parser.add_argument('--window', '-w', type=int, default=None)
  parser.add_argument('--exhaustive', '-x', action='store_true') # Continue searching even if N is not in M
  parser.add_argument('--savedir', '-d', type=str, default='multi')
  parser.add_argument('--copyfrom', '-c', type=str, default='multi')
  parser.add_argument('--begin', '-b', type=int, default=1)
  parser.add_argument('--end', '-e', type=int, default=None)
  args = parser.parse_args()

  SAVE_DIR = os.path.join(os.environ['COVERAGE_DIR'], args.savedir)
  if args.copyfrom != args.savedir:
    COPY_DIR = os.path.join(os.environ['COVERAGE_DIR'], args.copyfrom)
  else:
    COPY_DIR = None

  print(f"Results will be saved to {SAVE_DIR}")

  projects = args.projects.split(',')
  for project in projects:
    valid_ids = [vid for vid in range(1, NUM_FAULTS[project]+1) if vid not in DEPRECATED[project]]

    # Define search space
    search_space = {}
    for i, vid in enumerate(valid_ids):
      if vid < args.begin:
        continue
      elif args.end is not None and vid > args.end:
        continue

      if args.window is not None:
        search_space[vid] = valid_ids[i+1:i+args.window+1]
      else:
        search_space[vid] = valid_ids[i+1:]

    print("Search space:", search_space)

    for n in search_space:
      for m in search_space[n]:
        identifier = f"{project}-{n}-{m}"
        savepath = os.path.join(SAVE_DIR, identifier)
        print(project, n, m, savepath)

        if COPY_DIR is not None:
          copypath = os.path.join(COPY_DIR, identifier)
          if not os.path.exists(savepath) and os.path.exists(copypath):
            shutil.copytree(copypath, savepath)
            print(f"Copy data from {copypath} to {savepath}")

        os.system(f"sh check_exist.sh {project} {n} {m} {os.path.abspath(savepath)}")
        print("========================================================")
        if not args.exhaustive and does_not_exist(savepath):
          break
        time.sleep(2)
      if os.path.exists(f'/tmp/{project}-{n}b'):
        shutil.rmtree(f'/tmp/{project}-{n}b')
