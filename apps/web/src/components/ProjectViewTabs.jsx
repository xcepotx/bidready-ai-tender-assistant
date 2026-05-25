function ProjectViewTabs({
  activeProjectView,
  setActiveProjectView,
  uiLanguage = "en",
  selectedProjectId = null,
  busy = false,
  downloadExecutivePack = null,
  proposalTemplate = null,
  clarificationTracker = { summary: null, items: [] },
  addendumImpacts = { summary: null, items: [] },
  decisionGateHistory = { summary: null, events: [] },
  approvalWorkflow = { summary: null, request: null, steps: [] },
  complianceScorecard = { summary: null, items: [] },
  riskItems = [],
  actionItems = [],
}) {
  const isIdUi = uiLanguage === "id";
  const L = (en, id) => (isIdUi ? id : en);

  const groups = [
    {
      key: "main",
      label: L("Main", "Utama"),
      description: L("Core tender review flow", "Alur utama review tender"),
      tabs: [
        { key: "summary", label: L("Overview", "Ringkasan") },
        { key: "requirements", label: L("Requirements", "Requirement") },
        { key: "clarifications", label: L("Clarifications", "Klarifikasi") },
        { key: "response", label: L("Response", "Respons") },
        { key: "proposal", label: L("Proposal", "Proposal") },
        { key: "evidence", label: L("Evidence", "Evidence") },
      ],
    },
    {
      key: "governance",
      label: L("Governance", "Governance"),
      description: L("Compliance, approval, and audit controls", "Kontrol compliance, approval, dan audit"),
      tabs: [
        { key: "compliance", label: L("Compliance", "Compliance"), badge: complianceScorecard?.summary?.total_items ?? complianceScorecard?.items?.length ?? 0 },
        { key: "approvals", label: L("Approvals", "Approval"), badge: approvalWorkflow?.summary?.pending_steps ?? approvalWorkflow?.steps?.length ?? 0 },
        { key: "gateHistory", label: L("Gate History", "Riwayat Gate"), badge: decisionGateHistory?.summary?.total_events ?? decisionGateHistory?.events?.length ?? 0 },
        { key: "audit", label: L("Audit", "Audit") },
      ],
    },
    {
      key: "execution",
      label: L("Execution", "Eksekusi"),
      description: L("Risks, actions, document changes, and clarification follow-up", "Risiko, action, perubahan dokumen, dan follow-up klarifikasi"),
      tabs: [
        { key: "risks", label: L("Risks", "Risiko"), badge: riskItems?.length ?? 0 },
        { key: "actions", label: L("Actions", "Action"), badge: actionItems?.length ?? 0 },
        { key: "addendum", label: L("Addendum", "Addendum"), badge: addendumImpacts?.summary?.total_items ?? addendumImpacts?.items?.length ?? 0 },
        { key: "clarificationTracker", label: L("Clarify Tracker", "Tracker Klarifikasi"), badge: clarificationTracker?.summary?.open_items ?? clarificationTracker?.items?.length ?? 0 },
      ],
    },
    {
      key: "output",
      label: L("Output", "Output"),
      description: L("Proposal template and export preparation", "Template proposal dan persiapan export"),
      tabs: [
        { key: "template", label: L("Template", "Template"), badge: proposalTemplate?.id ? 1 : 0 },
        { key: "executivePack", label: L("Executive Pack", "Executive Pack") },
      ],
    },
  ];

  const activeGroup =
    groups.find((group) => group.tabs.some((tab) => tab.key === activeProjectView))?.key || "main";

  const selectedGroup = groups.find((group) => group.key === activeGroup) || groups[0];

  return (
    <div className="groupedProjectTabs">
      <div className="tabGroupSelector">
        {groups.map((group) => {
          const groupBadge = group.tabs.reduce((total, tab) => total + Number(tab.badge || 0), 0);
          const isActive = group.key === activeGroup;

          return (
            <button
              key={group.key}
              type="button"
              className={`tabGroupButton ${isActive ? "active" : ""}`}
              onClick={() => {
                if (!isActive && group.tabs[0]) {
                  setActiveProjectView(group.tabs[0].key);
                }
              }}
            >
              <span>{group.label}</span>
              {groupBadge > 0 && <strong>{groupBadge}</strong>}
            </button>
          );
        })}
      </div>

      <div className="tabGroupMeta">
        <strong>{selectedGroup.label}</strong>
        <span>{selectedGroup.description}</span>
      </div>

      <div className="projectViewTabs groupedTabsRow">
        {selectedGroup.tabs.map((tab) => {
          const isActive = activeProjectView === tab.key;

          return (
            <button
              key={tab.key}
              type="button"
              className={`projectTab ${isActive ? "active" : ""}`}
              onClick={() => setActiveProjectView(tab.key)}
            >
              <span>{tab.label}</span>
              {Number(tab.badge || 0) > 0 && <span className="tabBadge">{tab.badge}</span>}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default ProjectViewTabs;
