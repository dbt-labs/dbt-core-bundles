set -e
archive_file="$1"
requirements_file="$2"

rm -rf bundle_pkg_test
unzip -o "${archive_file}" -d bundle_pkg_test

rm -rf test_archive_install
python -m venv test_archive_install
source test_archive_install/bin/activate
DBT_PSYCOPG2_NAME=psycopg2 python -m pip install -r "${requirements_file}" \
  --no-index \
  --find-links ./bundle_pkg_test \
  --pre
dbt --version
# make sure psycopg2 is installed, but not psycopg2-binary
echo -n "Checking psycopg2 install..."
if ! pip freeze | grep psycopg2; then
    echo "psycopg2 is not installed!"
    exit 1
fi
echo ok

echo -n "Checking psycopg2-binary..."
if pip freeze | grep psycopg2-binary; then
    echo "psycopg2-binary is installed and should not be!"
    exit 1
fi
echo ok
deactivate