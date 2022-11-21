import os
import requests
from typing import Dict, List, Optional, Set, Tuple
from semantic_version import Version, match
from github import Github
from github.GitRelease import GitRelease
from github.GitReleaseAsset import GitReleaseAsset

_GH_SNAPSHOT_REPO = "dbt-labs/dbt-core-snapshots"
_GH_ACCESS_TOKEN = os.environ["GH_ACCESS_TOKEN"]
_SNAP_REQ_NAME = "snapshot_requirements"


def get_github_client() -> Github:
    return Github(_GH_ACCESS_TOKEN)


def get_latest_release(input_version:str) -> Tuple[Version, Optional[GitRelease]]:
    gh = get_github_client()
    target_version = Version(input_version)
    target_match = f"~{target_version.major}.{target_version.minor}"
    latest = Version(major=target_version.major, minor=target_version.minor, patch=0)
    repo = gh.get_repo(_GH_SNAPSHOT_REPO)
    releases = repo.get_releases()
    latest_release = None
    for r in releases:
        release_version = Version.coerce(r.tag_name)
        if match(target_match, r.tag_name) and release_version > latest:
            latest = release_version
            latest_release = r
    return latest, latest_release


def _get_local_snapshot_reqs(snapshot_req_path:str) -> List[str]:
    with open(snapshot_req_path) as f:
        reqs = f.read()
    return reqs.split()


def _get_gh_release_asset(release_asset: GitReleaseAsset) -> List[str]:
    resp = requests.get(release_asset.browser_download_url)
    resp.raise_for_status()
    return resp.content.decode("utf-8").split()


def _compare_reqs(snapshot_req: List[str], release_req: List[str]) -> Tuple[Set[str], Set[str]]:
    snapshot_req_set = set(snapshot_req)
    release_req_set = set(release_req)
    added_req = snapshot_req_set - release_req_set
    removed_req = release_req_set -  snapshot_req_set
    return added_req, removed_req


def _diff_snapshot_requirements(snapshot_req_path:str, latest_release: Optional[GitRelease]):
    # Scenarios being handled:
    # 1. No change - raise exception
    # 2. No prior patch version - Creat major.minor.0 snapshot
    # 3. New changes - generate diff
    diff_result = ""
    if latest_release:
        release_reqs = [_asset for _asset in latest_release.get_assets() if _SNAP_REQ_NAME in _asset.name]
        snapshot_req = _get_local_snapshot_reqs(snapshot_req_path=snapshot_req_path)
        release_req = _get_gh_release_asset(release_reqs[0])
        added, removed = _compare_reqs(snapshot_req=snapshot_req, release_req=release_req)
        if added:
            diff_result += "Added:\n* "+ "\n* ".join(added) + "\n___\n"
        if removed:
            diff_result += "\nRemoved:\n* " + "\n* ".join(removed) + "\n"
        if diff_result == "":
            raise Exception("New snapshot does not contain any new changes")
        return diff_result
    else:    
        return "No prior snapshot"
    

def create_new_release_for_version(release_version:Version, assets:Dict, latest_release: Optional[GitRelease], )->None:
    gh = get_github_client()
    release_tag = str(release_version)
    repo = gh.get_repo(_GH_SNAPSHOT_REPO)
    release_body = _diff_snapshot_requirements(assets[_SNAP_REQ_NAME], latest_release=latest_release)
    created_release = repo.create_git_release(tag=release_tag, name='Snapshot Release', message=release_body)
    try:
        for asset_name, asset_path in assets.items():
            created_release.upload_asset(path=asset_path, name=asset_name)
    except Exception as e:
        created_release.delete_release()
        raise e