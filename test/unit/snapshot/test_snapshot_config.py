from semantic_version import Version

from release_creation.snapshot.snapshot_config import get_snapshot_config


def test_get_snapshot_config_returns_object():

    conf = get_snapshot_config(target_version=Version("1.5.0"))
    print(conf)