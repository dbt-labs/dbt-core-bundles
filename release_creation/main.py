import logging
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

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ReleaseOperations(StrEnum):
    create = "create"
    update = "update"


def write_result(version: Version):
    with open(f"{os.getcwd()}/result.env", "w+") as f:
        f.write(f"CREATED_TAG=\"{str(version)}\"")


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
    args = parser.parse_args()
    version = args.input_version
    operation = args.operation
    latest_version, latest_release = get_latest_bundle_release(version)
    if operation == ReleaseOperations.create:
        target_version = latest_version.next_patch()
        target_version.prerelease = latest_version.prerelease
        target_version.build = latest_version.build
        bundle_assets = generate_bundle(target_version)
        logger.info(f"Attempting to create new release for target version: {target_version}")
        create_new_release_for_version(target_version, bundle_assets, latest_release)
        write_result(version=target_version)
    elif operation == ReleaseOperations.update:
        bundle_assets = generate_bundle(latest_version)
        add_assets_to_release(assets=bundle_assets, latest_release=latest_release)


if __name__ == "__main__":
    main()
