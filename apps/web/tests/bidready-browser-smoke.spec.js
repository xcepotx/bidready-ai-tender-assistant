import { test, expect } from "@playwright/test";

const BASE_URL = process.env.BIDREADY_WEB_URL || "http://127.0.0.1:3000";

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

async function assertNoFatalBrowserErrors(fatalErrors) {
  const fatal = fatalErrors.filter(Boolean);

  expect(fatal, `Fatal browser errors:\n${fatal.join("\n\n")}`).toEqual([]);
}

async function clickByExactTextIfVisible(page, label) {
  const escaped = escapeRegExp(label);
  const roleButton = page.getByRole("button", { name: new RegExp(`^${escaped}$`, "i") }).first();

  if (await roleButton.isVisible().catch(() => false)) {
    await roleButton.click();
    return true;
  }

  const exactText = page.getByText(new RegExp(`^${escaped}$`, "i")).first();

  if (await exactText.isVisible().catch(() => false)) {
    await exactText.click();
    return true;
  }

  return false;
}

async function maybeSelectFirstProject(page) {
  const selectProjectVisible = await page
    .getByText(/Select a bid project/i)
    .first()
    .isVisible({ timeout: 2000 })
    .catch(() => false);

  if (!selectProjectVisible) return;

  const projectCandidate = page
    .locator("button, [role='button'], .projectCard, .projectItem, .projectTile")
    .filter({ hasText: /RFP|Tender|Bid|Managed|Services|Enterprise|Project/i })
    .first();

  if (await projectCandidate.isVisible().catch(() => false)) {
    await projectCandidate.click();
    await page.waitForTimeout(500);
  }
}

async function clickTabs(page, fatalErrors, tabs) {
  const clicked = [];

  for (const tab of tabs) {
    const didClick = await clickByExactTextIfVisible(page, tab);

    if (!didClick) continue;

    clicked.push(tab);
    await page.waitForTimeout(500);
    await assertNoFatalBrowserErrors(fatalErrors);

    const bodyText = await page.locator("body").innerText();
    expect(bodyText.trim().length, `Body should not be blank after clicking ${tab}`).toBeGreaterThan(50);
  }

  return clicked;
}

test("BidReady browser smoke: main workspace tabs render without runtime errors", async ({ page }) => {
  const fatalErrors = [];

  page.on("pageerror", (error) => {
    fatalErrors.push(error?.stack || error?.message || String(error));
  });

  page.on("console", (message) => {
    if (message.type() !== "error") return;

    const text = message.text();

    if (
      /ReferenceError|is not defined|Cannot read properties|Cannot access|Uncaught/i.test(text)
    ) {
      fatalErrors.push(text);
    }
  });

  await page.goto(BASE_URL, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle").catch(() => {});
  await expect(page.getByText(/BidReady AI/i).first()).toBeVisible({ timeout: 15000 });

  await assertNoFatalBrowserErrors(fatalErrors);
  await maybeSelectFirstProject(page);

  const mainTabs = ["Overview", "Requirements", "Clarifications", "Response"];
  const clickedMainTabs = await clickTabs(page, fatalErrors, mainTabs);

  expect(
    clickedMainTabs.length,
    `Expected to click at least 3 main tabs. Clicked: ${clickedMainTabs.join(", ")}`
  ).toBeGreaterThanOrEqual(3);

  const groupedTabs = [
    { group: "Governance", tabs: ["Compliance", "Risk", "Approval", "Gate History"] },
    { group: "Execution", tabs: ["Actions", "Clarification Tracker", "Addendum"] },
    { group: "Output", tabs: ["Proposal", "Evidence", "Executive Pack", "Audit"] },
  ];

  for (const group of groupedTabs) {
    await clickByExactTextIfVisible(page, group.group);
    await page.waitForTimeout(250);
    await clickTabs(page, fatalErrors, group.tabs);
  }

  await assertNoFatalBrowserErrors(fatalErrors);
});
