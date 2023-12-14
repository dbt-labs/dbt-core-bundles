import sys
import subprocess

import pytest
from semantic_version import Version

from release_creation.bundle.create import generate_bundle
import os.path
import zipfile


@pytest.mark.parametrize("python_version", [sys.version_info])
@pytest.mark.parametrize(
    argnames="test_version",
    argvalues=["0.0.0", "1.3.0", "1.4.0", "1.5.0", "1.6.0", "1.7.0b1", "1.7.0"],
)
def test_generate_bundle_creates_a_bundle_with_valid_version(test_version, python_version):
    if python_version >= (3, 11) and Version.coerce(test_version) < Version.coerce("1.5.0"):
        pytest.skip("Python 3.11+ requires at least version 1.5.0 of the bundle")
    if python_version == (3, 10) and Version.coerce(test_version) >= Version.coerce("1.5.0"):
        pytest.skip("We run test for Python 3.11 with version 1.5.0+ of the bundle")
    created_assets = generate_bundle(Version.coerce(test_version))
    for asset_name, asset_location in created_assets.items():
        # check if the file exists
        assert os.path.isfile(asset_location)
        # check if files are empty
        assert os.path.getsize(asset_location) > 0

        if ".zip" in asset_name:
            assert zipfile.is_zipfile(asset_location)

        elif ".txt" in asset_name:
            try:
                subprocess.run(f"pip uninstall -r {asset_location}")
            except Exception as e:
                print(e)
        else:
            raise Exception("Unknown file type returned")
