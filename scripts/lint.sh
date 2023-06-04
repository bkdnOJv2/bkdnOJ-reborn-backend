#!/bin/bash
# Loads necessaries
set -e # Exit on error
source ./scripts/utils/prettyecho.sh

# Code

component=$1
if [ component = "" ]; then
    component="app"
else
    component="app/$component"
fi

echo_cyan "LINTING" "ERRORS ONLY MODE. Ignoring warnings and bad conventions.."
echo_cyan "LINTING" "bkdnOJ.v2 $component..."

pylint --output-format=colorized \
    --django-settings-module=bkdnoj.settings \
    --load-plugins pylint_django \
    --ignore=migrations \
    --errors-only \
    $component 
