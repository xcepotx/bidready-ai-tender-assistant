import { L } from "../utils/i18n.js";
import { useState, useMemo } from "react";
import ComplianceMetric from "../components/ComplianceMetric.jsx";
import ComplianceRelationBox from "../components/ComplianceRelationBox.jsx";
export default function ClarificationResponseTrackerView({
  clarificationTracker = { summary: null, items: [] },
  busy,
  generateClarificationResponseTracker,
  updateClarificationResponseItem,
}) {
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [ownerFilter, setOwnerFilter] = useState("all");

  const summary = clarificationTracker?.summary || {};
  const safeItems = Array.isArray(clarificationTracker?.items) ? clarificationTracker.items : [];

  const owners = useMemo(
    () => Array.from(new Set(safeItems.map((item) => item.owner).filter(Boolean))).sort(),
    [safeItems]
  );

  const statusRank = { overdue: 0, open: 1, sent: 2, answered: 3, incorporated: 4, closed: 5 };
  const priorityRank = { high: 0, medium: 1, low: 2 };

  const filteredItems = safeItems
    .filter((item) => {
      if (statusFilter !== "all" && item.response_status !== statusFilter) return false;
      if (priorityFilter !== "all" && item.priority !== priorityFilter) return false;
      if (ownerFilter !== "all" && item.owner !== ownerFilter) return false;
      return true;
    })
    .sort((a, b) => {
      const statusDiff = (statusRank[a.response_status] ?? 9) - (statusRank[b.response_status] ?? 9);
      if (statusDiff !== 0) return statusDiff;
      return (priorityRank[a.priority] ?? 1) - (priorityRank[b.priority] ?? 1);
    });

  const statusCounts = summary.status_counts || {};

  return (
    <div className="workspaceView clarificationTrackerView">
      <div className="viewHeader clarificationTrackerHeader">
        <div>
          <p className="eyebrow">Clarification Response Tracker</p>
          <h2>Client response lifecycle tracker</h2>
          <p className="muted">
            Track clarification answers, follow-ups, owner accountability, and downstream artifact impact.
          </p>
        </div>

        <button
          type="button"
          className="regenerateAllButton"
          disabled={busy}
          onClick={generateClarificationResponseTracker}
        >
          Generate Tracker
        </button>
      </div>

      <div className="clarificationTrackerHero">
        <div className="clarificationProgressCard">
          <strong>{summary.completion_percent ?? 0}%</strong>
          <span>Completion</span>
          <p>{summary.recommendation || "Generate tracker after clarification questions are available."}</p>
        </div>

        <div className="clarificationProgressCard warning">
          <strong>{summary.open_items ?? 0}</strong>
          <span>Open Items</span>
          <p>High priority: {summary.high_priority_items ?? 0}. High risk: {summary.high_risk_items ?? 0}.</p>
        </div>
      </div>

      <div className="actionStatGrid clarificationTrackerStats">
        <ComplianceMetric label="Total" value={summary.total_items ?? safeItems.length} />
        <ComplianceMetric label="Open" value={statusCounts.open || 0} tone="warning" />
        <ComplianceMetric label="Sent" value={statusCounts.sent || 0} />
        <ComplianceMetric label="Answered" value={statusCounts.answered || 0} />
        <ComplianceMetric label="Incorporated" value={statusCounts.incorporated || 0} />
        <ComplianceMetric label="Overdue" value={statusCounts.overdue || 0} tone="danger" />
      </div>

      <div className="actionFilterBar clarificationTrackerFilterBar">
        <label>
          Status
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="all">{L("All statuses", "Semua status")}</option>
            <option value="open">Open</option>
            <option value="sent">Sent</option>
            <option value="answered">Answered</option>
            <option value="incorporated">Incorporated</option>
            <option value="closed">Closed</option>
            <option value="overdue">Overdue</option>
          </select>
        </label>

        <label>
          Priority
          <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
            <option value="all">All priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </label>

        <label>
          Owner
          <select value={ownerFilter} onChange={(e) => setOwnerFilter(e.target.value)}>
            <option value="all">All owners</option>
            {owners.map((owner) => (
              <option key={owner} value={owner}>{owner}</option>
            ))}
          </select>
        </label>
      </div>

      <p className="actionTrackerMeta">
        Showing {filteredItems.length} of {safeItems.length} clarification response item(s).
      </p>

      {filteredItems.length === 0 ? (
        <div className="sectionBox actionEmptyState">
          <h3>No clarification response tracker yet</h3>
          <p className="muted">Generate tracker after clarification questions are available.</p>
        </div>
      ) : (
        <div className="clarificationTrackerList">
          {filteredItems.map((item) => (
            <article key={item.id} className={`clarificationTrackerCard ${item.response_status}`}>
              <div className="clarificationTrackerTop">
                <div>
                  <span className={`clarificationStatusPill ${item.response_status}`}>{item.response_status}</span>
                  <span className={`priorityPill ${item.priority}`}>{item.priority}</span>
                  <span className="sourcePill">{item.category}</span>
                </div>

                <select
                  value={item.response_status || "open"}
                  disabled={busy}
                  onChange={(e) => updateClarificationResponseItem(item.id, { response_status: e.target.value })}
                >
                  <option value="open">Open</option>
                  <option value="sent">Sent</option>
                  <option value="answered">Answered</option>
                  <option value="incorporated">Incorporated</option>
                  <option value="closed">Closed</option>
                  <option value="overdue">Overdue</option>
                </select>
              </div>

              <h3>Clarification #{item.clarification_id || "-"}</h3>
              <p>{item.question_text}</p>

              <div className="actionItemMetaGrid">
                <div>
                  <span>Owner</span>
                  <strong>{item.owner || "Unassigned"}</strong>
                </div>
                <div>
                  <span>Due Date</span>
                  <strong>{item.due_date || "-"}</strong>
                </div>
                <div>
                  <span>Risk</span>
                  <strong>{item.risk_level}</strong>
                </div>
                <div>
                  <span>Impacts</span>
                  <strong>{(item.impacted_artifacts || []).join(", ") || "-"}</strong>
                </div>
              </div>

              <div className="clarificationInlineGrid">
                <label>
                  Owner
                  <input
                    className="tableInput"
                    defaultValue={item.owner || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.owner || "")) {
                        updateClarificationResponseItem(item.id, { owner: e.target.value });
                      }
                    }}
                  />
                </label>

                <label>
                  Due Date
                  <input
                    className="tableInput"
                    defaultValue={item.due_date || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.due_date || "")) {
                        updateClarificationResponseItem(item.id, { due_date: e.target.value });
                      }
                    }}
                  />
                </label>

                <label>
                  Sent At
                  <input
                    className="tableInput"
                    defaultValue={item.sent_at || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.sent_at || "")) {
                        updateClarificationResponseItem(item.id, { sent_at: e.target.value });
                      }
                    }}
                  />
                </label>
              </div>

              <div className="riskPlanGrid">
                <label>
                  Client Response
                  <textarea
                    className="tableTextarea"
                    defaultValue={item.client_response || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.client_response || "")) {
                        updateClarificationResponseItem(item.id, { client_response: e.target.value });
                      }
                    }}
                  />
                </label>

                <label>
                  Recommended Follow-up
                  <textarea
                    className="tableTextarea"
                    defaultValue={item.recommended_follow_up || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.recommended_follow_up || "")) {
                        updateClarificationResponseItem(item.id, { recommended_follow_up: e.target.value });
                      }
                    }}
                  />
                </label>
              </div>

              <div className="evidenceRelationGrid">
                <ComplianceRelationBox title="Response IDs" values={item.related_response_item_ids || []} />
                <ComplianceRelationBox title="Compliance IDs" values={item.related_compliance_item_ids || []} />
                <ComplianceRelationBox title="Risk IDs" values={item.related_risk_item_ids || []} />
                <ComplianceRelationBox title="Addendum IDs" values={item.related_addendum_impact_ids || []} />
              </div>

              <div className="actionQuickControls">
                <button type="button" disabled={busy} onClick={() => updateClarificationResponseItem(item.id, { response_status: "sent" })}>
                  Mark Sent
                </button>
                <button type="button" disabled={busy} onClick={() => updateClarificationResponseItem(item.id, { response_status: "answered" })}>
                  Mark Answered
                </button>
                <button type="button" disabled={busy} onClick={() => updateClarificationResponseItem(item.id, { response_status: "incorporated" })}>
                  Mark Incorporated
                </button>
                <button type="button" disabled={busy} onClick={() => updateClarificationResponseItem(item.id, { response_status: "closed" })}>
                  Close
                </button>
                <button type="button" disabled={busy} onClick={() => updateClarificationResponseItem(item.id, { response_status: "overdue" })}>
                  Mark Overdue
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
