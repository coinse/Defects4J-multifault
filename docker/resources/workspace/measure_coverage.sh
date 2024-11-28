project=$1
version=$2

project_dir=$TMP_DIR/$project-$version

echo "Prepare $project_dir"
[ -d $project_dir] && rm $project_dir
defects4j checkout -p $project -v $version -w $project_dir
cd $project_dir && defects4j compile;
[ ! -f classes.relevant ] && defects4j export -p classes.relevant -o classes.relevant;
[ ! -f dir.bin.classes ] && defects4j export -p dir.bin.classes -o dir.bin.classes;
python /root/workspace/get_all_classes.py $project_dir $(cat dir.bin.classes) $project_dir/classes.all;

cat classes.all;

all_tests=/root/workspace/all_tests/$project-$version
result_path=$COVERAGE_DIR/single/$project-$version
[ ! -d $COVERAGE_DIR/single ] && mkdir $COVERAGE_DIR/single;
[ ! -d $result_path ] && mkdir ${result_path}

sort $all_tests | while read test_method; do
  echo "Measuring coverage of $test_method .............."
  defects4j coverage -t $test_method -i classes.all #classes.relevant
  mv coverage.xml ${result_path}/$test_method.xml
done
