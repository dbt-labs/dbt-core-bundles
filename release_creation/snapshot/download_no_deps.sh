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
# include the psycopg2-binary in mac builds for ease of install
if [[ "$OSTYPE" == darwin* ]]; then 
    pip download wheel Cython~=0.29.0 psycopg2-binary~=2.9.5 \
    --dest $staging \
    --progress-bar off \
    --platform $platform \
    --no-deps
fi

cp -a $staging/. $final_dest/