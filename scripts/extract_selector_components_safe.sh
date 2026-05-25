#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

run_build() {
  echo
  echo "===== BUILD ====="
  rm -rf apps/web/dist
  (cd apps/web && npm run build)
}

run_guard() {
  echo
  echo "===== GUARD ====="
  scripts/frontend_guard.sh
}

rollback_one() {
  local name="$1"
  local target="apps/web/src/components/${name}.jsx"
  local backup="apps/web/src/App.jsx.bak.extract-${name}"

  echo
  echo "❌ FAILED: ${name}"
  echo "===== ROLLBACK ${name} ====="

  if [ -f "$backup" ]; then
    cp "$backup" apps/web/src/App.jsx
    echo "RESTORED: $backup -> apps/web/src/App.jsx"
  else
    git checkout -- apps/web/src/App.jsx
    echo "RESTORED: apps/web/src/App.jsx from git"
  fi

  rm -f "$target"
  git status --short
  exit 1
}

extract_one() {
  local name="$1"
  local target="apps/web/src/components/${name}.jsx"
  local import_path="./components/${name}.jsx"

  echo
  echo "============================================================"
  echo "Extracting selector component: ${name}"
  echo "============================================================"

  if [ -f "$target" ]; then
    echo "SKIP: ${target} already exists"
    return 0
  fi

  python3 scripts/inspect_component_boundary.py "$name" --out "/tmp/${name}.preview.jsx" || rollback_one "$name"

  python3 scripts/extract_function_component.py "$name" \
    --target "$target" \
    --import-path "$import_path" || rollback_one "$name"

  python3 scripts/extract_function_component.py "$name" \
    --target "$target" \
    --import-path "$import_path" \
    --apply || rollback_one "$name"

  echo
  echo "===== TARGET PREVIEW: ${name} ====="
  sed -n '1,80p' "$target"

  run_build || rollback_one "$name"
  run_guard || rollback_one "$name"

  git add apps/web/src/App.jsx "$target"
  git commit -m "Extract ${name} component safely"

  echo "✅ DONE: ${name}"
}

echo "===== PREFLIGHT ====="
git status --short
run_build
run_guard

extract_one "LanguageSelector"
extract_one "ActorSelector"

echo
echo "============================================================"
echo "FINAL CHECK"
echo "============================================================"
git status --short
run_build
run_guard
