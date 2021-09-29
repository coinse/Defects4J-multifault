# Multiple faults dataset for Java programs (Extension of Defects4J)

This replication package implements a technique to find multi-fault versions in the [Defecst4J](https://github.com/rjust/defects4j) dataset accompanying the paper: "Searching for Multi-Fault Programs in Defects4J", *Gabin An, Juyeon Yoon, Shin Yoo*, SSBSE 2021 (to appear, [preprint](https://arxiv.org/pdf/2108.04455.pdf)).

You can simply extract the search results to `fault_data/multi/` using the following command.
```
cd fault_data; sh extract.sh multi.tar.bz2
```

Please note that you can reproduce these results following Step 1 and 2 in [the replication guide](#a-guide-to-replication).


### Description of result files
- [./multiple_faults](./multiple_faults): A dataset of multiple faults. A `<project>.json` file includes the bugs contained in each buggy version in `<project>`.
- [./fault_data/multi/](./fault_data/multi): Raw search results (about *3GB*). 
  - The following files are written in `<project>-<N>-<M>`
    - `.*_error`: these files are created when an error occurs during the test transplanation, test compile, or execution.
    - `.overlapping`: this file is created when the revealing test cases of the bug `N` and `M` are ovelapped. 
    - `tests.trigger.*`:
      - `expected`: the original set of fault revealing test cases of `N`
      - `actual`: the set of tests that fail on `<project>-<M>b` containing the fault-revealing test cases of `N`
      - `actual.fixed`: the set of tests that fail on `<project>-<M>f` containing the fault-revealing test cases of `N` (generated only when `.overlapping` exists)
    - `failing_tests.*`:
      - `expected`: the original error messages of fault revealing test cases of `N`
      - `actual`: the error messages of failing tests on `<project>-<M>b` containing the fault-revealing test cases of `N`
      - `actual.fixed`: the error messages of failing tests on `<project>-<M>f` containing the fault-revealing test cases of `N` (generated only when `.overlapping` exists) 
    - `<project>-<N>-<M>.patch`: the git patch that transplants the fault-revealing test cases of `<project>-<N>` to `<project>-<M>b`
    - `test_copy.log`: log produced during the test transplanation. Similar to `<project>-<N>-<M>.patch`
    - `*.xml`: the coverage of fault-revealing test cases of `N` on `<project>-<M>b`.
    - `.not_exist`: if this file exists, `N` is not revealed in `<project>-<M>b`. See the file contents for more details.
  - [./analysis.ipynb](./analysis.ipynb): The data analysis script used to draw the figures in the paper
  
# A Guide to Replication

## Prerequisite

* Docker
* (Host machine) Python version 3.9.1

## Step 1. Preparing the docker environment

Build the docker image & execute the docker container
```bash
cd docker/
# build a docker image
docker build --tag mf:latest .
# create a docker container in the background
docker run -dt --name mf -v $(pwd)/resources/workspace:/root/workspace -v $(pwd)/../fault_data:/root/fault_data mf:latest
# execute an interactive bash shell on the container
docker exec -it mf bash
```

## Step 2. Running the search

To replicate the whole search in the paper, 
```bash
# on the docker container
cd /root/workspace
python3.6 search.py <projects> --savedir <dirname>
```

Then, the search results are saved to `/root/fault_data/<dirname>/` directory in the container (which is `./fault_data/<dirname>` in the host machine).

For example,
```
python3.6 search.py Lang,Chart,Time,Math,Closure --savedir multi_replicated
```
will save the searh results to `/root/fault_data/multi_replicated/`

### Want to test for a single pair of N and M?
One can use the following command to check a specific bug `<project>-<N>` exists in the buggy version `<project>-<M>b`. 
```bash
# on the docker container
sh check_exist.sh <project> <N> <M> <savepath>
# ex) sh check_exish.sh Math 5 6 ./Math-5-6
```
The existence check result will be saved into `<savepath>`.

## Step 3. Checkout the multi-fault version (Optional)

**Note that we do not alter any source codes to artifically inject faults. We only added bug-revealing test cases that can reveal multiple faults in the original code version**

After the step 2, you may want to check out the multiple fault version where 
the source code remains the same, but additional bug-revealing test cases are transplanted.

On the docker container, use the following command to check out the source code:
```bash
# on the docker container
python3.6 checkout.py Lang-26-27-31 -w /tmp/Lang-26-27-31
cd /tmp/Lang-26-27-31
git diff
cat tests.trigger.*
```

## Step 4. Analysing the search results and creating the dataset of multiple faults

```bash
# on the host machine (repository root)
python create_dataset.py <project> --savepath <savepath>
```
This command creates two result files, `<savepath>` and `<savepath>.pairs.csv`.

For example, executing the following command
```
python create_dataset.py Lang --savepath multiple_faults_replicated/Lang.json
```
will create `multiple_faults_replicated/Lang.json` and `multiple_faults_replicated/Lang.json.pairs.csv`. 
Please refer to [`multiple_faults/README.md`](./multiple_faults/README.md) for more details about the data format.
