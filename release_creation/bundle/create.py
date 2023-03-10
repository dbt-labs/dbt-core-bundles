from typing import Dict, List, Optional
from semantic_version import Version
import subprocess
import shutil

from release_creation.bundle.bundle_config import get_bundle_config, BundleConfig

SNAPSHOT_REQ_NAME_PREFIX = "snapshot_requirements"


def _get_extra_platforms_for_os(_os: str) -> List[str]:
    if _os == "mac":
        return ['macosx_10_9_x86_64', 'macosx_11_0_arm64', 'macosx_10_10_intel', 'macosx_12_0_arm64']
    else:
        return ['manylinux_2_17_x86_64', 'manylinux2014_x86_64', 'manylinux2014_i686']


def _get_requirements_prefix(
        major_version: Optional[int], minor_version: Optional[int], is_pre: bool = False
):
    suffix = "latest"
    if is_pre:
        suffix = "pre"
    return f"v{major_version}.{minor_version}.{suffix}"


def _download_packages(bundle_config: BundleConfig):
    download_requirements_file = f"{bundle_config.file_dir}/requirements/{bundle_config.requirements_prefix}.requirements.txt"
    subprocess.run(
        ['bash', f"{bundle_config.file_dir}/download.sh",
         bundle_config.py_version_tmp_path, download_requirements_file, bundle_config.py_version],
        check=True)


def _install_packages(bundle_config: BundleConfig):
    subprocess.run(
        ['bash', f"{bundle_config.file_dir}/install.sh",
         bundle_config.file_dir, bundle_config.requirements_prefix,
         bundle_config.py_version_tmp_path, bundle_config.py_version],
        check=True)


def _freeze_dependencies(bundle_config: BundleConfig):
    subprocess.run(['bash', f"{bundle_config.file_dir}/freeze.sh",
                    bundle_config.requirements_file, bundle_config.py_version], check=True)


def _download_binaries(bundle_config: BundleConfig):
    extra_platforms = _get_extra_platforms_for_os(bundle_config.local_os)
    for extra_platform in extra_platforms:
        subprocess.run(
            ['bash', f"{bundle_config.file_dir}/download_no_deps.sh",
             bundle_config.py_version_tmp_path, extra_platform, bundle_config.requirements_file], check=True)


def _generate_assets(bundle_config: BundleConfig) -> dict:
    shutil.make_archive(bundle_config.py_version_archive_path, 'zip', bundle_config.py_version_tmp_path)
    created_archive = bundle_config.py_version_archive_path + ".zip"
    created_asset_name = f"snapshot_core_all_adapters_{bundle_config.local_os}_{bundle_config.py_major_minor}.zip"
    req_file_name = f"{SNAPSHOT_REQ_NAME_PREFIX}_{bundle_config.local_os}_{bundle_config.py_major_minor}.txt"
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
    _download_packages(bundle_configuration)
    # Check install
    _install_packages(bundle_configuration)
    # Freeze complete requirements (i.e. including transitive dependencies)
    _freeze_dependencies(bundle_configuration)
    # Use the complete requirements to do a no-deps download (doesn't check system compatibility)
    # This allows us to download requirements for platform architectures other than the local
    _download_binaries(bundle_configuration)

    # return a dict with a Zip archive of required packages and the req file
    return _generate_assets(bundle_configuration)
