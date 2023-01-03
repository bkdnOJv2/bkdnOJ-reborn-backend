#!/bin/bash
source ./scripts/prettyecho.sh
source ./venv/bin/activate

set -e

echo_cyan "LINT" "bkdnOJ.v2 ..."
pylint --output-format=colorized \
    --load-plugins pylint_django \
    --django-settings-module=bkdnoj.settings \
    app/

deactivate
