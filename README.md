# dbt-core-snapshots
Generates bundles of verified adapters + core

###Changing the GHA Workflow
You can test updates to the workflow on your feature branch by calling:
`gh workflow run release_snapshot.yml -f version_number=1.3.0 --ref YOUR_BRANCH`