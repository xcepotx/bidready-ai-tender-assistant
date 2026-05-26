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
  const exactRoleButton = page.getByRole("button", { name: new RegExp(`^${escaped}$`, "i") }).first();

  if (await exactRoleButton.isVisible().catch(() => false)) {
    await exactRoleButton.click();
    return true;
  }

  const startsWithRoleButton = page.getByRole("button", { name: new RegExp(`^${escaped}(\\s|$)`, "i") }).first();

  if (await startsWithRoleButton.isVisible().catch(() => false)) {
    await startsWithRoleButton.click();
    return true;
  }

  const exactText = page.getByText(new RegExp(`^${escaped}$`, "i")).first();

  if (await exactText.isVisible().catch(() => false)) {
    await exactText.click();
    return true;
  }

  const startsWithText = page.getByText(new RegExp(`^${escaped}(\\s|$)`, "i")).first();

  if (await startsWithText.isVisible().catch(() => false)) {
    await startsWithText.click();
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

async function clickRequiredTabAndAssertContent(page, fatalErrors, label, expectedContent) {
  const didClick = await clickByExactTextIfVisible(page, label);

  expect(didClick, `Expected to find and click tab: ${label}`).toBe(true);

  await page.waitForTimeout(700);
  await assertNoFatalBrowserErrors(fatalErrors);

  const bodyText = await page.locator("body").innerText();

  expect(bodyText.trim().length, `Body should not be blank after clicking ${label}`).toBeGreaterThan(80);
  expect(bodyText, `Expected content after clicking ${label}: ${expectedContent}`).toMatch(expectedContent);
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
    { group: "Governance", tabs: ["Compliance", "Traceability", "Approvals", "Gate History", "Audit"] },
    { group: "Execution", tabs: ["Risks", "Actions", "Addendum", "Clarify Tracker"] },
    { group: "Output", tabs: ["Executive Pack", "Proposal Template"] },
  ];

  for (const group of groupedTabs) {
    const groupClicked = await clickByExactTextIfVisible(page, group.group);
    expect(groupClicked, `Expected to click group: ${group.group}`).toBe(true);

    await page.waitForTimeout(250);

    const clickedGroupTabs = await clickTabs(page, fatalErrors, group.tabs);

    expect(
      clickedGroupTabs.length,
      `Expected to click at least one tab in ${group.group}. Clicked: ${clickedGroupTabs.join(", ")}`
    ).toBeGreaterThanOrEqual(1);
  }

  await clickByExactTextIfVisible(page, "Governance");
  await page.waitForTimeout(250);
  await clickRequiredTabAndAssertContent(page, fatalErrors, "Traceability", /Traceability Matrix|Requirement-to-submission|Peta coverage/i);

  await assertNoFatalBrowserErrors(fatalErrors);
});
