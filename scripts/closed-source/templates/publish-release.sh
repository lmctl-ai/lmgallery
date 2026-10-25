#!/usr/bin/env bash
# Manual publisher for a green full-matrix lmaudio Actions run.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${GITHUB_REPOSITORY:-lmctlhq/lmaudio}"
RUN_ID="${1:?usage: scripts/publish-release.sh RUN_ID TAG}"
TAG="${2:?usage: scripts/publish-release.sh RUN_ID TAG}"
PUBLIC_REPO="lmctl-ai/lmaudio"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/lmaudio-publish-XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

case "$REPO" in lmctlhq/lmaudio) ;; *) echo "refusing unexpected source repository: $REPO" >&2; exit 2;; esac
case "$TAG" in v[0-9]*.[0-9]*.[0-9]*) ;; *) echo "refusing non-version tag: $TAG" >&2; exit 2;; esac

conclusion="$(gh run view "$RUN_ID" -R "$REPO" --json status,conclusion --jq '.conclusion')"
[ "$conclusion" = success ] || { echo "source run $RUN_ID is not green ($conclusion)" >&2; exit 1; }

gh run download "$RUN_ID" -R "$REPO" --pattern 'lmaudio-*' --dir "$WORK/artifacts"
gh repo clone "$PUBLIC_REPO" "$WORK/public"
mkdir -p "$WORK/release"
find "$WORK/artifacts" -type f -name 'lmaudio-*' -exec cp {} "$WORK/release/" \;
for asset in lmaudio-linux-x64 lmaudio-linux-arm64 lmaudio-macos-arm64 lmaudio-macos-x64 lmaudio-windows-x64.exe; do
  test -f "$WORK/release/$asset"
done
cp "$WORK/public/LICENSE-binaries" "$WORK/release/LICENSE"
cp "$WORK/public/THIRD_PARTY_NOTICES" "$WORK/release/THIRD_PARTY_NOTICES"
(cd "$WORK/release" && sha256sum lmaudio-* > SHA256SUMS)

gh release create "$TAG" -R "$PUBLIC_REPO" --target main --title "$TAG" --generate-notes "$WORK/release"/*
