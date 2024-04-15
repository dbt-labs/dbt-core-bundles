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
dbt --version

# make sure psycopg2 is installed, but not psycopg2-binary
echo -n "Checking psycopg2 install..."
PSYCOPG2_PIP_ENTRY=$(pip list | grep "psycopg2 " || pip list | grep psycopg2-binary)
PSYCOPG2_NAME="${PSYCOPG2_PIP_ENTRY%% *}"
if [[ "$OSTYPE" == linux* && "${PSYCOPG2_NAME}" == "pscyopg2" ]]; then
  echo "psycopg2 is installed on linux as expected"
  echo ok
else
  echo "psycopg2-binary is installed on linux and should not be!"
  exit 1
fi
if [[ "$OSTYPE" == darwin* && "${PSYCOPG2_NAME}" == "pscyopg2-binary" ]]; then
  echo "psycopg2-binary is installed on linux as expected"
  echo ok
else
  echo "psycopg2 is installed on macos and should not be!"
  exit 1
fi
if [[ "$OSTYPE" != linux* && "$OSTYPE" != darwin* ]]; then
  echo "unexpected OSTYPE:"
  echo "$OSTYPE"
  exit 1
fi

deactivate
