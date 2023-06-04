#!/bin/bash
# Loads necessaries
set -e
source ./scripts/utils/prettyecho.sh

IMAGE_NAME=""
IMAGE_DOCKERFILE_SUBDIR=""
readonly IMAGE_TYPE=$1
readonly IMAGE_TAG=$2

if [[ $IMAGE_TYPE == "app" ]]; then
    IMAGE_NAME="bkdnoj-v2/backend"
    IMAGE_DOCKERFILE_SUBDIR="app"
elif [[ $IMAGE_TYPE == "migrate" ]]; then
    IMAGE_NAME="bkdnoj-v2/migrate"
    IMAGE_DOCKERFILE_SUBDIR="migrate"
else
    echo "FATAL: unrecognize image type '$IMAGE_TYPE'"
    exit 1
fi

if [[ $IMAGE_TAG == "" ]]; then
    echo "FATAL: empty image tag"
    exit 1
fi

docker build \
    --progress=plain \
    -f ./docker/$IMAGE_DOCKERFILE_SUBDIR/Dockerfile -t $IMAGE_NAME ./app