#!/bin/bash

IMAGE_REPOSITORY="nvat/bkdnoj-v2-api"
readonly IMAGE_TAG="$1"
readonly PUSH_IMAGE="$2"

docker build \
    --progress=plain \
    --tag "$IMAGE_REPOSITORY":"$IMAGE_TAG" \
    -f ./docker/app/Dockerfile -t $IMAGE_REPOSITORY ./app 

if [ "$PUSH_IMAGE" == "push" ]; then
    docker push "$IMAGE_REPOSITORY":"$IMAGE_TAG"
fi