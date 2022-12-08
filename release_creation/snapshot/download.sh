set -e
base_dir=$1

rm -rf $base_dir
mkdir  -p $base_dir

python -m pip download \
 --progress-bar off \
 --prefer-binary \
 --dest $base_dir \
 --no-cache-dir \
 $2