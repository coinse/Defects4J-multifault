#!/bin/bash

# This script checks if <project>-<fault> is revealed in <project>-<base>b.

project=$1
fault=$2
base=$3

fault_dir=$TMP_DIR/$project-${fault}b
base_dir=$TMP_DIR/$project-${base}b

if [ "$#" -eq 3 ]; then
  save_dir=$COVERAGE_DIR/multi/${project}-${fault}-${base}
else
  save_dir=$(pwd)/$4
fi

echo "Fault dir: $fault_dir"
echo "Base version dir: $base_dir"
echo "Result dir: $save_dir"

# 1.
# Prepare the fault <project>-<fault>
#
echo "Prepare $fault_dir"
[ ! -d $fault_dir ] && defects4j checkout -p $project -v ${fault}b -w $fault_dir
[ ! -d $fault_dir ] && exit 1;

cd $fault_dir;

# 1-1. Prepare some needed information
defects4j export -p classes.relevant -o classes.relevant;
defects4j export -p tests.trigger -o tests.trigger;
fault_tests_dir=$fault_dir/$(defects4j export -p dir.src.tests)

# 1-2. Clean-up & Run tests
git checkout -- .
[ -f failing_tests ] && rm failing_tests;
defects4j test;

#
# 2.
# Prepare the buggy version <project>-<base>b
#
echo "Prepare $base_dir"
[ ! -d $base_dir ] && defects4j checkout -p $project -v ${base}b -w $base_dir
[ ! -d $base_dir ] && exit 1;

cd $base_dir

# 2-1. Prepare some needed information
defects4j export -p classes.relevant -o classes.relevant;
defects4j export -p tests.trigger -o tests.trigger.base; # the bug-revealing tests of <project>-<base> (used in the overlapping check)
base_classes_bin_dir=$base_dir/$(defects4j export -p dir.bin.classes);
base_tests_bin_dir=$base_dir/$(defects4j export -p dir.bin.tests);
base_classes_dir=$base_dir/$(defects4j export -p dir.src.classes)
base_tests_dir=$base_dir/$(defects4j export -p dir.src.tests)

# 2-2. Clean up existing data
git checkout -- .
[ -d $base_classes_bin_dir ] && rm -rf $base_classes_bin_dir;
[ -d $base_tests_bin_dir ] && rm -rf $base_tests_bin_dir;
[ -f tests.trigger ] && rm tests.trigger;
[ -f failing_tests ] && rm failing_tests;


#
# 3.
# Create the directory to save result data
#

[ ! -d $(dirname $save_dir) ] && mkdir $(dirname $save_dir);
[ -d $save_dir ] && rm -rf $save_dir;
mkdir $save_dir


#
# 4.
# Transplant the fault-revealing tests of <project>-<fault>
# to the <project>-<base>b
#
copy_log=$save_dir/test_copy.log
touch $copy_log

cd $fault_dir
cat tests.trigger | uniq | while read testcase; do
  test_name=$(echo $testcase | grep "[^\:]*$" -o)
  test_class=$(echo $testcase | grep "^[^\:]*" -o)
  test_file="$(echo $test_class | sed 's/\./\//g').java"

  src_file=$fault_tests_dir/$test_file
  dest_file=$base_tests_dir/$test_file
  echo "Copy $testcase from $src_file to $dest_file"

  if [ -f $src_file ]; then
    # if the file exists at destination, create or overwrite the test methods
    cp $dest_file $dest_file.orig
    python3.6 /root/workspace/copy_test.py $src_file $dest_file $test_name >> $copy_log
    if [ ! $? -eq 0 ]; then
      echo "$test_name: error during the copy" >> $copy_log
    else
      diff $dest_file.orig $dest_file >> $copy_log
    fi
    rm $dest_file.orig
  else
    echo "$test_name: no destination file" >> $save_dir/.transplant_error
  fi
done

echo "==========================="
cat $copy_log
echo "==========================="

[ -f $save_dir/.transplant_error ] && exit 1
cd $base_dir
git diff HEAD -- $base_tests_dir > $save_dir/$project-$fault-$base.patch

#
# 5. Compile the test-transplanted version of <project>-<base>b
#
defects4j compile
if [ ! $? -eq 0 ]; then
  echo "Error during the compilation"
  touch $save_dir/.compile_error
  exit 1
fi

#
# 6. Run the test suite (timeout: 10m)
#
timeout 10m defects4j test
if [ ! $? -eq 0 ]; then
  touch $save_dir/.test_error
  exit 1
fi

if [ -f failing_tests ]; then
  grep "\-\-\- \K(.*)" failing_tests -oP > tests.trigger;
else
  touch tests.trigger
  touch failing_tests
fi

#
# 7. Save the test result data
#
echo "=========== Revealing ============="
cat $fault_dir/tests.trigger;
echo ""
echo "============ Failing =============="
cat $base_dir/tests.trigger;

cp $fault_dir/tests.trigger $save_dir/tests.trigger.expected;
cp $base_dir/tests.trigger $save_dir/tests.trigger.actual;
cp $fault_dir/failing_tests $save_dir/failing_tests.expected;
cp $base_dir/failing_tests $save_dir/failing_tests.actual;

#
# 8. Get the classes to instrument (for coverage measurement)
# = classes that are loaded by either the failing tests of <project>-<fault> or <project>-<base>
#
cat $fault_dir/classes.relevant > $base_dir/classes.instrument
echo "\n" >> $base_dir/classes.instrument
cat $base_dir/classes.relevant >> $base_dir/classes.instrument
sort classes.instrument | uniq | awk 'NF' > classes.instrument.uniq
mv classes.instrument.uniq classes.instrument
echo "============================="
cat classes.instrument
echo "\n============================="

#
# 9. Measure the coverage of all failing tests on <project>-<base>b
#
sort $fault_dir/tests.trigger | while read test_method; do
  echo "Measuring coverage of $test_method .............."
  timeout 5m defects4j coverage -t $test_method -i classes.instrument
  if [ ! $? -eq 0 ]; then
    echo "Timeout!"
    touch $save_dir/.coverage_error
  else
    python3.6 /root/workspace/discard_zero_hit.py coverage.xml $save_dir/$test_method.xml
  fi
  rm -rf .classes_instrumented
done

#
# 10. If bug-revealing test cases of two bugs (fault, base) are overlapping, run tests again on the fixed version
#
if [ ! -z "$(comm -12 <(sort "$fault_dir/tests.trigger") <(sort "$base_dir/tests.trigger.base"))" ]; then
  touch $save_dir/.overlapping
  git checkout HEAD~1 $base_classes_dir
  rm failing_tests

  echo $base_classes_bin_dir;
  echo $base_tests_bin_dir;

  # clean up
  [ -d $base_classes_bin_dir ] && rm -rf $base_classes_bin_dir;
  [ -d $base_tests_bin_dir ] && rm -rf $base_tests_bin_dir;

  git status;
  defects4j compile;
  defects4j compile;

  timeout 10m defects4j test
  if [ ! $? -eq 0 ]; then
    touch $save_dir/.test_error
    exit 1
  fi

  if [ -f failing_tests ]; then
    grep "\-\-\- \K(.*)" failing_tests -oP > $save_dir/tests.trigger.actual.fixed
    cp failing_tests $save_dir/failing_tests.actual.fixed
  else
    touch $save_dir/tests.trigger.actual.fixed
    touch $save_dir/failing_tests.actual.fixed
  fi

  git reset HEAD $base_classes_dir
  git checkout -- $base_classes_dir
fi
