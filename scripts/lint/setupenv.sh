#!/bin/bash

source ./scripts/utils/prettyecho.sh

TMP_LINTER_NAME="bkdnoj-lint-tmp"
TMP_LINTER_IMAGE_NAME="bkdnoj-lint-image:local"
CONTAINER_WORKDIR="/usr/app"

spin_up() {
  set +e

  echo ""
  einfo 1 "Lint | Setup" "Spinning up temporary container for lint..."

  # Check if container is already running
  einfo 2 "Lint | Setup" "Checking if container is already running..."

  local msg=$(docker inspect $TMP_LINTER_NAME 2> /dev/null);
  if [ "$msg" != "[]" ]; then
    ewarn 2 "Lint | Setup" "Container is already running. Skipping..."
    return 0
  else
    einfo 2 "Lint | Setup" "Container is not running."
  fi

  # Container is not up, spin up a new one
  einfo 2 "Lint | Setup" "Building image..."
  docker build -t $TMP_LINTER_IMAGE_NAME -f ./scripts/lint/Dockerfile .

  einfo 2 "Lint | Setup" "Running container in the background..."
  docker run -t -d --name $TMP_LINTER_NAME -v ".:$CONTAINER_WORKDIR" -w $CONTAINER_WORKDIR \
    $TMP_LINTER_IMAGE_NAME bash

  esucceed 2 "Lint | Setup" "Container is ready."

  echo ""
  set -e
}

tear_down() {
  echo ""
  einfo 1 "Lint" "Tearing down temporary container for lint..."
  docker rm -f $TMP_LINTER_NAME
  echo ""
}
