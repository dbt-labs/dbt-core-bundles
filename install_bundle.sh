#!/bin/bash -e
set -e

created_asset_url="$1"
req_file_url="$2"
python_version="$3"
os_platform="$4"
suffix="${os_platform}_${python_version}"
archive_file="bundle_core_all_adapters_${suffix}.zip"
requirements_file="bundle_requirements_${suffix}.txt"
echo $suffix
export DBT_PSYCOPG2_NAME=psycopg2
curl --fail --retry 5 --retry-all-errors -OL "${created_asset_url}"
curl --fail --retry 5 --retry-all-errors -OL "${req_file_url}"
unzip -o "${archive_file}" -d bundle_pkgs
pip install -r "${requirements_file}" \
  --no-index \
  --no-cache-dir \
  --ignore-installed \
  --find-links ./bundle_pkgs \
  --pre

unset DBT_PSYCOPG2_NAME

