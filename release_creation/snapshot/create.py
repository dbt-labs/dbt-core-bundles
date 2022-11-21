from typing import Dict, List, Optional, Tuple
from semantic_version import Version
import os
import subprocess
import shutil


_OUTPUT_ARCHIVE_FILE_BASE = "dbt-core-all-adapters-snapshot"
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
_SNAPSHOT_FILE = f"{_FILE_DIR}/snapshot.requirements.txt"


def _generate_download_command_args(major_version:Optional[int], minor_version:Optional[int], is_pre:bool = False) -> Tuple[List, str]:
    download_command = []
    suffix = "latest"
    if is_pre:
        download_command.append("--pre")
        suffix = "pre"
    requirements_prefix = f"v{major_version}.{minor_version}.{suffix}"
    download_command.append(f"-r {_FILE_DIR}/requirements/{requirements_prefix}.requirements.txt")
    return download_command, requirements_prefix


def generate_snapshot(target_version: Version) -> Dict[str, str]:
    is_pre = True if target_version.prerelease else False
    download_cmd, requirements_prefix = _generate_download_command_args(major_version=target_version.major, minor_version=target_version.minor, is_pre=is_pre)
    subprocess.run(['sh',f"{_FILE_DIR}/download.sh", *download_cmd], check=True)
    subprocess.run(['sh',f"{_FILE_DIR}/install.sh", _FILE_DIR, requirements_prefix], check=True)
    subprocess.run(['sh',f"{_FILE_DIR}/freeze.sh", _SNAPSHOT_FILE], check=True)
    archive_path = f"{_OUTPUT_ARCHIVE_FILE_BASE}-{str(target_version)}"
    shutil.make_archive(archive_path, 'zip', 'tmp')
    assets = {
        "snapshot_core_all_adapters": archive_path + ".zip",
         "snapshot_requirements": _SNAPSHOT_FILE
    }
    return assets