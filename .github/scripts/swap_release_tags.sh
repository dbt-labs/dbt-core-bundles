#!/bin/bash
#we don't want set -e because otherwise the script fails if the swap_to_release doesn't exist

swap_from_tag="$1"
swap_to_tag="$2"
swap_to_temp_tag="${swap_to_tag}.temp"

swap_from_release=$(gh release view "${swap_from_tag}") #0.0.0
swap_to_release=$(gh release view "${swap_to_tag}") #0.0.1

if [ -z "$swap_from_release" ]; then
  echo "Release with tag $swap_from_tag does not exist."
  exit 1
fi

if [ -z "$swap_to_release" ]; then
  gh release edit "${swap_from_tag}" --tag "${swap_to_tag}"
else
  gh release edit "${swap_to_tag}" --tag "${swap_to_temp_tag}"
  gh release edit "${swap_from_tag}" --tag "${swap_to_tag}"
  gh release edit "${swap_to_temp_tag}" --tag "${swap_from_tag}"
fi

