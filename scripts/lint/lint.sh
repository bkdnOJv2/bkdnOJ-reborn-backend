#!/bin/bash

CLNORMAL=$(tput sgr0)
CLCYAN=$(tput setaf 6)

component=$1
if [ component = "" ]; then
  component="app"
else
  component="app/$component"
fi

echo "${CLCYAN} * [ LINT ] Linting $component...${CLNORMAL}"

pylint --output-format=colorized \
  --django-settings-module=bkdnoj.settings \
  --load-plugins pylint_django \
  --ignore=migrations \
  --errors-only \
  $component 