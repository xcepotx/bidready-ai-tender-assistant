import { useMemo, useState } from "react";
import { translateRequirementTextForUi } from "../utils/i18n.js";

const DONE_STATUSES = new Set(["done", "closed", "completed", "cancelled", "canceled", "resolved", "accepted", "approved"]);
const BAD_COMPLIANCE = new Set(["needs_review", "needs_clarification", "partially_compliant", "non_compliant", "blocked"]);

const GAP_DEFINITIONS = {
  missing_response: {
    tone: "critical",
    en: "Missing response",
    id: "Respons kosong",
  },
  missing_evidence: {
    tone: "warning",
    en: "Missing evidence",
    id: "Evidence kosong",
  },
  missing_proposal: {
    tone: "warning",
    en: "Missing proposal",
    id: "Proposal kosong",
  },
  compliance_gap: {
    tone: "critical",
    en: "Compliance gap",
    id: "Gap compliance",
  },
  open_actions: {
    tone: "warning",
    en: "Open actions",
    id: "Action open",
  },
  open_clarifications: {
    tone: "warning",
    en: "Open clarifications",
    id: "Klarifikasi open",
  },
  high_risk: {
    tone: "critical",
    en: "High risk",
    id: "High risk",
  },
};

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function hasId(values, id) {
  return asArray(values).map(Number).includes(Number(id));
}

function intersects(values, idSet) {
  const safeSet = new Set(Array.from(idSet || []).map(Number));
  return asArray(values).some((value) => safeSet.has(Number(value)));
}

function isDone(status) {
  return DONE_STATUSES.has(String(status || "").toLowerCase());
}

function shortText(value, max = 130) {
  const text = String(value || "").trim();
  if (text.length <= max) return text;
  return `${text.slice(0, max).trim()}...`;
}

