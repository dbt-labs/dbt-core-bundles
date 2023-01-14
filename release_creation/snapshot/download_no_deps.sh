#!/bin/bash -e
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

# some mac builds needs wheel and cython installed
if [[ "$OSTYPE" == darwin* ]]; then 
    pip download wheel cython \
    --dest $staging \
    --progress-bar off \
    --platform $platform \
    --no-deps
fi

cp -a $staging/. $final_dest/