#!/bin/bash
source ./scripts/prettyecho.sh
source ./venv/bin/activate

set -e

COMPO=$1
if [ COMPO = "" ]; then
    COMPO="app"
else
    COMPO="app/$COMPO"
fi

ERRONLY=$2
if [ ERRONLY != "--errors-only" ]; then
    ERRONLY=""
fi

echo_cyan "LINT" "bkdnOJ.v2 $COMPO..."

pylint --output-format=colorized \
    --django-settings-module=bkdnoj.settings \
    --load-plugins pylint_django \
    --ignore=migrations \
    --errors-only \
    $COMPO 

deactivate
