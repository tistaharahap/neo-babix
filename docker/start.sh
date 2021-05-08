#!/bin/bash -e
source "$( poetry env list --full-path )/bin/activate"
case $1 in
  "run")
    shift
    python -u app.py
    ;;
  *)
    echo "usage: $0 [run]"
    exit 1
    ;;
esac