# dbt Bundles (beta)
*NOTE*: this is still under active development please use with caution.
## Overview
Generate bundles (zip archives) of all python dependencies needed to install and run the verified adapters + core as GitHub releases. 

### Why? 
Python makes it difficult to create a shippable dependency enclosure that insures predictability at both install and run time. 

These bundles attempt to solve for two issues:
1. An update to a dependency contains breaking changes so dbt fails at runtime.
2. An update to a dependency creates a version conflict so dbt cannot be installed. 

### How does it work?
Every week we will release a new bundle that will include all of the changes from the prior week including changes to
dependencies for each supported major.minor version of dbt as a GitHub release. The release tag corresponds to the 
major.minor version of dbt it's for so `1.3.45` release includes the latest patches for all dbt packages that are `~=1.3.0`.

Every week day we will update a dev bundle that will install dbt-* packages off of main instead of pypi. This will allow
us to test and develop against the latest changes in Core. The release tag for this bundle will _always_ be `0.0.1`.

Note that the patch version *will not* match the patch version for dbt-core or any other package as it will increment 
with a change to any of the included python packages.  

#### EOL Packages
For dbt packages that have reached end-of-life we will be installing from the git repo instead of pypi. This will allow
us to incorporate any security patches that are released after we have stopped updating the package on pypi.

## How to use
To use a bundle you will need to download, unzip the archive and pass the resulting directory to pip.
You can use the [install_bundle.sh](/install_bundle.sh) to do this for you by running the following: 
```
curl -s https://raw.githubusercontent.com/dbt-labs/dbt-core-snapshots/main/install_bundle.sh | bash -s -- 1.4.5 3.9 mac
```
Where `1.4.5` is the bundle, `3.9` is the python version and `mac` is the platform. 

## Contributing and Maintaining
### Changing the GHA Workflow
You can test updates to the workflow on your feature branch by calling:
`gh workflow run release_bundle.yml -f version_number=1.3.0 --ref YOUR_BRANCH`

### Supporting new major.minor versions of dbt
* Update the [scheduled_releases.yml](/.github/workflows/scheduled_releases.yml) `version` matrix.
* Add the new version to the `argvalues` in [test_create.py](test/integration/bundle/test_create.py)