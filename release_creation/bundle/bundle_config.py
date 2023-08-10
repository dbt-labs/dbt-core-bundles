import os
import platform
from dataclasses import field
from typing import Optional

from pydantic.dataclasses import dataclass
from semantic_version import Version

from release_creation.bundle.bundle_os import BundleOS

_OUTPUT_ARCHIVE_FILE_BASE = "dbt-core-all-adapters-bundle"
_FILE_DIR = os.path.dirname(os.path.realpath(__file__))


def _get_requirements_prefix(major_version: Optional[int], minor_version: Optional[int], is_pre: bool = False):
    suffix = "pre" if is_pre else "latest"
    return f"v{major_version}.{minor_version}.{suffix}"


@dataclass
class BundleConfig:
    is_pre: bool
    file_dir: str
    requirements_prefix: str
    archive_path: str
    py_major_minor: Optional[str] = None
    requirements_file: Optional[str] = None
    py_version_tmp_path: Optional[str] = None
    py_version_archive_path: Optional[str] = None
    local_os: BundleOS = field(default_factory=BundleOS.get_local_os)
    py_version: str = field(default_factory=platform.python_version)

    def __post_init__(self):
        self.py_major_minor = ".".join(self.py_version.split(".")[:-1])
        self.requirements_file = f"{self.file_dir}/bundle.requirements.{self.py_major_minor}.txt"
        self.py_version_tmp_path = f"tmp/{self.local_os}/{self.py_major_minor}"
        self.py_version_archive_path = f"{self.archive_path}-{self.local_os}-{self.py_major_minor}"


def get_bundle_config(target_version: Version) -> BundleConfig:
    is_pre = True if target_version.prerelease else False
    req_prefix = _get_requirements_prefix(
        major_version=target_version.major,
        minor_version=target_version.minor,
        is_pre=is_pre
    )

    return BundleConfig(
        archive_path=f"{_OUTPUT_ARCHIVE_FILE_BASE}-{target_version}",
        requirements_prefix=req_prefix,
        is_pre=is_pre,
        file_dir=_FILE_DIR
    )
