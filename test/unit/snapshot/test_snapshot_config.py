import pytest
from semantic_version import Version

from release_creation.snapshot.snapshot_config import get_snapshot_config


@pytest.mark.parametrize(argnames="test_input",
                         argvalues=[("1.1.0", False), ("1.5.0", True)])
def test_get_snapshot_config_returns_valid_object(test_input):
    is_pre = test_input[1]
    test_version = Version.coerce(test_input[0])
    conf = get_snapshot_config(target_version=test_version)
    assert conf.is_pre == is_pre
    suffix = "pre" if is_pre else "latest"
    assert conf.requirements_prefix == f"v{test_version.major}.{test_version.minor}.{suffix}"
    assert conf.file_dir is not None
    assert str(test_version) in conf.py_version_archive_path
