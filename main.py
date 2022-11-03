import os

from release_creation.github import create_new_release_for_version, get_next_release_version
from release_creation.snapshots import generate_snapshot


def main():
    version = os.environ['INPUT_VERSION'] #1.3.4
    target_version = get_next_release_version(version) #1.3.6
    snapshot_path = generate_snapshot(target_version)
    create_new_release_for_version(target_version, snapshot_path)

if __name__ == "__main__":
    main()