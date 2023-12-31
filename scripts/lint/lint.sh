#!/bin/bash
# Loads necessaries
set -e # Exit on error

source ./scripts/utils/prettyecho.sh
source ./scripts/lint/setupenv.sh

VERBOSE=false
KEEP_CONTAINER=false
# Parse options
while getopts "v" opt; do
  case $opt in
    v)
      VERBOSE=true
      ;;
    d)
      KEEP_CONTAINER=true
      ;;
    \?)
      efatal "Lint" "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# Tearing down
spin_up
if [ $? -ne 0 ]; then
  efatal 0 "Lint" "Failed to spin up container."
  exit 1
fi

# Code
einfo 0 "Lint" "ERRORS ONLY MODE. Ignoring warnings and bad conventions.."

component=$1
if [ component = "" ]; then
  component="app"
else
  component="app/$component"
fi
einfo 1 "Lint" "Linting $component..."

docker exec -t $TMP_LINTER_NAME pylint --output-format=colorized \
    --django-settings-module=bkdnoj.settings \
    --load-plugins pylint_django \
    --ignore=migrations \
    --errors-only \
    $component 

# Tearing down
if [ "$KEEP_CONTAINER" = "false" ]; then
  einfo 0 "Lint" "Tearing down temporary container for lint..."
  tear_down
else
  einfo 0 "Lint" "Keeping container."
fi