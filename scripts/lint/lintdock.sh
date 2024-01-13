#!/bin/bash
# Loads necessaries
set -e # Exit on error

source ./scripts/utils/prettyecho.sh

source ./scripts/lint/setupenv.sh
# Defines
# # $TMP_LINTER_NAME
# # $TMP_LINTER_IMAGE_NAME
# # $CONTAINER_WORKDIR


VERBOSE=false
KEEP_CONTAINER=false
LINT_TARGET=""
# Parse options
while getopts "vdt" opt; do
  case $opt in
    v)
      VERBOSE=true
      ;;
    d)
      KEEP_CONTAINER=true
      ;;
    t)
      LINT_TARGET=$OPTARG
      ;;
    \?)
      efatal "Lint" "Invalid option: -$OPTARG" >&2
      einfo "Usage $0 [-v] [-d]"
      echo "  -v: To enable verbose"
      echo "  -d: To keep container after linting"
      exit 1
      ;;
  esac
done

einfo 0 "LINT OPTIONS" "VERBOSE=$VERBOSE, KEEP_CONTAINER=$KEEP_CONTAINER, LINT_TARGET='$LINT_TARGET'"

# Tearing down
spin_up
if [ $? -ne 0 ]; then
  efatal 0 "Lint" "Failed to spin up container."
  exit 1
fi

# Code
einfo 0 "Lint" "ERRORS ONLY MODE. Ignoring warnings and bad conventions.."

docker exec -t $TMP_LINTER_NAME bash $CONTAINER_WORKDIR/scripts/lint/lint.sh $LINT_TARGET

# Tearing down
if [ "$KEEP_CONTAINER" = "false" ]; then
  einfo 0 "Lint" "Tearing down temporary container for lint..."
  tear_down
else
  einfo 0 "Lint" "Keeping container."
fi