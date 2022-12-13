set -e
final_dest=$1
platform=$2
requirements_file=$3
staging="download-no-deps-staging"

pip download -r $requirements_file \
 --dest $staging \
 --progress-bar off \
 --platform $platform \
 --no-deps

cp -a $staging/. $final_dest/