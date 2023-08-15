import requests
from typing import Dict, List, Optional, Set, Tuple
from semantic_version import Version
from github.GithubException import GithubException, UnknownObjectException
from github.GitRelease import GitRelease
from github.GitReleaseAsset import GitReleaseAsset
from release_creation.bundle.create import BUNDLE_REQ_NAME_PREFIX
from release_creation.github_client import client
from release_creation.release_logger import get_logger

_GH_BUNDLE_REPO = "dbt-labs/dbt-core-bundles"

logger = get_logger()


def _get_local_bundle_reqs(bundle_req_path: str) -> List[str]:
    with open(bundle_req_path) as f:
        reqs = f.read()
    return reqs.split()


def _get_gh_release_asset(release_asset: GitReleaseAsset) -> List[str]:
    resp = requests.get(release_asset.browser_download_url)
    resp.raise_for_status()
    return resp.content.decode("utf-8").split()


def _compare_reqs(bundle_req: List[str], release_req: List[str]) -> Tuple[Set[str], Set[str]]:
    bundle_req_set = set(bundle_req)
    release_req_set = set(release_req)
    added_req = bundle_req_set - release_req_set
    removed_req = release_req_set - bundle_req_set
    return added_req, removed_req


def _diff_bundle_requirements(
    bundle_req_path: str, latest_release: Optional[GitRelease]
) -> str:
    # Scenarios being handled:
    # 1. No change - raise exception
    # 2. No prior patch version - Create major.minor.0 bundle
    # 3. New changes - generate diff
    if latest_release:
        logger.info(f"Comparing bundle requirements with {latest_release.tag_name}")
        diff_result = ""
        release_reqs = [
            _asset for _asset in latest_release.get_assets() if BUNDLE_REQ_NAME_PREFIX in _asset.name
        ]
        bundle_req = _get_local_bundle_reqs(bundle_req_path=bundle_req_path)
        release_req = _get_gh_release_asset(release_reqs[0])
        added, removed = _compare_reqs(bundle_req=bundle_req, release_req=release_req)
        if added:
            diff_result += "Added:\n* " + "\n* ".join(added) + "\n___\n"
        if removed:
            diff_result += "\nRemoved:\n* " + "\n* ".join(removed) + "\n"
        return diff_result
    else:
        return "No prior bundle"


def create_new_draft_release_for_version(
    release_version: Version, assets: Dict, latest_release: GitRelease
) -> None:
    """Given an input version it creates a matching Github Release and attaches the assets
       as a ReleaseAsset

    Args:
        release_version (Version): semantic version to be used when creating the release
        assets (Dict): assets to be added to the created release where a key is the asset name
        latest_release (GitRelease): supply if there is a prior release to be diffed against

    Raises:
        RuntimeError: _description_
        e: _description_
    """
    release_tag = str(release_version)
    is_pre = True if release_version.prerelease else False
    repo = client.get_bundle_repo()
    logger.info(f"Assets for release: {assets.keys()}")
    reqs_files = [x for x in assets if BUNDLE_REQ_NAME_PREFIX in x]
    release_name = f"Bundle for dbt v{release_version.major}.{release_version.minor}"
    if is_pre:
        release_name += f".{release_version.prerelease[0]}"
    release_body = _diff_bundle_requirements(
        assets[reqs_files[0]], latest_release=latest_release
    )

    if not release_body:
        raise RuntimeError("New bundle does not contain any new changes")
    created_release = repo.create_git_release(tag=release_tag, name=release_name, message=release_body, prerelease=is_pre, draft=True)

    try:
        add_assets_to_release(assets=assets, latest_release=created_release)
    except Exception as e:
        created_release.delete_release()
        raise e


def add_assets_to_release(assets: Dict, latest_release: Optional[GitRelease]) -> None:
    if not latest_release:
        raise ValueError("Cannot update that which doth not exist!")
    for asset_name, asset_path in assets.items():
        try:
            latest_release.upload_asset(path=asset_path, name=asset_name)
        except GithubException as e:
            if e.status == 422:
                logger.warning("Asset already exists!")
            else:
                raise e


def create_dev_release(release_version: Version, assets: Dict,) -> None:
    repo = client.get_bundle_repo()
    release_tag = str(release_version)
    try:
        latest_release = repo.get_release(release_tag)
        latest_release.delete_release()
    except UnknownObjectException:
        pass
    latest_release = repo.create_git_release(
        tag=release_tag,
        name=f"dev Bundle for dbt",
        message="This is a dev bundle release. It is meant for testing the latest changes in dbt-* packages.",
        prerelease=True,
        draft=False,
    )
    add_assets_to_release(assets=assets, latest_release=latest_release)
