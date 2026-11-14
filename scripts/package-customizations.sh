#!/usr/bin/env bash
# Packages customizations from this machine into a tarball for Docker COPY.
# Usage: scripts/package-customizations.sh [output_dir]
set -euo pipefail

OUTPUT_DIR="${1:-customizations}"
mkdir -p "$OUTPUT_DIR"

echo "=== Packaging Nanobot Customizations ==="

# --- 1. Venv site-packages patches ---
# These are files modified after package install (not tracked by git).
# We capture them so they survive Docker rebuild.
PATCHES_DIR="$OUTPUT_DIR/site-packages-patches"
mkdir -p "$PATCHES_DIR"

# Find Python files newer than the package marker
MARKER="$(pwd)/nanobot/__init__.py"
find "$(pwd)/venv/lib/python3.12/site-packages/nanobot/" \
    -name "*.py" -newer "$MARKER" 2>/dev/null | while read -r f; do
    VENV_BASE="$(pwd)/venv/lib/python3.12/site-packages"
    rel="${f#$VENV_BASE/}"
    dest="$PATCHES_DIR/$rel"
    mkdir -p "$(dirname "$dest")"
    cp "$f" "$dest"
    echo "  Patched: $rel"
done

if [ ! "$(ls -A "$PATCHES_DIR" 2>/dev/null)" ]; then
    echo "  No site-packages patches found."
fi

# --- 2. Config ---
cp ~/.nanobot/config.json "$OUTPUT_DIR/config.json" 2>/dev/null || true
echo "  Config: config.json"

# --- 3. Workspace files ---
cp ~/.nanobot/workspace/AGENTS.md "$OUTPUT_DIR/" 2>/dev/null || true
cp ~/.nanobot/workspace/SOUL.md "$OUTPUT_DIR/" 2>/dev/null || true
cp ~/.nanobot/workspace/USER.md "$OUTPUT_DIR/" 2>/dev/null || true
cp ~/.nanobot/workspace/HEARTBEAT.md "$OUTPUT_DIR/" 2>/dev/null || true

# --- 4. Custom skills ---
SKILLS_DIR="$OUTPUT_DIR/workspace/skills"
mkdir -p "$SKILLS_DIR"
for skill in ~/.nanobot/workspace/skills/*/; do
    name=$(basename "$skill")
    if [ -f "$skill/SKILL.md" ]; then
        cp -r "$skill" "$SKILLS_DIR/"
        echo "  Skill: $name"
    fi
done

# --- 5. Custom plugins ---
PLUGINS_DIR="$OUTPUT_DIR/workspace/plugins"
mkdir -p "$PLUGINS_DIR"
for plugin in ~/.nanobot/workspace/plugins/*/; do
    name=$(basename "$plugin")
    if [ -d "$plugin" ]; then
        cp -r "$plugin" "$PLUGINS_DIR/"
        echo "  Plugin: $name"
    fi
done

# --- 6. .pgpass (DB credentials) ---
cp ~/.pgpass "$OUTPUT_DIR/.pgpass" 2>/dev/null && \
    chmod 600 "$OUTPUT_DIR/.pgpass" || true
echo "  DB auth: .pgpass"

echo ""
echo "Packaged into: $OUTPUT_DIR/"
ls -la "$OUTPUT_DIR/"
