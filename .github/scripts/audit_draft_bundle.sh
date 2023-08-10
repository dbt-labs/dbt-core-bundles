#!/bin/bash -e
set -e

tag="$1"
echo $tag

draft_release=$(gh release view "${tag}" --json isDraft --jq .isDraft)
echo $draft_release

if [ -z "$draft_release" ]; then
  echo "Release with tag $tag does not exist."
  exit 1
fi

if [ "$draft_release" = "false" ]; then
  echo "Release with tag $tag is already published."
  exit 1
fi
