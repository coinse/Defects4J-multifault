import os
import json
import argparse
import logging

MERGE_NEEDED = {
    'Closure': {'21': '22'}
}

def get_fault_revealing_tests(pid, vid):
    with open(f"./resources/failing_tests/{pid}/{vid}") as f:
        return [l.replace("::", ".") for l in f.read().splitlines()]

def get_multi_faults(fault_data_dir, target_pid):
    multi_faults = {}
    for dirname in os.listdir(fault_data_dir):
        path_to_dir = os.path.join(fault_data_dir, dirname)
        pid, recent, base = tuple(dirname.split('-'))
        if target_pid is not None and target_pid != pid:
            continue
        logging.info(f"{dirname}: Start checking .......")

        # check if no error
        not_exist = os.path.join(path_to_dir, '.not_exist')
        if os.path.exists(not_exist):
            with open(not_exist, 'r') as f:
                logging.info(f"{dirname}: {f.read()} (see details at {path_to_dir})")
            continue

        if base not in multi_faults:
            multi_faults[base] = set()

        multi_faults[base].add(recent)

    if target_pid in MERGE_NEEDED:
        for base in multi_faults:
            for sub, dom in MERGE_NEEDED[target_pid].items():
                if sub in multi_faults[base] and dom in multi_faults[base]:
                    multi_faults[base].remove(sub)

    return multi_faults

def export(pid, multi_faults, savepath=None):
    version_to_faults = {
        str(v): list(map(str, sorted(map(int, list(multi_faults[str(v)]))))) + [str(v)]
        for v in sorted(map(int, multi_faults))
    }
    if savepath is None:
        savepath = f'multiple_faults/{pid}.json'

    os.makedirs(os.path.dirname(savepath), exist_ok=True)
    with open(savepath, 'w') as jsonfile:
        json.dump(
            {
                vid: {
                    f: get_fault_revealing_tests(pid, f)
                    for f in version_to_faults[vid]
                }
                for vid in version_to_faults
            },
            jsonfile,
            indent=4
        )
    with open(savepath + '.pairs.csv', 'w') as file:
        file.write("N,M\n")
        for version in version_to_faults:
            for fault in version_to_faults[version]:
                if fault != version:
                    file.write(f"{fault},{version}\n")
            print(f"{'-'.join(version_to_faults[version])}")
    return savepath

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('pid', type=str)
    parser.add_argument('--fault-data-dir', '-d', type=str, default="./fault_data/multi/")
    parser.add_argument('--savepath', '-s', type=str, default=None)
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(
        format = '%(levelname)s:%(message)s',
        level=logging.DEBUG if args.verbose else logging.INFO
    )

    """
    Filtering only valid multi-fault data
    """
    multi_faults = get_multi_faults(args.fault_data_dir, args.pid)

    savepath = export(args.pid, multi_faults, savepath=args.savepath)

    logging.info(f"Data is saved to {savepath}")
