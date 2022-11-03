from sqlite3 import adapters
import subprocess
import os
import shutil
from typing import Optional
from semantic_version import Version

_BASE_DOWNLOAD_CMD = """pip3 download --dest ./tmp """
_OUTPUT_ARCHIVE_FILE_BASE = "dbt-core-all-adapters-snapshot"
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))

# def _generate_package_req(version: dict):
#     suffix = version['suffix'] if 'suffix' in version else ''
#     return f"{version['name']}{version['version_pinning']}{version['sem_ver']} {suffix} \\\n"

def _generate_download_command(major_version:Optional[int], minor_version:Optional[int], is_pre:bool = False) -> str:
    download_command = _BASE_DOWNLOAD_CMD
    suffix = "latest"
    if is_pre:
        download_command += "--pre"
        suffix = "pre"
    download_command += f" -r {_FILE_DIR}/requirements/v{major_version}.{minor_version}.{suffix}.requirements.txt"
    return download_command

def generate_snapshot(target_version: Version) -> str:
    is_pre = True if target_version.prerelease else False
    download_cmd = _generate_download_command(major_version=target_version.major, minor_version=target_version.minor, is_pre=is_pre)
    print(download_cmd)
    subprocess.run("python -m pip install --upgrade pip", shell=True, check=True)
    subprocess.run("rm -r tmp", shell=True, check=True)
    subprocess.run("mkdir tmp", shell=True, check=True)
    subprocess.run(download_cmd, shell=True, check=True)
    subprocess.run(['sh',f"./release_creation/install.sh"], check=True)
    archive_path = f"{_OUTPUT_ARCHIVE_FILE_BASE}-{str(target_version)}"
    shutil.make_archive(archive_path, 'zip', "tmp")
    return archive_path + ".zip"