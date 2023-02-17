# bkdnOJ.v2 Refactoring
Restructuring into directories:
- `app/`: Contains bkdnOJ backend application.
- `scripts/`: Contains scripts, some are used to automate execution
- `docker/`: Contains Dockerfiles
- ... to be updated

## Refactor checklist:
1. Refactor code by following Pylint (django plugin):
- DONE: `auth`, `bkdnoj`
- ON-HOLD: `compete`
- NOT DONE: `helpers`, `judgers`, `organization`, `problem`, `submission`, `userprofile`

2. Containerize application
- ON-GOING

3. Unittest
- NOT DONE
- Should be done before Task 1 but oh well.

## Priority
- Need to prioritize Containerize, then deploy an AI service for `hungphan` to test their source code labelling model.
