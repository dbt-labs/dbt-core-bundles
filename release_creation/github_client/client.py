import os

from github import Github
from github.Repository import Repository

_GH_BUNDLE_REPO = "dbt-labs/dbt-core-bundles"


def get_github_client() -> Github:
    return Github(os.environ.get("GH_ACCESS_TOKEN"))


def get_bundle_repo() -> Repository:
    gh = get_github_client()
    return gh.get_repo(_GH_BUNDLE_REPO)
