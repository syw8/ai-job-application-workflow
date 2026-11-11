#!/usr/bin/env sh
set -eu

python3 scripts/privacy_scan.py .
python3 scripts/validate_project.py .
python3 -m unittest discover -s tests -v
