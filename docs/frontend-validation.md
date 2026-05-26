# Frontend Validation Gate

Run this gate after every frontend refactor, UI patch, or extracted component/hook change.

Command:

    cd /data/tender-ai/app/tender-review-assistant

    rm -rf apps/web/dist
    cd apps/web && npm run build
    cd ../..

    scripts/frontend_guard.sh
    scripts/smoke_test_bidready_i18n.sh
    scripts/smoke_test_frontend_browser.sh

## Why this exists

Vite build can pass while runtime browser errors still happen, for example:

- ResponseList is not defined
- ExecutiveDashboardCard is not defined
- Upload is not defined
- L is not defined

The browser smoke test opens the app and checks main workspace tabs for fatal browser runtime errors.

## Disk note

Playwright browser cache is configured to use /data/tender-ai/cache through scripts/smoke_test_frontend_browser.sh to avoid filling the root filesystem.

## Rule

Do not commit if any of these fail:

1. npm run build
2. scripts/frontend_guard.sh
3. scripts/smoke_test_bidready_i18n.sh
4. scripts/smoke_test_frontend_browser.sh
