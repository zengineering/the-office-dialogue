#!/usr/bin/env bash

SCRIPT_PATH=$(dirname "$(readlink -f "$0")")

PYTHONPATH=$SCRIPT_PATH:$PYTHONPATH python -m officequotes $@
