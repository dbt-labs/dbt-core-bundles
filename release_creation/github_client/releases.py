import copy
import os
import requests
from typing import Dict, List, Optional, Set, Tuple
from semantic_version import Version
from github import Github
from github.GithubException import GithubException
from github.GitRelease import GitRelease
from github.GitReleaseAsset import GitReleaseAsset
from release_creation.bundle.create import BUNDLE_REQ_NAME_PREFIX
from release_creation.release_logger import get_logger

_GH_BUNDLE_REPO = "dbt-labs/dbt-core-bundles"
_GH_ACCESS_TOKEN = os.environ.get("GH_ACCESS_TOKEN")

logger = get_logger()


def get_github_client() -> Github:
    return Github(_GH_ACCESS_TOKEN)


def _normalize_version_tags(version: Version) -> Version:
    """Normalize the version tags:
    - if pre-release version use 'pre' instead of 'rc' or 'b1' for the tag
    - remove build tag
    """
    if version.prerelease or version.build:
        version.prerelease = ["pre"]
    if version.build:
        version.build = []
    return version


def _normalize_input_version(version: Version) -> Version:
    """Normalize the version:
    - set patch to 0
    """
    version = _normalize_version_tags(version)
    version.patch = 0
    return version


def get_latest_bundle_release(input_version: str) -> Tuple[ Version, Optional[GitRelease]]:
    """Retrieve the latest release matching the major.minor and release stage
       semantic version if it exists. Ignores the patch version. 

    Args:
        input_version (str): semantic version (1.0.0.0rc, 2.3.5) to match against 

    Returns:
        Tuple[ Version, Optional[GitRelease]]: A tuple of the latest release tag 
        and the latest release itself.
    """
    gh = get_github_client()
    target_version = Version.coerce(input_version)
    latest_version = copy.copy(target_version)
    latest_version = _normalize_input_version(latest_version)
    repo = gh.get_repo(_GH_BUNDLE_REPO)
    releases = repo.get_releases()
    latest_release = None
    for r in releases:
        release_version = Version.coerce(r.tag_name)
        if (
            release_version.major == latest_version.major
            and release_version.minor == latest_version.minor
            and (not release_version.prerelease) == (not latest_version.prerelease)
            and (not release_version.build) == (not latest_version.build)
            and release_version.patch >= latest_version.patch  # type: ignore
        ):
            latest_version = release_version
            latest_release = r
    return _normalize_version_tags(latest_version), latest_release


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


def generate_download_urls(release: GitRelease, bundle_config: BundleConfig) -> List[str]:
    created_asset_name = f"bundle_core_all_adapters_{bundle_config.local_os}_{bundle_config.py_major_minor}.zip"
    req_file_name = f"{BUNDLE_REQ_NAME_PREFIX}_{bundle_config.local_os}_{bundle_config.py_major_minor}.txt"

    for asset in release.get_assets():
        if asset.name == created_asset_name:
            created_asset_url = asset.browser_download_url
        if asset.name == req_file_name:
            req_file_url = asset.browser_download_url
    return created_asset_url, req_file_url 


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


def create_new_release_for_version(
    release_version: Version, assets: Dict, latest_release: GitRelease, draft: str
) -> GitRelease:
    """Given an input version it creates a matching Github Release and attaches the assets
       as a ReleaseAsset

    Args:
        release_version (Version): semantic version to be used when creating the release
        draft (str): if this is a draft release or not
        assets (Dict): assets to be added to the created release where a key is the asset name
        latest_release (GitRelease): supply if there is a prior release to be diffed against

    Raises:
        RuntimeError: _description_
        e: _description_
    """
    gh = get_github_client()
    release_tag = str(release_version)
    is_pre = True if release_version.prerelease else False
    is_draft = True if draft == "true" else False
    repo = gh.get_repo(_GH_BUNDLE_REPO)
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
    created_release = repo.create_git_release(tag=release_tag, name=release_name, message=release_body, prerelease=is_pre, draft=is_draft)

    try:
        for asset_name, asset_path in assets.items():
            created_release.upload_asset(path=asset_path, name=asset_name)
    except Exception as e:
        created_release.delete_release()
        raise e
    return created_release


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
