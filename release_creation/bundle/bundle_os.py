import platform

from strenum import StrEnum


class BundleOS(StrEnum):
    LINUX = "linux"
    MAC = "mac"
    WINDOWS = "windows"

    @classmethod
    def get_local_os(cls) -> str:
        local_sys = platform.system()
        if local_sys == "Linux":
            return BundleOS.LINUX
        elif local_sys == "Windows":
            return BundleOS.WINDOWS
        elif local_sys == "Darwin":
            return BundleOS.MAC
        else:
            raise ValueError(f"Unsupported system {local_sys}")


# these values have been derived by trial and error, as to date
# there isn't an authoritative source, see:
# https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/
PIP_PLATFORM_OS_VALUES = {
    BundleOS.MAC: ['macosx_10_9_x86_64', 'macosx_11_0_arm64', 'macosx_12_0_arm64'],
    BundleOS.LINUX: ['manylinux_2_17_x86_64', 'manylinux2014_x86_64',
                     'manylinux_2_17_aarch64', 'manylinux2014_aarch64']
}
