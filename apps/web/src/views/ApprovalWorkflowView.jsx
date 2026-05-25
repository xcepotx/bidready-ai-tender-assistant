import ComplianceMetric from "../components/ComplianceMetric.jsx";
export default function ApprovalWorkflowView({
  approvalWorkflow = { summary: null, request: null, steps: [] },
  busy,
  actorName,
  generateApprovalWorkflow,
  submitApprovalWorkflow,
  updateApprovalStep,
}) {
  const summary = approvalWorkflow?.summary || {};
  const request = approvalWorkflow?.request || null;
  const steps = Array.isArray(approvalWorkflow?.steps) ? approvalWorkflow.steps : [];

  const statusCounts = steps.reduce((acc, step) => {
    acc[step.status] = (acc[step.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="workspaceView approvalWorkflowView">
      <div className="viewHeader approvalHeader">
        <div>
          <p className="eyebrow">Approval Workflow</p>
          <h2>Bid approval routing and sign-off</h2>
          <p className="muted">
            Generate approval steps from decision gate, compliance scorecard, risk register, and action tracker.
          </p>
        </div>

        <div className="approvalHeaderActions">
          <button
            type="button"
            className="regenerateAllButton"
            disabled={busy}
            onClick={generateApprovalWorkflow}
          >
            Generate Workflow
          </button>

          <button
            type="button"
            className="secondaryButton"
            disabled={busy || !request?.id || request?.status !== "draft"}
            onClick={() => submitApprovalWorkflow(request?.id)}
          >
            Submit for Approval
          </button>
        </div>
      </div>

      <div className="approvalSummaryHero">
        <div className="approvalProgressRing">
          <strong>{summary.progress_percent ?? 0}%</strong>
          <span>Approved</span>
        </div>

        <div className="approvalSummaryCopy">
          <h3>{request?.title || "No approval workflow generated yet"}</h3>
          <p className="muted">
            {request?.description || "Generate an approval workflow after compliance, risks, and decision gate are ready."}
          </p>
          <div className={`approvalStatusPill ${request?.status || "not_generated"}`}>
            {request?.status || "not_generated"}
          </div>
        </div>
      </div>

      <div className="actionStatGrid approvalStatGrid">
        <ComplianceMetric label="Total Steps" value={summary.total_steps ?? steps.length} />
        <ComplianceMetric label="Pending" value={summary.pending_steps ?? statusCounts.pending ?? 0} tone="warning" />
        <ComplianceMetric label="Approved" value={summary.approved_steps ?? statusCounts.approved ?? 0} />
        <ComplianceMetric label="Changes" value={summary.changes_requested_steps ?? statusCounts.changes_requested ?? 0} tone="warning" />
        <ComplianceMetric label="Rejected" value={summary.rejected_steps ?? statusCounts.rejected ?? 0} tone="danger" />
      </div>

      {steps.length === 0 ? (
        <div className="sectionBox actionEmptyState">
          <h3>No approval steps yet</h3>
          <p className="muted">Generate the approval workflow after the decision gate and scorecards are available.</p>
        </div>
      ) : (
        <div className="approvalStepTimeline">
          {steps.map((step) => (
            <article key={step.id} className={`approvalStepCard ${step.status}`}>
              <div className="approvalStepOrder">{step.step_order}</div>

              <div className="approvalStepBody">
                <div className="approvalStepTop">
                  <div>
                    <span className={`approvalStatusPill ${step.status}`}>{step.status}</span>
                    <span className="sourcePill">{step.role}</span>
                  </div>

                  <strong>{step.approver_name || step.role}</strong>
                </div>

                <div className="approvalInlineGrid">
                  <label>
                    Approver
                    <input
                      className="tableInput"
                      defaultValue={step.approver_name || ""}
                      disabled={busy}
                      onBlur={(e) => {
                        if (e.target.value !== (step.approver_name || "")) {
                          updateApprovalStep(step.id, { approver_name: e.target.value });
                        }
                      }}
                    />
                  </label>

                  <label>
                    Email
                    <input
                      className="tableInput"
                      defaultValue={step.approver_email || ""}
                      disabled={busy}
                      onBlur={(e) => {
                        if (e.target.value !== (step.approver_email || "")) {
                          updateApprovalStep(step.id, { approver_email: e.target.value });
                        }
                      }}
                    />
                  </label>

                  <label>
                    Due Date
                    <input
                      className="tableInput"
                      defaultValue={step.due_date || ""}
                      disabled={busy}
                      onBlur={(e) => {
                        if (e.target.value !== (step.due_date || "")) {
                          updateApprovalStep(step.id, { due_date: e.target.value });
                        }
                      }}
                    />
                  </label>
                </div>

                <label className="approvalDecisionNote">
                  Decision Note
                  <textarea
                    className="tableTextarea"
                    defaultValue={step.decision_note || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (step.decision_note || "")) {
                        updateApprovalStep(step.id, { decision_note: e.target.value });
                      }
                    }}
                  />
                </label>

                <div className="approvalQuickControls">
                  <button type="button" disabled={busy} onClick={() => updateApprovalStep(step.id, { status: "pending" })}>
                    Mark Pending
                  </button>
                  <button type="button" disabled={busy} onClick={() => updateApprovalStep(step.id, { status: "approved", decision_note: step.decision_note || `Approved by ${actorName}` })}>
                    Approve
                  </button>
                  <button type="button" disabled={busy} onClick={() => updateApprovalStep(step.id, { status: "changes_requested", decision_note: step.decision_note || "Changes requested" })}>
                    Request Changes
                  </button>
                  <button type="button" disabled={busy} onClick={() => updateApprovalStep(step.id, { status: "rejected", decision_note: step.decision_note || "Rejected" })}>
                    Reject
                  </button>
                </div>

                {step.decided_at && (
                  <p className="approvalDecisionMeta">
                    Decided by {step.decided_by || "-"} at {new Date(step.decided_at).toLocaleString()}
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
