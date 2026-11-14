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

# Strip all API keys / tokens / secrets from the packaged config.
# Values in any field whose name contains key/token/secret (case-
# insensitive) are blanked. Secrets stay in the live ~/.nanobot/config.json
# and get injected per-instance via external volumes / nanobot-conf template.
if [ -f "$OUTPUT_DIR/config.json" ]; then
    python3 - "$OUTPUT_DIR/config.json" <<'PYEOF'
import json, sys, re
path = sys.argv[1]
with open(path) as f:
    cfg = json.load(f)

SECRET_NAME = re.compile(r"key|token|secret|password|pgpass", re.I)
stripped = []

def scrub(node, path=""):
    if isinstance(node, dict):
        for k, v in list(node.items()):
            kp = f"{path}.{k}" if path else k
            if isinstance(v, str) and v and SECRET_NAME.search(k):
                node[k] = ""
                stripped.append(kp)
            elif isinstance(v, (dict, list)):
                scrub(v, kp)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            scrub(v, f"{path}[{i}]")

scrub(cfg)
with open(path, "w") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"  Stripped {len(stripped)} secret value(s):")
for s in stripped:
    print(f"    - {s}")
PYEOF
fi
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

# --- 6. .pgpass is deliberately NOT packaged ---
# Nanobot production is REST-only (no DB access), and secrets stay
# in external volumes / per-instance config, never baked into the image.

echo ""
echo "Packaged into: $OUTPUT_DIR/"
ls -la "$OUTPUT_DIR/"
