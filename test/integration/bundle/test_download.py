from pathlib import Path
from semantic_version import Version
import sys

import pytest

from release_creation.bundle.bundle_config import get_bundle_config
from release_creation.bundle.create import _download_packages


@pytest.mark.parametrize("test_version", ["1.8.0b1"])
def test_correct_version_of_psycopg2(test_version):
    if sys.version_info == (3, 10) and Version.coerce(test_version) >= Version.coerce(
        "1.5.0"
    ):
        pytest.skip("We run test for Python 3.11 with version 1.5.0+ of the bundle")

    bundle_configuration = get_bundle_config(Version.coerce(test_version))
    _download_packages(bundle_configuration)

    tmp_dir = Path(bundle_configuration.py_version_tmp_path)
    assert tmp_dir.is_dir()
    psycopg2_is_found = False
    for file in tmp_dir.iterdir():
        if "psycopg2" in file.name:
            psycopg2_is_found = True
            assert "psycopg2-binary" not in file.name
            assert "psycopg2_binary" not in file.name
    assert psycopg2_is_found
