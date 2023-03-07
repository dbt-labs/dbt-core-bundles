from typing import Dict, List, Optional
from semantic_version import Version
import subprocess
import shutil

from release_creation.snapshot.snapshot_config import get_snapshot_config, SnapshotConfig


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


def _download_packages(snapshot_config: SnapshotConfig):
    download_requirements_file = f"{snapshot_config.file_dir}/requirements/{snapshot_config.requirements_prefix}.requirements.txt"
    download_requirements_file += ' --pre' if snapshot_config.is_pre else ''
    subprocess.run(
        ['bash', f"{snapshot_config.file_dir}/download.sh",
         snapshot_config.py_version_tmp_path, download_requirements_file, snapshot_config.py_version],
        check=True)


def _install_packages(snapshot_config: SnapshotConfig):
    subprocess.run(
        ['bash', f"{snapshot_config.file_dir}/install.sh",
         snapshot_config.file_dir, snapshot_config.requirements_prefix,
         snapshot_config.py_version_tmp_path, snapshot_config.py_version],
        check=True)


def _freeze_dependencies(snapshot_config: SnapshotConfig):
    subprocess.run(['bash', f"{snapshot_config.file_dir}/freeze.sh",
                    snapshot_config.requirements_file, snapshot_config.py_version], check=True)


def _download_binaries(snapshot_config: SnapshotConfig):
    extra_platforms = _get_extra_platforms_for_os(snapshot_config.local_os)
    for extra_platform in extra_platforms:
        subprocess.run(
            ['bash', f"{snapshot_config.file_dir}/download_no_deps.sh",
             snapshot_config.py_version_tmp_path, extra_platform, snapshot_config.requirements_file], check=True)


def _generate_assets(snapshot_config: SnapshotConfig) -> dict:
    shutil.make_archive(snapshot_config.py_version_archive_path, 'zip', snapshot_config.py_version_tmp_path)
    created_archive = snapshot_config.py_version_archive_path + ".zip"
    created_asset_name = f"snapshot_core_all_adapters_{snapshot_config.local_os}_{snapshot_config.py_major_minor}.zip"
    req_file_name = f"{SNAPSHOT_REQ_NAME_PREFIX}_{snapshot_config.local_os}_{snapshot_config.py_major_minor}.txt"
    subprocess.run(
        ['bash', f"{snapshot_config.file_dir}/test_archive_install.sh",
         created_archive, snapshot_config.requirements_file], check=True)
    return {created_asset_name: created_archive,
            req_file_name: snapshot_config.requirements_file}


def generate_snapshot(target_version: Version) -> Dict[str, str]:
    """creates a zip archive of the python dependencies for the provided 
       semantic version

    Args:
        target_version (Version): the input version to use when determining 
        the requirements to download.

    Returns:
        Dict[str, str]: dict of generated snapshot assets, key is its name
                        and the value is the path to the file.
    """
    snapshot_configuration = get_snapshot_config(target_version=target_version)
    # Download pip dependencies
    _download_packages(snapshot_configuration)
    # Check install
    _install_packages(snapshot_configuration)
    # Freeze complete requirements (i.e. including transitive dependencies)
    _freeze_dependencies(snapshot_configuration)
    # Use the complete requirements to do a no-deps download (doesn't check system compatibility)
    # This allows us to download requirements for platform architectures other than the local
    _download_binaries(snapshot_configuration)

    # Generate a Zip archive of required packages

    return _generate_assets(snapshot_configuration)
