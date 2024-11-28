project=$1
recent=$2
old=$3
save_dir=$4

[ ! -d $save_dir ] && ./check_exist_core.sh $project $recent $old $save_dir
python check_exist.py $save_dir --verbose
