import { useMemo, useState } from "react";

const DONE_STATUSES = new Set(["done", "closed", "completed", "cancelled", "canceled", "resolved", "accepted", "approved"]);
const BAD_COMPLIANCE = new Set(["needs_review", "needs_clarification", "partially_compliant", "non_compliant", "blocked"]);

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

function TraceabilityMetric({ label, value, tone = "neutral" }) {
  return (
    <div className={`traceabilityMetric ${tone}`}>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
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
}) {
  const isId = String(languageSetting?.output_language || "en").startsWith("id");
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
      .sort((a, b) => b.gaps.length - a.gaps.length || Number(a.requirement.id || 0) - Number(b.requirement.id || 0));
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

  const filteredRows = rows.filter((row) => {
    const req = row.requirement;
    const query = searchQuery.trim().toLowerCase();

    const matchesSearch =
      !query ||
      String(req.requirement_text || "").toLowerCase().includes(query) ||
      String(req.category || "").toLowerCase().includes(query) ||
      String(req.suggested_owner || "").toLowerCase().includes(query) ||
      String(req.status || "").toLowerCase().includes(query) ||
      String(req.risk_level || "").toLowerCase().includes(query);

    const matchesStatus = statusFilter === "all" || req.status === statusFilter;

    const matchesGap =
      gapFilter === "all" ||
      (gapFilter === "complete" && row.gaps.length === 0) ||
      (gapFilter === "has_gaps" && row.gaps.length > 0) ||
      row.gaps.includes(gapFilter);

    return matchesSearch && matchesStatus && matchesGap;
  });

  const metrics = {
    total: rows.length,
    complete: rows.filter((row) => row.gaps.length === 0).length,
    missingResponse: rows.filter((row) => row.gaps.includes("missing_response")).length,
    missingEvidence: rows.filter((row) => row.gaps.includes("missing_evidence")).length,
    openActions: rows.filter((row) => row.gaps.includes("open_actions")).length,
    complianceGap: rows.filter((row) => row.complianceGap).length,
  };

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
      </div>

      <div className="traceabilityMetricGrid">
        <TraceabilityMetric label={L("Requirements", "Requirement")} value={metrics.total} />
        <TraceabilityMetric label={L("Complete", "Lengkap")} value={metrics.complete} tone="ok" />
        <TraceabilityMetric label={L("Missing response", "Respons kosong")} value={metrics.missingResponse} tone={metrics.missingResponse ? "danger" : "ok"} />
        <TraceabilityMetric label={L("Missing evidence", "Evidence kosong")} value={metrics.missingEvidence} tone={metrics.missingEvidence ? "warning" : "ok"} />
        <TraceabilityMetric label={L("Open actions", "Action open")} value={metrics.openActions} tone={metrics.openActions ? "warning" : "ok"} />
        <TraceabilityMetric label={L("Compliance gaps", "Gap compliance")} value={metrics.complianceGap} tone={metrics.complianceGap ? "danger" : "ok"} />
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
                <tr key={req.id} className={row.gaps.length ? "hasGap" : "complete"}>
                  <td className="traceabilityRequirementCell">
                    <strong>#{req.id} · {req.category || "-"}</strong>
                    <span>{shortText(req.requirement_text)}</span>
                    <small>Owner: {req.suggested_owner || "-"} · Status: {req.status || "-"}</small>
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
                          <span className={`traceabilityGapPill ${gap}`} key={`${req.id}-${gap}`}>{gap.replaceAll("_", " ")}</span>
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
