import { L } from "../utils/i18n.js";
import { useState, useMemo } from "react";
import ComplianceMetric from "../components/ComplianceMetric.jsx";
import ComplianceRelationBox from "../components/ComplianceRelationBox.jsx";
export default function AddendumImpactView({
  addendumImpacts = { summary: null, items: [] },
  busy,
  generateAddendumImpactAnalysis,
  updateAddendumImpactItem,
}) {
  const [severityFilter, setSeverityFilter] = useState("all");
  const [artifactFilter, setArtifactFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const summary = addendumImpacts?.summary || {};
  const safeItems = Array.isArray(addendumImpacts?.items) ? addendumImpacts.items : [];

  const artifacts = useMemo(
    () => Array.from(new Set(safeItems.map((item) => item.impacted_artifact).filter(Boolean))).sort(),
    [safeItems]
  );

  const severityRank = { critical: 0, high: 1, medium: 2, low: 3 };

  const filteredItems = safeItems
    .filter((item) => {
      if (severityFilter !== "all" && item.severity !== severityFilter) return false;
      if (artifactFilter !== "all" && item.impacted_artifact !== artifactFilter) return false;
      if (statusFilter !== "all" && item.status !== statusFilter) return false;
      return true;
    })
    .sort((a, b) => (severityRank[a.severity] ?? 2) - (severityRank[b.severity] ?? 2));

  const severityCounts = summary.severity_counts || {};
  const statusCounts = summary.status_counts || {};

  return (
    <div className="workspaceView addendumImpactView">
      <div className="viewHeader addendumHeader">
        <div>
          <p className="eyebrow">Addendum / Document Impact Analysis</p>
          <h2>Document change impact tracker</h2>
          <p className="muted">
            Analyze revised tender documents against requirements, response plan, compliance, risks, and approvals.
          </p>
        </div>

        <button
          type="button"
          className="regenerateAllButton"
          disabled={busy}
          onClick={generateAddendumImpactAnalysis}
        >
          Generate Impact Analysis
        </button>
      </div>

      <div className="addendumHero">
        <div className="addendumHeroCard">
          <span>Total Impacts</span>
          <strong>{summary.total_items ?? safeItems.length}</strong>
          <p>{summary.recommendation || "Generate impact analysis after an addendum or revised document is uploaded."}</p>
        </div>

        <div className="addendumHeroCard warning">
          <span>Critical / High</span>
          <strong>{summary.critical_items ?? 0} / {summary.high_items ?? 0}</strong>
          <p>Open items: {summary.open_items ?? statusCounts.open ?? 0}</p>
        </div>
      </div>

      <div className="actionStatGrid addendumStatGrid">
        <ComplianceMetric label="Critical" value={severityCounts.critical || 0} tone="danger" />
        <ComplianceMetric label="High" value={severityCounts.high || 0} tone="danger" />
        <ComplianceMetric label="Medium" value={severityCounts.medium || 0} tone="warning" />
        <ComplianceMetric label="Low" value={severityCounts.low || 0} />
        <ComplianceMetric label="Resolved" value={statusCounts.resolved || 0} />
      </div>

      <div className="actionFilterBar addendumFilterBar">
        <label>
          Severity
          <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
            <option value="all">All severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </label>

        <label>
          Artifact
          <select value={artifactFilter} onChange={(e) => setArtifactFilter(e.target.value)}>
            <option value="all">All artifacts</option>
            {artifacts.map((artifact) => (
              <option key={artifact} value={artifact}>{artifact}</option>
            ))}
          </select>
        </label>

        <label>
          Status
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="all">{L("All statuses", "Semua status")}</option>
            <option value="open">Open</option>
            <option value="reviewed">Reviewed</option>
            <option value="accepted">Accepted</option>
            <option value="resolved">Resolved</option>
            <option value="rejected">Rejected</option>
          </select>
        </label>
      </div>

      <p className="actionTrackerMeta">
        Showing {filteredItems.length} of {safeItems.length} addendum impact item(s).
      </p>

      {filteredItems.length === 0 ? (
        <div className="sectionBox actionEmptyState">
          <h3>No addendum impacts yet</h3>
          <p className="muted">Generate impact analysis after uploading or selecting a revised tender document.</p>
        </div>
      ) : (
        <div className="addendumImpactList">
          {filteredItems.map((item) => (
            <article key={item.id} className={`addendumImpactCard ${item.severity}`}>
              <div className="addendumImpactTop">
                <div>
                  <span className={`priorityPill ${item.severity}`}>{item.severity}</span>
                  <span className="sourcePill">{item.impacted_artifact}</span>
                  <span className="sourcePill">{item.impact_type}</span>
                </div>

                <select
                  value={item.status || "open"}
                  disabled={busy}
                  onChange={(e) => updateAddendumImpactItem(item.id, { status: e.target.value })}
                >
                  <option value="open">Open</option>
                  <option value="reviewed">Reviewed</option>
                  <option value="accepted">Accepted</option>
                  <option value="resolved">Resolved</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>

              <h3>{item.title}</h3>
              {item.summary && <p>{item.summary}</p>}

              <div className="actionItemMetaGrid">
                <div>
                  <span>Source Document</span>
                  <strong>{item.source_document_name || "-"}</strong>
                </div>
                <div>
                  <span>Owner</span>
                  <strong>{item.owner || "Unassigned"}</strong>
                </div>
                <div>
                  <span>Due Date</span>
                  <strong>{item.due_date || "-"}</strong>
                </div>
                <div>
                  <span>Confidence</span>
                  <strong>{item.confidence ?? "-"}</strong>
                </div>
              </div>

              <div className="riskPlanGrid">
                <label>
                  Recommended Action
                  <textarea
                    className="tableTextarea"
                    defaultValue={item.recommended_action || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.recommended_action || "")) {
                        updateAddendumImpactItem(item.id, { recommended_action: e.target.value });
                      }
                    }}
                  />
                </label>

                <label>
                  Notes
                  <textarea
                    className="tableTextarea"
                    defaultValue={item.notes || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.notes || "")) {
                        updateAddendumImpactItem(item.id, { notes: e.target.value });
                      }
                    }}
                  />
                </label>
              </div>

              {item.source_excerpt && (
                <p className="actionItemNotes">
                  <strong>Source:</strong> {item.source_excerpt}
                </p>
              )}

              <div className="evidenceRelationGrid">
                <ComplianceRelationBox title="Requirement IDs" values={item.related_requirement_ids || []} />
                <ComplianceRelationBox title="Response IDs" values={item.related_response_item_ids || []} />
                <ComplianceRelationBox title="Clarification IDs" values={item.related_clarification_ids || []} />
                <ComplianceRelationBox title="Risk IDs" values={item.related_risk_item_ids || []} />
              </div>

              <div className="actionQuickControls">
                <button type="button" disabled={busy} onClick={() => updateAddendumImpactItem(item.id, { status: "reviewed" })}>
                  Mark Reviewed
                </button>
                <button type="button" disabled={busy} onClick={() => updateAddendumImpactItem(item.id, { status: "accepted" })}>
                  Accept
                </button>
                <button type="button" disabled={busy} onClick={() => updateAddendumImpactItem(item.id, { status: "resolved" })}>
                  Resolve
                </button>
                <button type="button" disabled={busy} onClick={() => updateAddendumImpactItem(item.id, { severity: "critical" })}>
                  Escalate Critical
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
