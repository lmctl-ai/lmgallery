#!/usr/bin/env bash
# Publish a green five-platform artifact set from a private workflow run.
set -euo pipefail

PRIVATE_REPO="${GITHUB_REPOSITORY:?private repo identity is required}"
PRODUCT="${PRIVATE_REPO##*/}"
TAG="${1:?usage: release-to-public.sh vMAJOR.MINOR.PATCH ARTIFACT_DIR}"
ARTIFACT_DIR="${2:?usage: release-to-public.sh vMAJOR.MINOR.PATCH ARTIFACT_DIR}"
PUBLIC_REPO="lmctl-ai/$PRODUCT"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/${PRODUCT}-publish-XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

case "$PRIVATE_REPO" in lmctlhq/*) ;; *) echo "refusing unexpected source repo: $PRIVATE_REPO" >&2; exit 2;; esac
[[ "$TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "refusing non-version tag: $TAG" >&2; exit 2; }
test -n "${GH_TOKEN:-}" || { echo "GH_TOKEN (RELEASE_TOKEN) is required" >&2; exit 2; }

mkdir -p "$WORK/release"
find "$ARTIFACT_DIR" -type f -name "$PRODUCT-*" -exec cp {} "$WORK/release/" \;
for asset in "$PRODUCT-linux-x64" "$PRODUCT-linux-arm64" "$PRODUCT-macos-arm64" "$PRODUCT-macos-x64" "$PRODUCT-windows-x64.exe"; do
  test -f "$WORK/release/$asset" || { echo "missing matrix asset: $asset" >&2; exit 1; }
done
gh repo clone "$PUBLIC_REPO" "$WORK/public"
cp "$WORK/public/LICENSE" "$WORK/release/LICENSE"
find "$WORK/public" -maxdepth 1 -type f -name 'THIRD_PARTY_NOTICES*' -exec cp {} "$WORK/release/" \;
chmod +x "$WORK/release/$PRODUCT-linux-x64"
actual="$("$WORK/release/$PRODUCT-linux-x64" --version)"
test "$actual" = "$PRODUCT ${TAG#v}" || { echo "tag $TAG does not match $actual" >&2; exit 1; }
(cd "$WORK/release" && sha256sum "$PRODUCT"-* > SHA256SUMS)

if gh release view "$TAG" -R "$PUBLIC_REPO" >/dev/null 2>&1; then
  echo "release $TAG already exists in $PUBLIC_REPO; refusing to overwrite" >&2
  exit 1
fi
gh release create "$TAG" -R "$PUBLIC_REPO" --target main --title "$TAG" --generate-notes "$WORK/release"/*
