#!/bin/bash -e

# 1.0 to 1.3 support python 3.8 to 3.10
# 1.4 added support for python 3.11
# 1.7 added support for python 3.12

major_version="$1"
minor_version="$2"
# if major.minor is 0.0 that is a dev release
if [[ ${major_version} == 0 && ${minor_version} == 0 ]]
then
py_versions='["3.8", "3.9", "3.10", "3.11", "3.12"]'
elif [[ ${major_version} == 1 && ${minor_version} < 4  ]]
then
py_versions='["3.8", "3.9", "3.10"]'
elif [[ ${major_version} == 1 && ${minor_version} > 3 && ${minor_version} < 7 ]]
then
py_versions='["3.8", "3.9", "3.10", "3.11"]'
else
py_versions='["3.8", "3.9", "3.10", "3.11", "3.12"]'
fi
echo $py_versions
echo "versions=$py_versions" >> "$GITHUB_OUTPUT"
