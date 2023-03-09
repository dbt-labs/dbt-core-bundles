import pytest
from semantic_version import Version

from release_creation.snapshot.create import generate_snapshot
import os.path
import zipfile


@pytest.mark.parametrize(argnames="test_version",
                         argvalues=["1.1.0", "1.2.0", "1.3.0", "1.4.0", "1.5.0b1"])
def test_generate_snapshot_creates_a_snapshot_with_valid_version(test_version):
    created_assets = generate_snapshot(Version.coerce(test_version))
    for asset_name, asset_location in created_assets.items():
        assert os.path.isfile(asset_location)
        if ".zip" in asset_name:
            assert zipfile.is_zipfile(asset_location)
        else:
            assert os.path.getsize(asset_location) > 0
