from typing import Dict, Optional
from semantic_version import Version
import subprocess
import shutil

from release_creation.bundle.bundle_config import get_bundle_config, BundleConfig
from release_creation.bundle.bundle_os import PIP_PLATFORM_OS_VALUES
from release_creation.release_logger import get_logger

BUNDLE_REQ_NAME_PREFIX = "bundle_requirements"
logger = get_logger()

def _get_requirements_prefix(
        major_version: Optional[int], minor_version: Optional[int], is_pre: bool = False
):
    suffix = "latest"
    if is_pre:
        suffix = "pre"
    return f"v{major_version}.{minor_version}.{suffix}"


def _download_packages(bundle_config: BundleConfig):
    """
    Download wheels for build dependencies and packages specified in the bundle requirements file.

    Taking 1.8.0b1 running locally on MacOS/py38 as an example:
        1. Create a fresh `./tmp/mac/3.8` directory
        2. Update `pip`
        3. Download `./release_creation/bundle/requirements/v1.8.pre-requirements.txt` into `./tmp/mac/3.8`
        4. Download `wheel` into `./tmp/mac/3.8`
    """
    download_requirements_file = f"{bundle_config.file_dir}/requirements/{bundle_config.requirements_prefix}.requirements.txt"
    subprocess.run(
        ['bash', f"{bundle_config.file_dir}/download.sh",
         bundle_config.py_version_tmp_path, download_requirements_file, bundle_config.py_version],
        check=True)


def _install_packages(bundle_config: BundleConfig):
    """
    Install packages specified in the bundle requirements file using the local downloaded versions.

    Taking 1.8.0b1 running locally on MacOS/py38 as an example:
        1. Create a fresh `./target` directory
        2. Install `./tmp/mac/3.8` into `./target/3.8.18`
            using `./release_creation/bundle/requirements/v1.8.pre-requirements.txt`
    """
    subprocess.run(
        ['bash', f"{bundle_config.file_dir}/install.sh",
         bundle_config.file_dir, bundle_config.requirements_prefix,
         bundle_config.py_version_tmp_path, bundle_config.py_version],
        check=True)


def _freeze_dependencies(bundle_config: BundleConfig):
    """
    Freeze specific versions of dependencies into a requirements file.

    Taking 1.8.0b1 running locally on MacOS/py38 as an example:
        1. Run `pip freeze` on `./target/3.8.18`
        2. Save the results to `./release_creation/bundle/bundle.requirements.3.8.txt` (overwrite)
        3. Append ` --no-binary dbt-postgres` to the `dbt-core==1.8.0b1` line the above file
            a. TODO: This only makes sense for `dbt-core<=1.7`, but it doesn't hurt anything keeping it here
    """
    subprocess.run(['bash', f"{bundle_config.file_dir}/freeze.sh",
                    bundle_config.requirements_file, bundle_config.py_version], check=True)


def _download_binaries(bundle_config: BundleConfig):
    """
    Download platform-specific wheels, with no transient dependencies, for packages specified in the pip freeze file.
    Also download platform-specific wheels, such as `Cython~=0.29.0` and `psycopg2-binary~=2.9.5` for MacOS.

    Taking 1.8.0b1 running locally on MacOS/py38 as an example:
        1. Create fresh `./download-no-deps-staging`
        2. Download wheels for packages specified in `./release_creation/bundle/bundle.requirements.3.8.txt`
            into `./download-no-deps-staging` for the 'macosx_10_9_x86_64' platform
        3. Download wheels for `wheel`, `Cython~=0.29.0`, and `psycopg2-binary~=2.9.5`
            into `./download-no-deps-staging` for the 'macosx_10_9_x86_64' platform
        4. Copy the contents of `./download-no-deps-staging` into `./tmp/mac/3.8`
        5. Do steps 2-4 for the 'macosx_11_0_arm64' and 'macosx_12_0_arm64' platforms
    """
    extra_platforms = PIP_PLATFORM_OS_VALUES[bundle_config.local_os]
    for extra_platform in extra_platforms:
        subprocess.run(
            ['bash', f"{bundle_config.file_dir}/download_no_deps.sh",
             bundle_config.py_version_tmp_path, extra_platform, bundle_config.requirements_file], check=True)


def _generate_assets(bundle_config: BundleConfig) -> dict:
    """
    Create an archive from the local wheels and test that this archive can be installed with `pip`.

    Taking 1.8.0b1 running locally on MacOS/py38 as an example:
        1. Remove `./bundle_pkg_test` and `./test_archive_install`
        2. Create `./dbt-core-all-adapters-bundle-1.8.0-b1-mac-3.8.zip` from `./tmp/mac/3.8`
            a. TODO: This potentially provides too many wheels, as generics and platform-specifics are available.
        3. Unzip `./dbt-core-all-adapters-bundle-1.8.0-b1-mac-3.8.zip` into `./bundle_pkg_test`
        4. Create a virtual environment named `./test_archive_install`
        5. Install `./bundle_pkg_test` into `./test_archive_install`
            using `./release_creation/bundle/requirements/v1.8.pre-requirements.txt`
        6. Verify installation using `dbt --version`
        7. Verify `psycopg2` is installed and `psycopg2-binary` is not installed
    """
    shutil.make_archive(bundle_config.py_version_archive_path, 'zip', bundle_config.py_version_tmp_path)
    created_archive = bundle_config.py_version_archive_path + ".zip"
    created_asset_name = f"bundle_core_all_adapters_{bundle_config.local_os}_{bundle_config.py_major_minor}.zip"
    req_file_name = f"{BUNDLE_REQ_NAME_PREFIX}_{bundle_config.local_os}_{bundle_config.py_major_minor}.txt"
    subprocess.run(
        ['bash', f"{bundle_config.file_dir}/test_archive_install.sh",
         created_archive, bundle_config.requirements_file], check=True)
    return {created_asset_name: created_archive,
            req_file_name: bundle_config.requirements_file}


def generate_bundle(target_version: Version) -> Dict[str, str]:
    """creates a zip archive of the python dependencies for the provided 
       semantic version

    Args:
        target_version (Version): the input version to use when determining 
        the requirements to download.

    Returns:
        Dict[str, str]: dict of generated bundle assets, key is its name
                        and the value is the path to the file.
    """
    bundle_configuration = get_bundle_config(target_version=target_version)
    # Download pip dependencies
    logger.info("===========================\n")
    logger.info(f"Downloading dependencies")
    _download_packages(bundle_configuration)
    # Check install
    logger.info("===========================\n")
    logger.info(f"Installing dependencies")
    _install_packages(bundle_configuration)
    # Freeze complete requirements (i.e. including transitive dependencies)
    logger.info("===========================\n")
    logger.info(f"Freezing dependencies for")
    _freeze_dependencies(bundle_configuration)
    # Use the complete requirements to do a no-deps download (doesn't check system compatibility)
    # This allows us to download requirements for platform architectures other than the local
    logger.info("===========================\n")
    logger.info(f"Downloading binaries for")
    _download_binaries(bundle_configuration)

    # return a dict with a Zip archive of required packages and the req file
    logger.info("===========================\n")
    logger.info(f"Generating assets")
    return _generate_assets(bundle_configuration)
