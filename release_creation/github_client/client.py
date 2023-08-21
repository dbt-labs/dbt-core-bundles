import os

from github import Github
from github.Repository import Repository
from urllib3 import Retry

_GH_BUNDLE_REPO = "dbt-labs/dbt-core-bundles"
_RETRY = Retry(total=5, backoff_factor=0.2)

def get_github_client() -> Github:
    return Github(os.environ.get("GH_ACCESS_TOKEN"), retry=_RETRY)


def get_bundle_repo() -> Repository:
    gh = get_github_client()
    return gh.get_repo(_GH_BUNDLE_REPO)
