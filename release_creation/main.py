import os

from github_client.releases import create_new_release_for_version, get_latest_release
from snapshot.create import generate_snapshot

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def main():
    version = os.environ['INPUT_VERSION'] #e.g. v1.3.4
    latest_version, latest_release = get_latest_release(version)
    target_version = latest_version.next_patch()
    snapshot_assets = generate_snapshot(target_version)
    create_new_release_for_version(target_version, snapshot_assets, latest_release)

if __name__ == "__main__":
    main()