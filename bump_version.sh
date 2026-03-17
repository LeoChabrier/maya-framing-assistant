#!/usr/bin/env bash
# Bump the patch version, create a git tag, and push it.
# Usage: bash bump_version.sh [major|minor|patch]
#   Defaults to "patch" if no argument is given.

set -euo pipefail

BUMP_TYPE="${1:-patch}"

# Get latest tag
latest=$(git tag --sort=-v:refname | head -n 1)
if [ -z "$latest" ]; then
    latest="v0.0.0"
fi

# Strip leading 'v'
version="${latest#v}"
IFS='.' read -r major minor patch <<< "$version"

case "$BUMP_TYPE" in
    major)
        major=$((major + 1))
        minor=0
        patch=0
        ;;
    minor)
        minor=$((minor + 1))
        patch=0
        ;;
    patch)
        patch=$((patch + 1))
        ;;
    *)
        echo "Usage: $0 [major|minor|patch]"
        exit 1
        ;;
esac

new_tag="v${major}.${minor}.${patch}"

echo "Previous tag: ${latest}"
echo "New tag:      ${new_tag}"

# Prompt for tag message
read -rp "Tag message (leave empty for default): " tag_message
if [ -z "$tag_message" ]; then
    tag_message="Release ${new_tag}"
fi

git tag -a "$new_tag" -m "$tag_message"
git push origin "$new_tag"

echo "Tag ${new_tag} created and pushed."
