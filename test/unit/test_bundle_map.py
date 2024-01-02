from unittest.mock import patch, Mock, ANY

import yaml
from semantic_version import Version

from release_creation.bundle_map import get_latest_bundle_from_map, update_latest_bundles_in_map

test_map = yaml.safe_load("""
                    release_version:
                      '1.0': 1.0.30
                      '1.1': 1.1.19
                      '1.2': 1.2.19
                    """)


def mock_safe_load(*args, **kwargs):
    return test_map


def mock_repo_get_contents(*args, **kwargs):
    return Mock(decoded_content=yaml.safe_dump(test_map))


_MOCK_REPO_UPDATE = Mock()
_MOCK_REPO = Mock(get_contents=mock_repo_get_contents, update_file=_MOCK_REPO_UPDATE)


@patch("release_creation.bundle_map.get_bundle_repo", Mock(return_value=_MOCK_REPO))
def test_get_latest_bundle_from_map_with_valid_version():
    bundle_version = Version.coerce("1.1.0")
    expected_version = "1.1.19"

    actual_version = get_latest_bundle_from_map(bundle_version)

    assert actual_version == expected_version


@patch("release_creation.bundle_map.get_bundle_repo", Mock(return_value=_MOCK_REPO))
def test_update_latest_bundles_in_map():
    bundle_versions = [Version.coerce("1.1.20"), Version.coerce("1.3.0")]
    expected_map = yaml.safe_load("""
                    release_version:
                        '1.0': 1.0.30
                        '1.1': 1.1.20
                        '1.2': 1.2.19
                        '1.3': 1.3.0
                    """)

    update_latest_bundles_in_map(bundle_versions)
    calls = _MOCK_REPO.mock_calls
    kwargs_call = calls[0].kwargs
    assert yaml.safe_load(kwargs_call['content']) == expected_map
    assert kwargs_call['message'] == "Updated: 1.1=1.1.20, 1.3=1.3.0"
