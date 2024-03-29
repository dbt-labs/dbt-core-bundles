#!/bin/bash -e
set -e

tag="$1"
python_version="$2"
os_platform="$3"
suffix="${os_platform}_${python_version}"
github_url="https://github.com/dbt-labs/dbt-core-bundles/releases/download/${tag}"
archive_file="bundle_core_all_adapters_${suffix}.zip"
requirements_file="bundle_requirements_${suffix}.txt"
echo $suffix
export DBT_PSYCOPG2_NAME=psycopg2
curl --fail --retry 5 --retry-all-errors -OL "${github_url}/${archive_file}"
curl --fail --retry 5 --retry-all-errors -OL "${github_url}/${requirements_file}"
unzip -o "${archive_file}" -d bundle_pkgs
pip install -r "${requirements_file}" \
  --no-index \
  --no-cache-dir \
  --ignore-installed \
  --find-links ./bundle_pkgs \
  --pre

unset DBT_PSYCOPG2_NAME