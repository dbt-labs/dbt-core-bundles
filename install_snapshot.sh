#!/bin/bash -e
set -e

created_tag="$1"
python_version="$2"
operating_system="$3"
suffix="${operating_system}_${python_version}"
github_url="https://github.com/dbt-labs/dbt-core-snapshots/releases/download/${created_tag}"
archive_file="snapshot_core_all_adapters_${suffix}.zip"
requirements_file="snapshot_requirements_${suffix}.txt"
echo $suffix
export DBT_PSYCOPG2_NAME=psycopg2
curl --fail --retry 5 --retry-all-errors -OL "${github_url}/${archive_file}"
curl --fail --retry 5 --retry-all-errors -OL "${github_url}/${requirements_file}"
unzip -o "${archive_file}" -d snapshot_pkgs
pip install -r "${requirements_file}" \
  --no-index \
  --find-links ./snapshot_pkgs