#!/usr/bin/env bash
# health.sh: Cross-repository health dashboard wrapper for lmctl-ai
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$HERE/health.py" "$@"
