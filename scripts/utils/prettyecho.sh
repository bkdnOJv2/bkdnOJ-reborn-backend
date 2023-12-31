#!/bin/bash

source ./scripts/utils/colors.sh

ecolor() {
  # Check for VERBOSE env var
  if [ "$VERBOSE" = "false" ]; then
    return 0
  fi

  local color=$1
  local depth=$2
  local headmsg=$3
  local mainmsg=$4

  if [[ -z "$color" || -z "$depth" || -z "$headmsg" || -z "$mainmsg" ]]; then
    echo "Usage: ecolor <color> <depth> <headmsg> <mainmsg>"
    echo "   - <color> refers to the color of the head message. Check ./scripts/utils/colors.sh"
    echo "   - <depth> indent the message by <depth> spaces, must be a number."
    echo "   - <headmsg> is message to be wrapped in [HEADMSG]"
    echo "   - <mainmsg> is message after [HEADMSG]"
    return 1
  fi

  if [[ ! $depth =~ ^[0-9]+$ ]]; then
    echo "Usage: ecolor <color> <depth> <headmsg> <mainmsg>"
    echo "   - error: depth must be a number"
    return 1
  fi

  local indent="${color}＊$(printf "%${depth}s" | tr ' ' '-')"
  echo -e "${indent}[${headmsg}]${CLNORMAL} ${mainmsg}"
  return 0
}

efatal() {
  ecolor "$CLRED" "$1" "$2" "$3"
}

ewarn() {
  ecolor "$CLYELLOW" "$1" "$2" "$3"
}

esucceed() {
  ecolor "$CLGREEN" "$1" "$2" "$3"
}

einfo() {
  ecolor "$CLCYAN" "$1" "$2" "$3"
}

edebug() {
  ecolor "$CLBLUE" "$1" "$2" "$3"
}