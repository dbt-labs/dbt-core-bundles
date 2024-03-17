import sys
import platform

import pytest
from semantic_version import Version

from release_creation.github_client.get_release import get_latest_bundle_release


@pytest.mark.parametrize("version", ["1.2.0b1", "1.4.0pre", "1.2.0", "1.3.0a1"])
def test_get_latest_bundle_release_gets_latest_release(version):
    if platform.system() == "Darwin" and sys.version_info <= (3, 11):
        pytest.skip("Only test for Python 3.11 on macOS")
    if platform.system() == "Linux" and sys.version_info not in [(3, 8), (3.11)]:
        pytest.skip("Only test for Python 3.8 and 3.11 on Linux")
    input_version = Version.coerce(version)
    latest_version, is_draft, latest_release = get_latest_bundle_release(str(input_version))
    assert (not input_version.prerelease) == (not latest_version.prerelease)
    assert (not input_version.build) == (not latest_version.build)
    assert latest_version.patch >= input_version.patch
