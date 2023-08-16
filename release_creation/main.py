from semantic_version import Version
from strenum import StrEnum
import os
import argparse

from release_creation.github_client import create_release
from release_creation.bundle import create
from release_creation.github_client import get_release
from release_creation.release_logger import get_logger

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DEV_VERSION = "0.0.0.0dev"
logger = get_logger()


class ReleaseOperations(StrEnum):
    create = "create"
    update = "update"


def set_output(name, value):
    os.system(f"""echo "{name}={value}" >> $GITHUB_OUTPUT""")


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
    if version.startswith("0.0"):
        latest_version = Version.coerce(DEV_VERSION)
        is_draft = True
        latest_release = None
    else:
        latest_version, is_draft, latest_release = get_release.get_latest_bundle_release(version)
        logger.info(f"Retrieved latest version: {latest_version} "
                    f"and latest release: {latest_release.tag_name if latest_release else None}")
    if operation == ReleaseOperations.create:
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
        logger.info(f"Attempting to create new draft release for target version: {target_version}")

        if str(target_version) == DEV_VERSION:
            create_release.create_dev_release(release_version=target_version, assets=bundle_assets)
        else:
            create_release.create_new_draft_release_for_version(
                release_version=target_version,
                assets=bundle_assets,
                latest_release=latest_release,
            )
        set_output(name="created_tag", value=target_version)
    elif operation == ReleaseOperations.update:
        if not is_draft:
            raise RuntimeError(f"No draft release exists for version {latest_version}.  Nothing to update.")
        logger.info(f"Attempting to update existing draft release for latest version: {latest_version}")
        bundle_assets = create.generate_bundle(target_version=latest_version)
        logger.debug(f"latest_release: {latest_release}")
        create_release.add_assets_to_release(assets=bundle_assets, latest_release=latest_release)


if __name__ == "__main__":
    main()
