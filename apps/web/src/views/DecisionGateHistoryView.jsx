import { useState } from "react";

export default function DecisionGateHistoryView({ decisionGateHistory = { summary: null, events: [] } }) {
  const [eventFilter, setEventFilter] = useState("all");

  const summary = decisionGateHistory?.summary || {};
  const events = Array.isArray(decisionGateHistory?.events) ? decisionGateHistory.events : [];

  const filteredEvents = events.filter((event) => {
    if (eventFilter === "all") return true;
    return event.event_type === eventFilter;
  });

  return (
    <div className="workspaceView gateHistoryView">
      <div className="viewHeader gateHistoryHeader">
        <div>
          <p className="eyebrow">Decision Gate Approval History</p>
          <h2>Decision and approval timeline</h2>
          <p className="muted">
            Read-only timeline built from audit logs for decision gate changes and approval workflow actions.
          </p>
        </div>
      </div>

      <div className="gateHistorySummary">
        <div className="gateHistoryStatusCard">
          <span>Decision Status</span>
          <strong>{summary.latest_decision_status || "-"}</strong>
          <p>{summary.latest_recommendation || "No recommendation available."}</p>
        </div>

        <div className="gateHistoryStatusCard">
          <span>Approval Status</span>
          <strong>{summary.latest_approval_status || "-"}</strong>
          <p>
            Approved {summary.approved_steps ?? 0}, pending {summary.pending_steps ?? 0}, changes {summary.changes_requested_steps ?? 0}, rejected {summary.rejected_steps ?? 0}.
          </p>
        </div>

        <div className="gateHistoryStatusCard">
          <span>Readiness Score</span>
          <strong>{summary.readiness_score ?? 0}</strong>
          <p>Last actor: {summary.last_actor || "-"}.</p>
        </div>
      </div>

      <div className="actionStatGrid gateHistoryStats">
        <ComplianceMetric label="Total Events" value={summary.total_events ?? events.length} />
        <ComplianceMetric label="Decision Events" value={summary.decision_events ?? 0} />
        <ComplianceMetric label="Approval Events" value={summary.approval_events ?? 0} />
      </div>

      <div className="actionFilterBar gateHistoryFilterBar">
        <label>
          Event Type
          <select value={eventFilter} onChange={(e) => setEventFilter(e.target.value)}>
            <option value="all">All events</option>
            <option value="decision_gate">Decision gate</option>
            <option value="approval_workflow">Approval workflow</option>
            <option value="approval_step">Approval step</option>
          </select>
        </label>
      </div>

      {filteredEvents.length === 0 ? (
        <div className="sectionBox actionEmptyState">
          <h3>No history yet</h3>
          <p className="muted">Generate a decision gate or approval workflow to populate this timeline.</p>
        </div>
      ) : (
        <div className="gateTimeline">
          {filteredEvents.map((event) => (
            <article key={event.id} className={`gateTimelineCard ${event.event_type}`}>
              <div className="gateTimelineDot" />
              <div className="gateTimelineBody">
                <div className="gateTimelineTop">
                  <div>
                    <span className="sourcePill">{event.event_type}</span>
                    <span className="sourcePill">{event.action}</span>
                  </div>
                  <time>{event.created_at ? new Date(event.created_at).toLocaleString() : "-"}</time>
                </div>

                <h3>{event.title}</h3>
                {event.summary && <p>{event.summary}</p>}

                <div className="actionItemMetaGrid">
                  <div>
                    <span>Actor</span>
                    <strong>{event.actor || "-"}</strong>
                  </div>
                  <div>
                    <span>Status</span>
                    <strong>{event.status_from || "-"} → {event.status_to || "-"}</strong>
                  </div>
                  <div>
                    <span>Score / Step</span>
                    <strong>{event.score_from ?? "-"} → {event.score_to ?? "-"}</strong>
                  </div>
                  <div>
                    <span>Target</span>
                    <strong>{event.target || "-"}</strong>
                  </div>
                </div>

                {event.changed_fields?.length > 0 && (
                  <div className="gateChangedFields">
                    {event.changed_fields.map((field) => (
                      <span key={field}>{field}</span>
                    ))}
                  </div>
                )}

                {event.details?.decision_note && (
                  <p className="approvalDecisionMeta">
                    Note: {event.details.decision_note}
                  </p>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
