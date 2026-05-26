import { L } from "../utils/i18n.js";

const STEP_LABELS = {
  rfp_uploaded: ["RFP Uploaded", "RFP Diunggah"],
  requirements_analyzed: ["Requirements Analyzed", "Requirement Dianalisis"],
  readiness_review: ["Readiness Review", "Review Kesiapan"],
  clarifications: ["Clarifications", "Klarifikasi"],
  response_plan: ["Response Plan", "Rencana Respons"],
  proposal_outline: ["Proposal Outline", "Outline Proposal"],
  evidence_pack: ["Evidence Pack", "Paket Evidence"],
  compliance_scorecard: ["Compliance Scorecard", "Scorecard Kepatuhan"],
  risk_register: ["Risk Register", "Risk Register"],
  action_tracker: ["Action Tracker", "Action Tracker"],
  approval_workflow: ["Approval Workflow", "Alur Approval"],
};

function stepLabel(step) {
  const labels = STEP_LABELS[step?.key];
  if (!labels) return step?.label || "-";
  return L(labels[0], labels[1]);
}

function statusLabel(status) {
  if (status === "done") return L("Done", "Selesai");
  if (status === "pending") return L("Pending", "Pending");
  if (status === "optional") return L("Optional", "Opsional");
  return status || "-";
}

export default function WorkflowStatusCard({ workflowStatus }) {
  if (!workflowStatus) {
    return (
      <div className="summaryPanel workflowStatusCard">
        <div className="workflowHeader">
          <div>
            <p className="eyebrow dark">{L("Bid Workflow", "Alur Bid")}</p>
            <h3>{L("Project progress unavailable", "Progress project belum tersedia")}</h3>
          </div>
        </div>
        <p className="muted">
          {L(
            "Select a project or refresh project data to load workflow status.",
            "Pilih project atau refresh data project untuk memuat status alur kerja."
          )}
        </p>
      </div>
    );
  }

  const progress = Number.isFinite(Number(workflowStatus.overall_progress))
    ? Math.max(0, Math.min(100, Number(workflowStatus.overall_progress)))
    : 0;

  const steps = Array.isArray(workflowStatus.steps) ? workflowStatus.steps : [];
  const nextActions = Array.isArray(workflowStatus.next_actions) ? workflowStatus.next_actions : [];

  return (
    <div className="summaryPanel workflowStatusCard">
      <div className="workflowHeader">
        <div>
          <p className="eyebrow dark">{L("Bid Workflow", "Alur Bid")}</p>
          <h3>{L("Project Progress", "Progress Project")}</h3>
          <p className="muted">
            {L("Current stage", "Tahap saat ini")}: <strong>{workflowStatus.current_stage || "-"}</strong>
          </p>
        </div>

        <div className="workflowProgressBadge">
          <strong>{progress}%</strong>
          <span>{L("complete", "selesai")}</span>
        </div>
      </div>

      <div className="workflowProgressTrack" aria-label="Workflow progress">
        <div className="workflowProgressFill" style={{ width: `${progress}%` }} />
      </div>

      <div className="workflowStepGrid">
        {steps.map((step) => (
          <div className={`workflowStep workflowStep-${step.status || "unknown"}`} key={step.key}>
            <span className="workflowStepDot" />
            <div>
              <strong>{stepLabel(step)}</strong>
              <small>
                {statusLabel(step.status)} · {step.count ?? 0}
              </small>
            </div>
          </div>
        ))}
      </div>

      <div className="workflowNextActions">
        <h4>{L("Recommended next actions", "Rekomendasi aksi berikutnya")}</h4>
        {nextActions.length > 0 ? (
          <ol>
            {nextActions.slice(0, 5).map((action, index) => (
              <li key={`${action}-${index}`}>{action}</li>
            ))}
          </ol>
        ) : (
          <p className="muted">{L("No pending recommendation.", "Tidak ada rekomendasi pending.")}</p>
        )}
      </div>
    </div>
  );
}
