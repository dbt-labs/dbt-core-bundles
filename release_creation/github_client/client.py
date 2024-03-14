import os, base64

from github import Github
from github.Repository import Repository
from urllib3 import Retry
from requests import request

_GH_BUNDLE_REPO = "dbt-labs/dbt-core-bundles"
_RETRY = Retry(total=5, backoff_factor=0.2)


def get_github_client() -> Github:
    return Github(os.environ.get("GH_ACCESS_TOKEN"), retry=_RETRY)


def get_bundle_repo() -> Repository:
    gh = get_github_client()
    return gh.get_repo(_GH_BUNDLE_REPO)


def update_file(repo: Repository, path: str, message: str, branch: str, content: str, sha: str):
    """
    Note: this requires a PAT with repo scope be set in the GH_ACCESS_TOKEN env var

    Args:
        repo:
        path:
        message:
        branch:
        content:
        sha:

    Returns: Status code of the request

    """
    url = f"https://api.github.com/repos/{repo.full_name}/contents/{path}?ref={branch}"
    body = {
        "message": message,
        "branch": branch,
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha,
    }

    response = request(
        method="PUT",
        url=url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ.get('GH_ACCESS_TOKEN')}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json=body,
    )
    return response.raise_for_status()
