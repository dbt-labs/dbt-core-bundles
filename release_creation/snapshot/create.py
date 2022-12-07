from typing import Dict, List, Optional, Tuple
from semantic_version import Version
import os
import platform
import subprocess
import shutil


_OUTPUT_ARCHIVE_FILE_BASE = "dbt-core-all-adapters-snapshot"
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
_SNAPSHOT_FILE = f"{_FILE_DIR}/snapshot.requirements.txt"
_PYTHON_VERSIONS = ['3.8.11','3.9.1','3.10.0']

def _get_local_platform() -> str:
    local_sys = platform.system()
    if local_sys == "Linux":
        return "linux"
    elif local_sys == "Windows":
        return "windows"
    elif local_sys == "Darwin":
         return "mac"
    else:
        raise ValueError(f"Unsupported system {local_sys}")


def _get_requirements_prefix(
    major_version: Optional[int], minor_version: Optional[int], is_pre: bool = False
):
    suffix = "latest"
    if is_pre:
        suffix = "pre"
    return f"v{major_version}.{minor_version}.{suffix}"


def _generate_download_command_args(
    requirements_prefix: str, is_pre: bool = False
) -> str:
    download_command = ""
    if is_pre:
        download_command += " --pre"
    download_command += f" -r {_FILE_DIR}/requirements/{requirements_prefix}.requirements.txt"
    return download_command


def generate_snapshot(target_version: Version) -> Dict[str, str]:
    is_pre = True if target_version.prerelease else False
    requirements_prefix = _get_requirements_prefix(
        major_version=target_version.major, minor_version=target_version.minor, is_pre=is_pre
    )
    archive_path = f"{_OUTPUT_ARCHIVE_FILE_BASE}-{target_version}"
    _os = _get_local_platform()
    os_archive_path = f"{archive_path}-{_os}"
    base_tmp_path = f"tmp/{_os}/"
    assets = {}
    for py_version in _PYTHON_VERSIONS:
        py_major_minor = ".".join(py_version.split(".")[:-1])
        py_version_tmp_path = f"{base_tmp_path}{py_major_minor}"
        py_version_archive_path = os_archive_path + f"-{py_major_minor}"
        download_cmd = _generate_download_command_args(requirements_prefix=requirements_prefix, is_pre=is_pre)
        subprocess.run(
            ['sh',f"{_FILE_DIR}/download.sh", py_version_tmp_path, download_cmd, py_version], 
            check=True)
        subprocess.run(
            ['sh',f"{_FILE_DIR}/install.sh", _FILE_DIR, requirements_prefix, py_version_tmp_path, py_version], 
            check=True)
        shutil.make_archive(py_version_archive_path, 'zip', py_version_tmp_path)
        assets[f"snapshot_core_all_adapters_{_os}_{py_major_minor}.zip"] = py_version_archive_path + ".zip"
        subprocess.run(['sh',f"{_FILE_DIR}/freeze.sh", _SNAPSHOT_FILE, py_version], check=True)
        assets["snapshot_requirements"] = _SNAPSHOT_FILE
    return assets