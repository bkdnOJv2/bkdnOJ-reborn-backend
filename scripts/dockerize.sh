#!/bin/bash
# Loads necessaries
set -e
source ./scripts/utils/prettyecho.sh

IMAGE_NAME=""
IMAGE_DOCKERFILE_SUBDIR=""

readonly IMAGE_TYPE=$1
readonly IMAGE_TAG=$2
readonly PUSH_TO_REMOTE=$3

if [[ $IMAGE_TYPE == "app" ]]; then
    IMAGE_REPOSITORY="$DOCKER_USERNAME/bkdnoj-v2_api"
    IMAGE_DOCKERFILE_SUBDIR="app"
elif [[ $IMAGE_TYPE == "migrate" ]]; then
    IMAGE_REPOSITORY="$DOCKER_USERNAME/bkdnoj-v2_db-migrate"
    IMAGE_DOCKERFILE_SUBDIR="migrate"
else
    echo "FATAL: unrecognize image type '$IMAGE_TYPE'"
    exit 1
fi

if [[ $IMAGE_TAG == "" ]]; then
    echo "FATAL: empty image tag"
    exit 1
fi

echo "Building: docker build -f ./docker/$IMAGE_DOCKERFILE_SUBDIR/Dockerfile -t ${IMAGE_REPOSITORY}:${IMAGE_TAG} ./app" 
# docker build \
#     --progress=plain \
#     -f ./docker/$IMAGE_DOCKERFILE_SUBDIR/Dockerfile -t ${IMAGE_REPOSITORY}:${IMAGE_TAG} ./app

if [[ $PUSH_TO_REMOTE == "push" ]]; then
    echo "Pushing to ${IMAGE_REPOSITORY}:${IMAGE_TAG}"
    # docker push ${IMAGE_REPOSITORY}:${IMAGE_TAG}
fi