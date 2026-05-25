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

  echo
  echo "===== POST-ROLLBACK STATUS ====="
  git status --short

  echo
  echo "Stopped at ${name}. Send the error output to continue manually."
  exit 1
}

extract_one() {
  local name="$1"
  local target="apps/web/src/components/${name}.jsx"
  local import_path="./components/${name}.jsx"

  echo
  echo "============================================================"
  echo "Extracting card component: ${name}"
  echo "============================================================"

  if [ -f "$target" ]; then
    echo "SKIP: ${target} already exists"
    return 0
  fi

  echo "===== INSPECT: ${name} ====="
  python3 scripts/inspect_component_boundary.py "$name" --out "/tmp/${name}.preview.jsx" || rollback_one "$name"

  echo
  echo "===== DRY RUN: ${name} ====="
  python3 scripts/extract_function_component.py "$name" \
    --target "$target" \
    --import-path "$import_path" || rollback_one "$name"

  echo
  echo "===== APPLY: ${name} ====="
  python3 scripts/extract_function_component.py "$name" \
    --target "$target" \
    --import-path "$import_path" \
    --apply || rollback_one "$name"

  echo
  echo "===== INJECT LOCAL IMPORTS: ${name} ====="
  python3 scripts/inject_component_imports.py "$target" --self-name "$name" || rollback_one "$name"

  echo
  echo "===== TARGET PREVIEW: ${name} ====="
  sed -n '1,40p' "$target"

  run_build || rollback_one "$name"
  run_guard || rollback_one "$name"

  echo
  echo "===== COMMIT ${name} ====="
  git add apps/web/src/App.jsx "$target"
  git commit -m "Extract ${name} component safely"

  echo "✅ DONE: ${name}"
}

echo "===== PREFLIGHT ====="
git status --short
run_build
run_guard

extract_one "DecisionGateCard"
extract_one "RfpMetadataCard"
extract_one "BidBriefCard"
extract_one "ReadinessSummaryCard"

echo
echo "============================================================"
echo "FINAL CHECK"
echo "============================================================"
git status --short
run_build
run_guard
