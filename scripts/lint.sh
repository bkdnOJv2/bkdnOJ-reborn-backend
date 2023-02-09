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

echo_cyan "LINT" "bkdnOJ.v2 $COMPO..."

pylint --output-format=colorized \
    --load-plugins pylint_django \
    --django-settings-module=bkdnoj.settings \
    $COMPO 

deactivate
