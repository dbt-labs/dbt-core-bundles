import logging
from strenum import StrEnum
import os
from semantic_version.base import Version
import argparse

from github_client.releases import (
    create_new_release_for_version,
    get_latest_snapshot_release,
    add_assets_to_release,
)
from snapshot.create import generate_snapshot

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)


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
    latest_version, latest_release = get_latest_snapshot_release(version)
    if operation == ReleaseOperations.create:
        target_version = latest_version.next_patch()
        target_version.prerelease = latest_version.prerelease
        target_version.build = latest_version.build
        snapshot_assets = generate_snapshot(target_version)
        logger.info(f"Attempting to create new release for target version: {target_version}")
        create_new_release_for_version(target_version, snapshot_assets, latest_release)
        write_result(version=target_version)
    elif operation == ReleaseOperations.update:
        snapshot_assets = generate_snapshot(latest_version)
        add_assets_to_release(assets=snapshot_assets, latest_release=latest_release)


if __name__ == "__main__":
    main()
