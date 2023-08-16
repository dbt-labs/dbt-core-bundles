#!/bin/bash -e
set -e

swap_from_tag="$1"
swap_to_tag="$2"

swap_from_release=$(gh release view "${swap_from_tag}") #0.0.0
swap_to_release=$(gh release view "${swap_to_tag}") #0.0.1
swap_to_release_temp="${swap_to_release}.temp"

if [ -z "$swap_from_release" ]; then
  echo "Release with tag $swap_from_tag does not exist."
  exit 1
fi

if [ -z "$swap_to_release" ]; then
  echo "Release with tag $swap_to_tag does not exist."
  exit 1
fi

gh release edit "${swap_to_release}" --tag "${swap_to_release_temp}"
gh release edit "${swap_from_release}" --tag "${swap_to_release}"
gh release edit "${swap_to_release_temp}" --tag "${swap_from_release}"