import os
from unittest.mock import Mock

from semantic_version import Version
from release_creation.github_client import client
from release_creation.github_client import create_release


def test_create_new_release_for_version_correctly_calls_github(monkeypatch):
    mock_github = Mock()
    release_mock = Mock(get_assets=lambda: [])
    os.environ["GH_ACCESS_TOKEN"] = "someToken"
    test_version = Version.coerce("1.0.0")
    monkeypatch.setattr(client, "get_bundle_repo", lambda: mock_github)
    monkeypatch.setattr(create_release, "_diff_bundle_requirements",
                        lambda bundle_req_path, latest_release: "No prior bundle")
    create_release.create_new_draft_release_for_version(release_version=test_version,
                                                        assets={"bundle_requirements.txt": "path/to/req_files.txt"},
                                                        latest_release=release_mock)
    calls = mock_github.mock_calls
    assert calls[0].kwargs == {'tag': '1.0.0', 'name': 'Bundle for dbt v1.0',
                               'prerelease': False,
                               'draft': True,
                               'message': 'No prior bundle'}
    assert calls[1].kwargs == {'path': 'path/to/req_files.txt',
                               'name': 'bundle_requirements.txt'}


def test_create_new_release_for_dev_bundle(monkeypatch):
    mock_github = Mock()
    os.environ["GH_ACCESS_TOKEN"] = "someToken"
    test_version = Version.coerce("0.0.0")
    monkeypatch.setattr(client, "get_bundle_repo", lambda: mock_github)
    create_release.create_dev_release(release_version=test_version,
                                        assets={"bundle_requirements.txt": "path/to/req_files.txt"}
                                      )
    calls = mock_github.mock_calls
    assert calls[0].args[0] == '0.0.0'
    assert str(calls[1]) == 'call.get_release().delete_release()'
    assert calls[2].kwargs == {'tag': '0.0.0', 'name': 'dev Bundle for dbt',
                               'prerelease': True,
                               'draft': True,
                               'message': 'This is a dev bundle release. '
                                          'It is meant for testing the latest changes in dbt-* packages.'}
    assert calls[3].kwargs == {'path': 'path/to/req_files.txt',
                               'name': 'bundle_requirements.txt'}
