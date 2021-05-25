#!/bin/bash -e

case $1 in
  "run")
    shift
    python3 -u app.py
    ;;
  *)
    echo "usage: $0 [run]"
    exit 1
    ;;
esac