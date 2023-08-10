#!/bin/bash -e

# 1.0 to 1.3 support python 3.8 to 3.10
# 1.4 added support for python 3.11
# Note that Python 3.8 is manually added to the matrix so not included here

minor_version="$1"
if [[ ${minor_version} < 4 ]]
then
py_versions='["3.8", "3.9", "3.10"]'
else
py_versions='["3.8", "3.9", "3.10", "3.11"]'
fi
echo $py_versions
echo "versions=$py_versions" >> "$GITHUB_OUTPUT"
