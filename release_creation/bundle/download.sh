set -e
export DBT_PSYCOPG2_NAME=psycopg2
base_dir="$1"
download_reqs_file="$2"
rm -rf $base_dir
mkdir  -p $base_dir
python -m pip install --upgrade pip
python -m pip install setuptools_scm<8.0.0

python -m pip download \
 --progress-bar off \
 --prefer-binary \
 --dest $base_dir \
 --no-cache-dir \
 -r $download_reqs_file

python -m pip download \
 --progress-bar off \
 --dest $base_dir \
 wheel
