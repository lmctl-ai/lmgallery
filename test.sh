#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
network=()
mode=""
for arg in "$@"; do
  case "$arg" in
    --network) network=(--network) ;;
    --run) mode=local ;;
    --urls) mode=urls ;;
    *) echo "usage: ./test.sh [--network] [--run|--urls]" >&2; exit 2 ;;
  esac
done
python3 scripts/build-readme.py --check
python3 tests/check_gallery.py "${network[@]}"
if [[ "$mode" == urls ]]; then
  python3 scripts/run-examples.py --urls
elif [[ "$mode" == local ]]; then
  python3 scripts/run-examples.py
else
  echo 'SKIP: executable examples; run ./test.sh --run or --urls (requires lmctl and released hosts)'
fi

