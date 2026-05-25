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

# Commit extractor script itself if still uncommitted
if ! git diff --quiet -- scripts/extract_function_component.py 2>/dev/null || git ls-files --others --exclude-standard | grep -q '^scripts/extract_function_component.py$'; then
  git add scripts/extract_function_component.py
  git commit -m "Add safe function component extractor"
fi

# Commit ActionStat if it was extracted but not committed yet
if [ -f apps/web/src/components/ActionStat.jsx ]; then
  if ! git diff --quiet -- apps/web/src/App.jsx apps/web/src/components/ActionStat.jsx 2>/dev/null || git ls-files --others --exclude-standard | grep -q '^apps/web/src/components/ActionStat.jsx$'; then
    rm -rf apps/web/dist
    (cd apps/web && npm run build)
    scripts/frontend_guard.sh
    git add apps/web/src/App.jsx apps/web/src/components/ActionStat.jsx
    git commit -m "Extract ActionStat component safely"
  fi
fi

extract_one "ExecutiveMetric"
extract_one "ExecutiveStage"
extract_one "EvidenceStat"
extract_one "RiskStat"
extract_one "ComplianceMetric"
extract_one "ComplianceRelationBox"

echo
echo "============================================================"
echo "FINAL CHECK"
echo "============================================================"
git status --short
rm -rf apps/web/dist
(cd apps/web && npm run build)
scripts/frontend_guard.sh
