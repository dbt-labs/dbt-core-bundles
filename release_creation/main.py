from strenum import StrEnum
import os
from semantic_version.base import Version
import argparse

from release_creation.github_client.releases import (
    create_new_release_for_version,
    get_latest_bundle_release,
    add_assets_to_release,
)
from release_creation.bundle.create import generate_bundle
from release_creation.release_logger import get_logger

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
logger = get_logger()

class ReleaseOperations(StrEnum):
    create = "create"
    update = "update"


def set_output(name, value):
    os.system(f"""echo "{name}={value}" >> $GITHUB_OUTPUT""")


def main():
    """
    Implements two workflows:
    * Create: Generate a net new release for a major.minor version which corresponds to core.
    * Update: Add release assets to an existing release.

    Input version is a string that corresponds to the semver standard, 
    see https://semver.org/ for more info. 
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", required=True, type=ReleaseOperations)
    parser.add_argument("--input-version", required=True, type=str)  # e.g. 1.3.4
    parser.add_argument("--draft", required=True, type=str)  # e.g. true/false
    args = parser.parse_args()
    version = args.input_version
    operation = args.operation
    draft = args.draft
    latest_version, latest_release = get_latest_bundle_release(version)
    logger.info(f"Retrieved latest version: {latest_version} "
                f"and latest release: {latest_release.tag_name if latest_release else None}")
    if operation == ReleaseOperations.create:
        target_version = latest_version
        target_version.prerelease = latest_version.prerelease
        target_version.build = latest_version.build
        # pre-release semver versions are not incremented by next_patch
        target_version.patch += 1
        bundle_assets = generate_bundle(target_version=target_version)
        logger.info(f"Attempting to create new release for target version: {target_version}")
        created_release = create_new_release_for_version(release_version=target_version, assets=bundle_assets, latest_release=latest_release, draft=draft)
        logger.debug(f"Release created zipball url: {created_release.zipball_url}")
        logger.debug(f"Release created url: {created_release.url}")
        logger.debug(f"Release created id: {created_release.id}")
        logger.debug(f"Release created get_assets: {created_release.get_assets()}")
        logger.debug(f"Release created assets: {created_release.assets}")
        set_output(name="created_tag", value=created_release.tag_name)
        set_output(name="download_url", value=created_release.html_url)
    elif operation == ReleaseOperations.update:
        bundle_assets = generate_bundle(latest_version)
        logger.debug(f"latest_release: {latest_release}")
        # add_assets_to_release(assets=bundle_assets, latest_release=latest_release)


if __name__ == "__main__":
    main()
