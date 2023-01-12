#!/bin/bash -e
set -e
target_file="$1"
target_dir="$2"

pip freeze --path ./target/$target_dir > $target_file
if [[ "$OSTYPE" == darwin* ]]; then 
 # mac ships with a different version of sed that requires a delimiter arg
 sed -i "" "s/dbt-core==.*/& --no-binary dbt-postgres/g" $target_file
else
 sed -i "s/dbt-core==.*/& --no-binary dbt-postgres/g" $target_file
fi