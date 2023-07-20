import os
import unittest
from unittest.mock import Mock

from semantic_version import Version

from release_creation.github_client import releases


def test_create_new_release_for_version_correctly_calls_github(monkeypatch):
    mock_github = Mock()
    release_mock = Mock(get_assets=lambda: [])
    os.environ["GH_ACCESS_TOKEN"] = "someToken"
    test_version = Version.coerce("1.0.0")
    monkeypatch.setattr(releases, "get_github_client", lambda: mock_github)
    monkeypatch.setattr(releases, "_diff_bundle_requirements",
                        lambda bundle_req_path, latest_release: "No prior bundle")
    releases.create_new_release_for_version(release_version=test_version,
                                            assets={"bundle_requirements.txt": "path/to/req_files.txt"},
                                            latest_release=release_mock)
    calls = mock_github.mock_calls
    assert calls[0].args == ('dbt-labs/dbt-core-bundles',)
    assert calls[1].kwargs == {'tag': '1.0.0', 'name': 'Bundle for dbt v1.0',
                               'prerelease': False,
                               'message': 'No prior bundle'}
    assert calls[2].kwargs == {'path': 'path/to/req_files.txt',
                               'name': 'bundle_requirements.txt'}
