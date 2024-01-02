import os
from typing import List

from semantic_version import Version
import yaml

from release_creation.github_client.client import get_bundle_repo

_BUNDLE_MAP_FILE_NAME = "latest_bundle.yml"
_BUNDLE_MAP_FILE_BRANCH = os.getenv("BUNDLE_MAP_FILE_BRANCH", "main")


def _get_release_version(bundle_version: Version):
    return f"{bundle_version.major}.{bundle_version.minor}"


def get_latest_bundle_from_map(bundle_version: Version):
    release_version = _get_release_version(bundle_version)
    repo = get_bundle_repo()
    bundle_map_file = repo.get_contents(_BUNDLE_MAP_FILE_NAME,
                                        ref=_BUNDLE_MAP_FILE_BRANCH)
    bundles = yaml.safe_load(bundle_map_file.decoded_content)
    latest = bundles['release_version'][release_version]
    print(latest)
    return latest


def update_latest_bundles_in_map(bundle_versions: List[Version]):
    repo = get_bundle_repo()
    bundle_map_file = repo.get_contents(_BUNDLE_MAP_FILE_NAME,
                                        ref=_BUNDLE_MAP_FILE_BRANCH)
    bundles = yaml.safe_load(bundle_map_file.decoded_content)
    updated = []
    for bundle_version in bundle_versions:
        release_version = _get_release_version(bundle_version)
        bundles['release_version'][release_version] = str(bundle_version)
        updated.append(f"{release_version}={bundle_version}")
    repo.update_file(
        path=_BUNDLE_MAP_FILE_NAME,
        message="Updated: " + ", ".join(updated),
        branch=_BUNDLE_MAP_FILE_BRANCH,
        content=yaml.safe_dump(bundles),
        sha=bundle_map_file.sha
    )
