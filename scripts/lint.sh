#!/bin/bash
source ./scripts/prettyecho.sh
source ./venv/bin/activate

set -e

component=$1
if [ component = "" ]; then
    component="app"
else
    component="app/$component"
fi

err_only=$2
if [ err_only != "--errors-only" ]; then
    err_only=""
fi

echo_cyan "LINTING" "bkdnOJ.v2 $component..."

pylint --output-format=colorized \
    --django-settings-module=bkdnoj.settings \
    --load-plugins pylint_django \
    --ignore=migrations \
    --errors-only \
    $component 

deactivate
