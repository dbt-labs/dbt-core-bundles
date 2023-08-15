from unittest.mock import Mock

import pytest
from semantic_version import Version

from release_creation.github_client.get_release import get_latest_bundle_release


@pytest.mark.parametrize(["input_versions", "output_versions"],
                         [("1.2.0b1", "1.2.0-pre"), ("1.2.0", "1.2.1"), ("1.3.0a1", "1.3.0-pre"),
                          ("1.4.0pre", "1.4.0-pre"), ("1.5.1", "1.5.6")])
def test_get_latest_bundle_release_gets_latest_release(monkeypatch, input_versions, output_versions):
    mock_version_1_1 = Mock(tag_name="1.1.0")
    mock_version_1_2_0 = Mock(tag_name="1.2.0", is_draft=False)
    mock_version_1_2_1 = Mock(tag_name="1.2.1", is_draft=True)
    mock_version_1_3_1 = Mock(tag_name="1.3.1", is_draft=True)
    mock_version_1_5_6 = Mock(tag_name="1.5.6", is_draft=True)
    repo_mock = Mock(get_releases=lambda: [mock_version_1_2_1, mock_version_1_2_0, mock_version_1_1,
                                           mock_version_1_3_1, mock_version_1_5_6])
    monkeypatch.setattr("release_creation.github_client.get_release.get_bundle_repo", lambda: repo_mock)
    input_version = Version.coerce(input_versions)
    latest_version, is_draft, latest_release = get_latest_bundle_release(str(input_version))
    assert str(latest_version) == output_versions
