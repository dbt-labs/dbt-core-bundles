import strenum as strenum


class BundleOS(strenum):
    LINUX = "linux"
    MAC = "mac"
    WINDOWS = "windows"


# these values have been derived by trial and error, as to date
# there isn't an authoritative source, see:
# https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/
PIP_PLATFORM_OS_VALUES = {
    BundleOS.MAC: ['macosx_10_9_x86_64', 'macosx_11_0_arm64', 'macosx_10_10_intel', 'macosx_12_0_arm64'],
    BundleOS.LINUX: ['manylinux_2_17_x86_64', 'manylinux2014_x86_64', 'manylinux2014_i686']
}
