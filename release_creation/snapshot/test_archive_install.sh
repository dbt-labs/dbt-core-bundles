set -e
archive_file="$1"
requirements_file="$2"
export DBT_PSYCOPG2_NAME=psycopg2
unzip -o "${archive_file}" -d snapshot_pkg_test
python -m venv test_archive_install
source test_archive_install/bin/activate
python -m pip install -r "${requirements_file}" \
  --no-index \
  --find-links ./snapshot_pkg_test
deactivate