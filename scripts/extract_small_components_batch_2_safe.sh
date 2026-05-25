#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

extract_one() {
  local name="$1"
  local target="apps/web/src/components/${name}.jsx"
  local import_path="./components/${name}.jsx"

  echo
  echo "============================================================"
  echo "Extracting: ${name}"
  echo "============================================================"

  if [ -f "$target" ]; then
    echo "SKIP: ${target} already exists"
    return 0
  fi

  echo "===== INSPECT: ${name} ====="
  python3 scripts/inspect_component_boundary.py "$name" --out "/tmp/${name}.preview.jsx"

  echo
  echo "===== DRY RUN: ${name} ====="
  python3 scripts/extract_function_component.py "$name" \
    --target "$target" \
    --import-path "$import_path"

  echo
  echo "===== APPLY: ${name} ====="
  python3 scripts/extract_function_component.py "$name" \
    --target "$target" \
    --import-path "$import_path" \
    --apply

  echo
  echo "===== BUILD AFTER ${name} ====="
  rm -rf apps/web/dist
  (cd apps/web && npm run build)

  echo
  echo "===== GUARD AFTER ${name} ====="
  scripts/frontend_guard.sh

  echo
  echo "===== COMMIT ${name} ====="
  git add apps/web/src/App.jsx "$target"
  git commit -m "Extract ${name} component safely"

  echo "DONE: ${name}"
}

extract_one "DecisionList"
extract_one "MetadataField"
extract_one "BriefList"
extract_one "RelationBox"
extract_one "ResponseList"
extract_one "ProposalList"

echo
echo "============================================================"
echo "FINAL CHECK"
echo "============================================================"
git status --short
rm -rf apps/web/dist
(cd apps/web && npm run build)
scripts/frontend_guard.sh
