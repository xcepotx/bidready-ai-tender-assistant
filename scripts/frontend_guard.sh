#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."

fail() {
  echo "❌ FAIL: $1"
  exit 1
}

pass() {
  echo "✅ PASS: $1"
}

echo "===== Frontend Module Guard ====="

[ -f apps/web/src/App.jsx ] || fail "App.jsx exists"
[ -f apps/web/src/components/ProjectViewTabs.jsx ] || fail "ProjectViewTabs.jsx exists"
[ -f apps/web/src/views/RequirementsView.jsx ] || fail "RequirementsView.jsx exists"
[ -f apps/web/src/views/ClarificationsView.jsx ] || fail "ClarificationsView.jsx exists"

pass "required frontend module files exist"

if grep -q "function ProjectViewTabs(" apps/web/src/App.jsx; then
  fail "ProjectViewTabs should not live in App.jsx"
fi

if grep -q "function RequirementsView(" apps/web/src/App.jsx; then
  fail "RequirementsView should not live in App.jsx"
fi

if grep -q "function ClarificationsView(" apps/web/src/App.jsx; then
  fail "ClarificationsView should not live in App.jsx"
fi

pass "extracted views are not duplicated inside App.jsx"

if grep -q "downloadExecutivePack" apps/web/src/views/RequirementsView.jsx; then
  fail "RequirementsView must not reference downloadExecutivePack"
fi

pass "RequirementsView has no unrelated export handler reference"

if grep -q "<ClarificationDetail" apps/web/src/views/ClarificationsView.jsx; then
  if ! grep -q "function ClarificationDetail(" apps/web/src/views/ClarificationsView.jsx; then
    fail "ClarificationsView uses ClarificationDetail but does not define it locally"
  fi
fi

pass "ClarificationDetail dependency is local to ClarificationsView"

python3 - <<'PY'
from pathlib import Path
import re
import sys

bad = []

for path in list(Path("apps/web/src").rglob("*.jsx")) + list(Path("apps/web/src").rglob("*.js")):
    text = path.read_text(errors="ignore")

    uses_l = re.search(r"(?<![A-Za-z0-9_])L\(", text)
    has_l = "function L(" in text or "const L =" in text

    if uses_l and not has_l:
        bad.append(str(path))

if bad:
    print("Files using L(...) without local L helper:")
    for item in bad:
        print("-", item)
    sys.exit(1)

print("✅ PASS: L helper usage is locally defined")
PY

pass "frontend helper scope check passed"

echo
echo "===== Frontend Build ====="
cd apps/web
npm run build
cd ../..

pass "frontend build passed"

echo
echo "✅ FRONTEND GUARD PASSED"
