import os
from semantic_version import Version, match
from github import Github

_GH_SNAPSHOT_REPO = "dbt-labs/dbt-core-snapshots"
_GH_ACCESS_TOKEN = os.environ["GH_ACCESS_TOKEN"]


def get_github_client() -> Github:
    return Github(_GH_ACCESS_TOKEN)


def get_next_release_version(input_version:str) -> Version:
    gh = get_github_client()
    target_version = Version(input_version)
    target_match = f"~{target_version.major}.{target_version.minor}"
    latest = Version(major=target_version.major, minor=target_version.minor, patch=0)
    repo = gh.get_repo(_GH_SNAPSHOT_REPO)
    releases = repo.get_releases()
    for r in releases:
        release_version = Version.coerce(r.tag_name)
        if match(target_match, r.tag_name) and release_version > latest:
            latest = release_version
    return latest.next_patch()


def create_new_release_for_version(release_version:Version, asset_url)->None:
    gh = get_github_client()
    release_tag = str(release_version)
    repo = gh.get_repo(_GH_SNAPSHOT_REPO)
    created_release = repo.create_git_release(tag=release_tag, name=f'Snapshot Release', message='')
    try:
        created_release.upload_asset(path=asset_url, name=f"snapshot_core_all_adapters")
    except:
        created_release.delete_release()