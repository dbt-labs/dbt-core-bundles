from semantic_version import Version
from strenum import StrEnum
import os
import argparse

from release_creation.github_client import create_release
from release_creation.bundle import create
from release_creation.github_client import get_release
from release_creation.release_logger import get_logger

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DEV_VERSION = "0.0.0+dev"
logger = get_logger()


class ReleaseOperations(StrEnum):
    create = "create"
    update = "update"


def set_output(name, value):
    os.system(f"""echo "{name}={value}" >> $GITHUB_OUTPUT""")


def execute_create_bundle_release(version: str):
    if version.startswith("0.0"):
        latest_version = Version.coerce(DEV_VERSION)
        latest_release = None
    else:
        latest_version, is_draft, latest_release = get_release.get_latest_bundle_release(version)
        logger.info(f"Retrieved latest version: {latest_version} "
                    f"and latest release: {latest_release.tag_name if latest_release else None}")
        if is_draft:
            raise RuntimeError(
                f"A draft release already exists for version {latest_version}. "
                f"It needs to be published or deleted first")
    target_version = latest_version
    target_version.prerelease = latest_version.prerelease
    target_version.build = latest_version.build
    # if a latest release exists then there is a prior patch version
    if latest_release:
        # pre-release semver versions are not incremented by next_patch
        target_version.patch += 1

    bundle_assets = create.generate_bundle(target_version=target_version)

    if str(target_version) == DEV_VERSION:
        create_release.create_dev_release(release_version=target_version, assets=bundle_assets)
    else:
        logger.info(f"Attempting to create new draft release for target version: {target_version}")
        create_release.create_new_draft_release_for_version(
            release_version=target_version,
            assets=bundle_assets,
            latest_release=latest_release,
        )
    set_output(name="created_tag", value=target_version)


def execute_update_bundle_release(version: str):
    release_to_update = get_release.get_bundle_release(version)
    if not release_to_update:
        raise RuntimeError(f"Release {version} does not exist")
    logger.info(f"Attempting to update existing release for version: {version}")
    target_version = Version.coerce(version)
    bundle_assets = create.generate_bundle(target_version=target_version)
    logger.debug(f"latest_release: {release_to_update}")
    create_release.add_assets_to_release(assets=bundle_assets, latest_release=release_to_update)


def main():
    """
    Implements two workflows:
    * Create: Generate a net new draft release for a major.minor version which corresponds to core.
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
    if operation == ReleaseOperations.create:
        execute_create_bundle_release(version)
    elif operation == ReleaseOperations.update:
        execute_update_bundle_release(version)


if __name__ == "__main__":
    main()
