#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_DIR="$ROOT_DIR/apps/web"
WEB_URL="${BIDREADY_WEB_URL:-http://127.0.0.1:3000}"
BIDREADY_CACHE_DIR="${BIDREADY_CACHE_DIR:-/data/tender-ai/cache}"
export npm_config_cache="$BIDREADY_CACHE_DIR/npm"
export PLAYWRIGHT_BROWSERS_PATH="$BIDREADY_CACHE_DIR/ms-playwright"
mkdir -p "$npm_config_cache" "$PLAYWRIGHT_BROWSERS_PATH"

echo "===== BidReady Frontend Browser Smoke ====="
echo "ROOT_DIR=$ROOT_DIR"
echo "WEB_DIR=$WEB_DIR"
echo "WEB_URL=$WEB_URL"
echo "npm_config_cache=$npm_config_cache"
echo "PLAYWRIGHT_BROWSERS_PATH=$PLAYWRIGHT_BROWSERS_PATH"

echo
echo "===== CHECK WEB READY ====="
WEB_OK=0
for i in $(seq 1 30); do
  if curl -fsS "$WEB_URL" >/dev/null 2>&1; then
    WEB_OK=1
    echo "WEB OK"
    break
  fi

  echo "Waiting web... $i"
  sleep 1
done

if [ "$WEB_OK" != "1" ]; then
  echo "ERROR: Web is not reachable at $WEB_URL"
  exit 1
fi

cd "$WEB_DIR"

echo
echo "===== CHECK PLAYWRIGHT DEPENDENCY ====="
if [ ! -d "node_modules/@playwright/test" ]; then
  echo "Installing @playwright/test..."
  npm install -D @playwright/test
fi

echo
echo "===== ENSURE CHROMIUM INSTALLED ====="
npx playwright install chromium

echo
echo "===== RUN BROWSER SMOKE ====="
BIDREADY_WEB_URL="$WEB_URL" npx playwright test tests/bidready-browser-smoke.spec.js --project=chromium --reporter=line
