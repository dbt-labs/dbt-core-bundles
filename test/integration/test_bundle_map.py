from unittest.mock import patch

from semantic_version import Version

from release_creation.bundle_map import get_latest_bundle_from_map, update_latest_bundles_in_map


@patch("release_creation.bundle_map._BUNDLE_MAP_FILE_BRANCH", "test")
def test_map_is_gettable_and_updateable():
    version = "1.1.0"
    current_version = get_latest_bundle_from_map(Version(version))
    current_version = Version(current_version)
    to_update = current_version.next_patch()
    update_latest_bundles_in_map([to_update])
    updated_version = get_latest_bundle_from_map(Version(version))
    assert updated_version == str(to_update)

