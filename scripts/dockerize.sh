#!/bin/bash
IMAGE_NAME="bkdnoj-v2/backend"

docker build \
    --progress=plain \
    -f ./docker/app/Dockerfile -t $IMAGE_NAME ./app 