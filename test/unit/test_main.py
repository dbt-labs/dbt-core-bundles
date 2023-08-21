from unittest.mock import Mock

from semantic_version import Version

from release_creation.bundle import create
from release_creation.github_client import get_release, create_release
from release_creation.main import main, ReleaseOperations


def test_main_calls_correct_functions(monkeypatch):
    argparse_mock = Mock(parse_args=lambda: Mock(input_version="1.0.0", operation=ReleaseOperations.create))
    monkeypatch.setattr("argparse.ArgumentParser", lambda: argparse_mock)
    get_latest_bundle_release_mock = Mock(return_value=(Version("1.0.0"), False, None))
    monkeypatch.setattr(get_release, "get_latest_bundle_release", get_latest_bundle_release_mock)
    create_release_mock = Mock()
    monkeypatch.setattr(create_release, "create_new_draft_release_for_version", create_release_mock)
    generate_bundle_mock = Mock(return_value={})
    monkeypatch.setattr(create, "generate_bundle", generate_bundle_mock)
    main()
    assert get_latest_bundle_release_mock.call_count == 1
    assert create_release_mock.call_count == 1
    assert generate_bundle_mock.call_count == 1


def test_main_calls_correct_functions_with_dev_input(monkeypatch):
    argparse_mock = Mock(parse_args=lambda: Mock(input_version="0.0.0", operation=ReleaseOperations.create))
    monkeypatch.setattr("argparse.ArgumentParser", lambda: argparse_mock)
    get_latest_bundle_release_mock = Mock()
    monkeypatch.setattr(get_release, "get_latest_bundle_release", get_latest_bundle_release_mock)
    create_release_mock = Mock()
    monkeypatch.setattr(create_release, "create_dev_release", create_release_mock)
    generate_bundle_mock = Mock(return_value={})
    monkeypatch.setattr(create, "generate_bundle", generate_bundle_mock)
    main()
    assert get_latest_bundle_release_mock.call_count == 0
    assert create_release_mock.call_count == 1
    assert generate_bundle_mock.call_count == 1
