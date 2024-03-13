set -e
archive_file="$1"
requirements_file="$2"
export DBT_PSYCOPG2_NAME=psycopg2

rm -rf bundle_pkg_test
unzip -o "${archive_file}" -d bundle_pkg_test

rm -rf test_archive_install
python -m venv test_archive_install
source test_archive_install/bin/activate

python -m pip install -r "${requirements_file}" \
  --no-index \
  --find-links ./bundle_pkg_test \
  --pre

# make sure dbt-core is installed and can run a basic command
dbt --version

# make sure psycopg2 is installed, but not psycopg2-binary
echo -n "Checking psycopg2 is installed..."
if ! pip freeze | grep psycopg2; then
    echo "psycopg2 is not installed!"
    exit 1
fi
echo ok

echo -n "Checking psycopg2-binary is not installed..."
if pip freeze | grep psycopg2-binary; then
    echo "psycopg2-binary is installed and should not be!"
    exit 1
fi
echo ok

deactivate
