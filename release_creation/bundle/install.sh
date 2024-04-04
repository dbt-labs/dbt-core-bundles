set -e
base_dir="$1"
requirements_file_prefix="$2"
link_dir="$3"
target_dir="$4"
rm -rf target
mkdir target

pip install -r "$base_dir"/requirements/"$requirements_file_prefix".requirements.txt \
--no-index  \
--force-reinstall \
--find-links ./"$link_dir" \
--target "./target/$target_dir"
