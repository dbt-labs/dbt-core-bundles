import copy
from typing import Tuple, Optional

from github import UnknownObjectException
from github.GitRelease import GitRelease
from semantic_version import Version

from release_creation.github_client.client import get_bundle_repo


def _normalize_version_tags(version: Version) -> Version:
    """Normalize the version tags:
    - if pre-release version use 'pre' instead of 'rc' or 'b1' for the tag
    - remove build tag
    """
    if version.prerelease or version.build:
        version.prerelease = ["pre"]
    if version.build:
        version.build = []
    return version


def _normalize_input_version(version: Version) -> Version:
    """Normalize the version:
    - set patch to 0
    """
    version = _normalize_version_tags(version)
    version.patch = 0
    return version


def get_bundle_release(input_version: str) -> Optional[GitRelease]:
    """Retrieve the release matching the input version if it exists.
    Note: we can't use get_release since it won't return draft releases.

    Args:
        input_version (str): semantic version (1.0.0.0rc, 2.3.5) to match against

    Returns:
        Optional[GitRelease]: The release if it exists.
    """
    target_version = Version.coerce(input_version)
    repo = get_bundle_repo()
    releases = repo.get_releases()
    for r in releases:
        release_version = Version.coerce(r.tag_name)
        if (
                release_version.major == target_version.major
                and release_version.minor == target_version.minor
                and (not release_version.prerelease) == (not target_version.prerelease)
                and (not release_version.build) == (not target_version.build)
                and release_version.patch == target_version.patch  # type: ignore
        ):
            return r


def get_latest_bundle_release(input_version: str) -> Tuple[Version, bool, Optional[GitRelease]]:
    """Retrieve the latest release matching the major.minor and release stage
       semantic version if it exists. Ignores the patch version.

    Args:
        input_version (str): semantic version (1.0.0.0rc, 2.3.5) to match against

    Returns:
        Tuple[ Version, is_draft, Optional[GitRelease]]: A tuple of the latest release tag, if it's in a draft state
        and the latest release itself.
    """
    target_version = Version.coerce(input_version)
    latest_version = copy.copy(target_version)
    latest_version = _normalize_input_version(latest_version)
    repo = get_bundle_repo()
    releases = repo.get_releases()  # must have push access to the repo to get draft releases
    latest_release = None
    is_draft = False
    for r in releases:
        release_version = Version.coerce(r.tag_name)
        if (
            release_version.major == latest_version.major
            and release_version.minor == latest_version.minor
            and (not release_version.prerelease) == (not latest_version.prerelease)
            and (not release_version.build) == (not latest_version.build)
            and release_version.patch >= latest_version.patch  # type: ignore
        ):
            latest_version = release_version
            is_draft = r.draft
            latest_release = r
    return _normalize_version_tags(latest_version), is_draft, latest_release