function prettifyMeta(value) {
  return String(value || "-")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function getRequirementText(req, uiLanguage) {
  return translateRequirementTextForUi(req?.requirement_text || "", uiLanguage);
}

function getRequirementMeta(value, uiLanguage) {
  return translateRequirementTextForUi(prettifyMeta(value), uiLanguage);
}

function getCoverageStatus(row) {
  if (row.gaps.length === 0) return "complete";

  const criticalGaps = row.gaps.filter((gap) => GAP_DEFINITIONS[gap]?.tone === "critical");

  if (criticalGaps.length > 0) return "critical";

  return "attention";
}

function coverageLabel(status, L) {
  if (status === "complete") return L("Complete", "Lengkap");
  if (status === "critical") return L("Critical gap", "Gap kritikal");
  return L("Needs attention", "Perlu perhatian");
}

function gapLabel(gap, L) {
  const definition = GAP_DEFINITIONS[gap];
  if (!definition) return gap.replaceAll("_", " ");
  return L(definition.en, definition.id);
}

function gapTone(gap) {
  return GAP_DEFINITIONS[gap]?.tone || "neutral";
}

function TraceabilityMetric({ label, value, tone = "neutral", helper }) {
  return (
    <div className={`traceabilityMetric ${tone}`}>
      <strong>{value}</strong>
      <span>{label}</span>
      {helper && <small>{helper}</small>}
    </div>
  );
}

function TraceabilityQuickFilter({ active, value, label, count, onClick }) {
  return (
    <button
      type="button"
      className={active ? "active" : ""}
      onClick={() => onClick(value)}
    >
      <span>{label}</span>
      <strong>{count}</strong>
    </button>
  );
}

export default function TraceabilityMatrixView({
  requirements = [],
  responsePlan = [],
  evidencePack = [],
  proposalOutline = [],
  clarifications = [],
  complianceScorecard = { summary: null, items: [] },
  riskItems = [],
  actionItems = [],
  languageSetting = { output_language: "en" },
  downloadTraceabilityMatrix = null,
}) {
  const uiLanguage = String(languageSetting?.output_language || "en");
  const isId = uiLanguage.startsWith("id");
  const L = (en, id) => (isId ? id : en);

  const [searchQuery, setSearchQuery] = useState("");
  const [gapFilter, setGapFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const safeRequirements = asArray(requirements);
  const safeResponsePlan = asArray(responsePlan);
  const safeEvidencePack = asArray(evidencePack);
  const safeProposalOutline = asArray(proposalOutline);
  const safeClarifications = asArray(clarifications);
  const safeComplianceItems = asArray(complianceScorecard?.items);
  const safeRiskItems = asArray(riskItems);
  const safeActionItems = asArray(actionItems);

  const rows = useMemo(() => {
    return safeRequirements
      .map((req) => {
        const reqId = Number(req.id);

        const responses = safeResponsePlan.filter((item) => Number(item.requirement_id) === reqId);
        const responseIds = new Set(responses.map((item) => Number(item.id)).filter(Number.isFinite));

        const evidenceItems = safeEvidencePack.filter((item) =>
          hasId(item.related_requirement_ids, reqId) || intersects(item.related_response_item_ids, responseIds)
        );
        const evidenceIds = new Set(evidenceItems.map((item) => Number(item.id)).filter(Number.isFinite));

        const proposalSections = safeProposalOutline.filter((section) =>
          intersects(section.source_response_item_ids, responseIds)
        );
        const proposalIds = new Set(proposalSections.map((item) => Number(item.id)).filter(Number.isFinite));

        const requirementClarifications = safeClarifications.filter((item) => Number(item.requirement_id) === reqId);

        const complianceItems = safeComplianceItems.filter((item) =>
          Number(item.requirement_id) === reqId || responseIds.has(Number(item.response_item_id))
        );

        const risks = safeRiskItems.filter((item) =>
          hasId(item.related_requirement_ids, reqId) ||
          intersects(item.related_response_item_ids, responseIds) ||
          intersects(item.related_evidence_item_ids, evidenceIds) ||
          (item.source_type === "requirement" && Number(item.source_id) === reqId)
        );

        const actions = safeActionItems.filter((item) =>
          hasId(item.related_requirement_ids, reqId) ||
          intersects(item.related_response_item_ids, responseIds) ||
          intersects(item.related_evidence_item_ids, evidenceIds) ||
          intersects(item.related_proposal_section_ids, proposalIds) ||
          (item.source_type === "requirement" && Number(item.source_id) === reqId)
        );

        const openActions = actions.filter((item) => !isDone(item.status));
        const openClarifications = requirementClarifications.filter((item) => !isDone(item.status));
        const highRisks = risks.filter((item) => ["high", "critical"].includes(String(item.severity || item.risk_level || "").toLowerCase()));
        const complianceGap = complianceItems.some((item) => BAD_COMPLIANCE.has(String(item.compliance_status || "").toLowerCase()));

        const gaps = [];
        if (responses.length === 0) gaps.push("missing_response");
        if (evidenceItems.length === 0) gaps.push("missing_evidence");
        if (proposalSections.length === 0) gaps.push("missing_proposal");
        if (complianceGap) gaps.push("compliance_gap");
        if (openActions.length > 0) gaps.push("open_actions");
        if (openClarifications.length > 0) gaps.push("open_clarifications");
        if (highRisks.length > 0) gaps.push("high_risk");

        return {
          requirement: req,
          responses,
          evidenceItems,
          proposalSections,
          complianceItems,
          risks,
          actions,
          openActions,
          openClarifications,
          highRisks,
          gaps,
          complianceGap,
        };
      })
      .map((row) => ({
        ...row,
        coverageStatus: getCoverageStatus(row),
      }))
      .sort((a, b) => {
        const statusRank = { critical: 0, attention: 1, complete: 2 };
        const statusDiff = statusRank[a.coverageStatus] - statusRank[b.coverageStatus];
        if (statusDiff !== 0) return statusDiff;

        const gapDiff = b.gaps.length - a.gaps.length;
        if (gapDiff !== 0) return gapDiff;

        return Number(a.requirement.id || 0) - Number(b.requirement.id || 0);
      });
  }, [
    safeRequirements,
    safeResponsePlan,
    safeEvidencePack,
    safeProposalOutline,
    safeClarifications,
    safeComplianceItems,
    safeRiskItems,
    safeActionItems,
  ]);

  const statusOptions = Array.from(new Set(safeRequirements.map((item) => item.status).filter(Boolean))).sort();

  const metrics = {
    total: rows.length,
    complete: rows.filter((row) => row.coverageStatus === "complete").length,
    critical: rows.filter((row) => row.coverageStatus === "critical").length,
    attention: rows.filter((row) => row.coverageStatus === "attention").length,
    missingResponse: rows.filter((row) => row.gaps.includes("missing_response")).length,
    missingEvidence: rows.filter((row) => row.gaps.includes("missing_evidence")).length,
    openActions: rows.filter((row) => row.gaps.includes("open_actions")).length,
    complianceGap: rows.filter((row) => row.complianceGap).length,
  };

  const filteredRows = rows.filter((row) => {
    const req = row.requirement;
    const query = searchQuery.trim().toLowerCase();

    const displayRequirementText = getRequirementText(req, uiLanguage);
    const displayCategory = getRequirementMeta(req.category, uiLanguage);
    const displayStatus = getRequirementMeta(req.status, uiLanguage);
    const displayRisk = getRequirementMeta(req.risk_level, uiLanguage);

    const matchesSearch =
      !query ||
      displayRequirementText.toLowerCase().includes(query) ||
      displayCategory.toLowerCase().includes(query) ||
      String(req.suggested_owner || "").toLowerCase().includes(query) ||
      displayStatus.toLowerCase().includes(query) ||
      displayRisk.toLowerCase().includes(query);

    const matchesStatus = statusFilter === "all" || req.status === statusFilter;

    const matchesGap =
      gapFilter === "all" ||
      (gapFilter === "complete" && row.coverageStatus === "complete") ||
      (gapFilter === "critical" && row.coverageStatus === "critical") ||
      (gapFilter === "attention" && row.coverageStatus === "attention") ||
      (gapFilter === "has_gaps" && row.gaps.length > 0) ||
      row.gaps.includes(gapFilter);

    return matchesSearch && matchesStatus && matchesGap;
  });

  const quickFilters = [
    ["all", L("All", "Semua"), metrics.total],
    ["critical", L("Critical", "Kritikal"), metrics.critical],
    ["missing_response", L("Missing response", "Respons kosong"), metrics.missingResponse],
    ["missing_evidence", L("Missing evidence", "Evidence kosong"), metrics.missingEvidence],
    ["open_actions", L("Open actions", "Action open"), metrics.openActions],
    ["complete", L("Complete", "Lengkap"), metrics.complete],
  ];

  return (
    <div className="workspaceView traceabilityView">
      <div className="viewHeader traceabilityHeader">
        <div>
          <p className="eyebrow">Traceability Matrix</p>
          <h2>{L("Requirement-to-submission coverage map", "Peta coverage requirement sampai submission")}</h2>
          <p className="muted">
            {L(
              "Track each requirement across response plan, evidence, proposal sections, compliance, risks, actions, and clarifications.",
              "Pantau setiap requirement terhadap response plan, evidence, proposal section, compliance, risk, action, dan klarifikasi."
            )}
          </p>
        </div>

        <button
          type="button"
          className="regenerateAllButton"
          disabled={!downloadTraceabilityMatrix}
          onClick={downloadTraceabilityMatrix}
        >
          {L("Export Traceability Excel", "Export Traceability Excel")}
        </button>
      </div>

      <div className="traceabilityMetricGrid">
        <TraceabilityMetric label={L("Requirements", "Requirement")} value={metrics.total} helper={L("Total analyzed", "Total dianalisis")} />
        <TraceabilityMetric label={L("Complete", "Lengkap")} value={metrics.complete} tone="ok" helper={L("No visible gap", "Tanpa gap terlihat")} />
        <TraceabilityMetric label={L("Critical gaps", "Gap kritikal")} value={metrics.critical} tone={metrics.critical ? "danger" : "ok"} helper={L("Needs priority review", "Perlu review prioritas")} />
        <TraceabilityMetric label={L("Needs attention", "Perlu perhatian")} value={metrics.attention} tone={metrics.attention ? "warning" : "ok"} helper={L("Operational follow-up", "Follow-up operasional")} />
        <TraceabilityMetric label={L("Missing evidence", "Evidence kosong")} value={metrics.missingEvidence} tone={metrics.missingEvidence ? "warning" : "ok"} helper={L("Evidence coverage", "Coverage evidence")} />
        <TraceabilityMetric label={L("Compliance gaps", "Gap compliance")} value={metrics.complianceGap} tone={metrics.complianceGap ? "danger" : "ok"} helper={L("Compliance review", "Review compliance")} />
      </div>

      <div className="traceabilityQuickFilters" aria-label="Traceability quick filters">
        {quickFilters.map(([value, label, count]) => (
          <TraceabilityQuickFilter
            key={value}
            active={gapFilter === value}
            value={value}
            label={label}
            count={count}
            onClick={setGapFilter}
          />
        ))}
      </div>

      <div className="filterBar traceabilityFilterBar">
        <input
          className="filterInput"
          value={searchQuery}
          onChange={(event) => setSearchQuery(event.target.value)}
          placeholder={L("Search requirement, category, owner, status, or risk...", "Cari requirement, kategori, owner, status, atau risk...")}
        />

        <select className="filterSelect" value={gapFilter} onChange={(event) => setGapFilter(event.target.value)}>
          <option value="all">{L("All coverage", "Semua coverage")}</option>
          <option value="critical">{L("Critical gaps", "Gap kritikal")}</option>
          <option value="attention">{L("Needs attention", "Perlu perhatian")}</option>
          <option value="has_gaps">{L("Has any gap", "Ada gap")}</option>
          <option value="missing_response">{L("Missing response", "Respons kosong")}</option>
          <option value="missing_evidence">{L("Missing evidence", "Evidence kosong")}</option>
          <option value="missing_proposal">{L("Missing proposal", "Proposal kosong")}</option>
          <option value="compliance_gap">{L("Compliance gap", "Gap compliance")}</option>
          <option value="open_actions">{L("Open actions", "Action open")}</option>
          <option value="open_clarifications">{L("Open clarifications", "Klarifikasi open")}</option>
          <option value="high_risk">High risk</option>
          <option value="complete">{L("Complete only", "Lengkap saja")}</option>
        </select>

        <select className="filterSelect" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
          <option value="all">{L("All statuses", "Semua status")}</option>
          {statusOptions.map((status) => (
            <option key={status} value={status}>{status}</option>
          ))}
        </select>

        <button
          type="button"
          className="clearFilterButton"
          onClick={() => {
            setSearchQuery("");
            setGapFilter("all");
            setStatusFilter("all");
          }}
        >
          {L("Clear", "Reset")}
        </button>
      </div>

      <p className="actionTrackerMeta">
        {L("Showing", "Menampilkan")} <strong>{filteredRows.length}</strong> / <strong>{rows.length}</strong> {L("requirement row(s)", "baris requirement")}
      </p>

      <div className="traceabilityTableWrap">
        <table className="traceabilityTable">
          <thead>
            <tr>
              <th>{L("Requirement", "Requirement")}</th>
              <th>{L("Coverage", "Coverage")}</th>
              <th>{L("Response", "Respons")}</th>
              <th>Evidence</th>
              <th>Proposal</th>
              <th>Compliance</th>
              <th>Risk</th>
              <th>{L("Actions", "Action")}</th>
              <th>{L("Clarifications", "Klarifikasi")}</th>
              <th>{L("Gaps", "Gap")}</th>
            </tr>
          </thead>

          <tbody>
            {filteredRows.map((row) => {
              const req = row.requirement;
              const complianceStatus = row.complianceItems[0]?.compliance_status || "-";

              return (
                <tr key={req.id} className={`traceabilityRow ${row.coverageStatus}`}>
                  <td className="traceabilityRequirementCell">
                    <strong>#{req.id} · {getRequirementMeta(req.category, uiLanguage)}</strong>
                    <span>{shortText(getRequirementText(req, uiLanguage))}</span>
                    <small>
                      {L("Owner", "PIC")}: {req.suggested_owner || "-"} · {L("Status", "Status")}: {getRequirementMeta(req.status, uiLanguage)}
                    </small>
                  </td>

                  <td>
                    <strong className={`traceabilityCoveragePill ${row.coverageStatus}`}>
                      {coverageLabel(row.coverageStatus, L)}
                    </strong>
                    <span>{row.gaps.length} {L("gap(s)", "gap")}</span>
                  </td>

                  <td><strong>{row.responses.length}</strong><span>{row.responses[0]?.compliance_status || "-"}</span></td>
                  <td><strong>{row.evidenceItems.length}</strong><span>{row.evidenceItems[0]?.status || "-"}</span></td>
                  <td><strong>{row.proposalSections.length}</strong><span>{row.proposalSections[0]?.status || "-"}</span></td>
                  <td><strong className={`traceabilityStatus ${complianceStatus}`}>{complianceStatus}</strong><span>{row.complianceItems[0]?.evidence_coverage || "-"}</span></td>
                  <td><strong>{row.risks.length}</strong><span>{row.highRisks.length} high</span></td>
                  <td><strong>{row.actions.length}</strong><span>{row.openActions.length} open</span></td>
                  <td><strong>{row.openClarifications.length}</strong><span>{row.openClarifications.length ? "open" : "-"}</span></td>
                  <td>
                    <div className="traceabilityGapList">
                      {row.gaps.length === 0 ? (
                        <span className="traceabilityGapPill ok">{L("Complete", "Lengkap")}</span>
                      ) : (
                        row.gaps.map((gap) => (
                          <span className={`traceabilityGapPill ${gapTone(gap)}`} key={`${req.id}-${gap}`}>
                            {gapLabel(gap, L)}
                          </span>
                        ))
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {safeRequirements.length === 0 && (
          <div className="emptyState actionEmptyState">
            <h3>{L("No requirements yet", "Belum ada requirement")}</h3>
            <p>{L("Analyze the RFP first to build the traceability matrix.", "Analyze RFP dulu untuk membangun traceability matrix.")}</p>
          </div>
        )}

        {safeRequirements.length > 0 && filteredRows.length === 0 && (
          <div className="emptyState actionEmptyState">
            <h3>{L("No matching rows", "Tidak ada data yang cocok")}</h3>
            <p>{L("Try adjusting search or filters.", "Coba ubah search atau filter.")}</p>
          </div>
        )}
      </div>
    </div>
  );
}
