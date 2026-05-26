import DecisionGateCard from "../components/DecisionGateCard.jsx";
import RfpMetadataCard from "../components/RfpMetadataCard.jsx";
import BidBriefCard from "../components/BidBriefCard.jsx";
import ReadinessSummaryCard from "../components/ReadinessSummaryCard.jsx";
import ExecutiveDashboardCard from "../components/ExecutiveDashboardCard.jsx";
import WorkflowStatusCard from "../components/WorkflowStatusCard.jsx";
import { Upload } from "lucide-react";
export default function SummaryView({
  selectedProject,
  readinessSummary,
  projectMetadata,
  bidBrief,
  workflowStatus,
  responsePlan,
  proposalOutline,
  evidencePack,
  decisionGate,
  documents,
  requirements,
  clarifications,
  auditLogs,
  uploadFile,
  setUploadFile,
  uploadDocument,
  analyzeRfp,
  generateClarifications,
  generateResponsePlan,
  generateProposalOutline,
  generateDecisionGate,
  regenerateAllArtifacts,
  updateDecisionGate,
  extractMetadata,
  busy,
  selectedProjectId,
  downloadReadinessMatrix,
  downloadProposalDraft,
}) {
  const safeEvidencePack = Array.isArray(evidencePack) ? evidencePack : [];

  const safeProposalOutline = Array.isArray(proposalOutline) ? proposalOutline : [];

  const safeResponsePlan = Array.isArray(responsePlan) ? responsePlan : [];

  return (
    <div className="workspaceView">
      <ExecutiveDashboardCard
        readinessSummary={readinessSummary}
        decisionGate={decisionGate}
        requirements={requirements}
        clarifications={clarifications}
        responsePlan={safeResponsePlan}
        proposalOutline={safeProposalOutline}
        evidencePack={safeEvidencePack}
      />

      <WorkflowStatusCard workflowStatus={workflowStatus} />

      <ReadinessSummaryCard summary={readinessSummary} />
<DecisionGateCard
        gate={decisionGate}
        busy={busy}
        generateDecisionGate={generateDecisionGate}
        updateDecisionGate={updateDecisionGate}
      />

      <RfpMetadataCard metadata={projectMetadata} />

      <BidBriefCard bidBrief={bidBrief} />

      <div className="summaryGrid">
        <div className="summaryPanel">
          <h3>Workspace Metrics</h3>
          <div className="readinessMetrics">
            <div>
              <strong>{documents.length}</strong>
              <span>Documents</span>
            </div>
            <div>
              <strong>{requirements.length}</strong>
              <span>Requirements</span>
            </div>
            <div>
              <strong>{clarifications.length}</strong>
              <span>Clarifications</span>
            </div>
            <div>
              <strong>{auditLogs.length}</strong>
              <span>Audit Logs</span>
            </div>
          </div>
        </div>

        <div className="summaryPanel">
          <h3>Actions</h3>

          <form onSubmit={uploadDocument} className="summaryUpload">
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
            />
            <button disabled={busy || !selectedProjectId || !uploadFile} type="submit">
              <Upload size={16} />
              Upload & Parse
            </button>
          </form>

          <div className="summaryActions">
            <button disabled={busy || documents.length === 0} onClick={extractMetadata}>
              Extract Metadata
            </button>

            <button disabled={busy || documents.length === 0} onClick={analyzeRfp}>
              Analyze RFP
            </button>
            <button disabled={busy || requirements.length === 0} onClick={generateClarifications}>
              Generate Clarifications
            </button>

            <button disabled={busy || requirements.length === 0} onClick={generateResponsePlan}>
              Generate Response Plan
            </button>


<button disabled={busy || safeResponsePlan.length === 0} onClick={generateProposalOutline}>
              Generate Proposal Outline
            </button>

            <button type="button" onClick={generateDecisionGate}>
              Generate Decision Gate
            </button>

              <button
                type="button"
                className="regenerateAllButton"
                disabled={busy || requirements.length === 0}
                onClick={regenerateAllArtifacts}
              >
                Regenerate All Artifacts
              </button>
            <button
              type="button"
              className="downloadButton"
              disabled={busy || requirements.length === 0}
              onClick={downloadReadinessMatrix}
            >
              Export Readiness Matrix
            </button>

            <button
              type="button"
              className="downloadButton secondaryDownload"
              disabled={busy || safeProposalOutline.length === 0}
              onClick={downloadProposalDraft}
            >
              Export Proposal Draft
            </button>
          </div>
        </div>
      </div>

      <div className="summaryPanel">
        <h3>Documents</h3>
        <div className="compactDocList">
          {documents.map((doc) => (
            <div className="docChip" key={doc.id}>
              <strong>{doc.filename}</strong>
              <span>
                {doc.page_count} page(s) · {doc.processing_status} · {Math.round(doc.file_size / 1024)} KB
              </span>
            </div>
          ))}
          {documents.length === 0 && <p className="empty">No RFP documents uploaded yet.</p>}
        </div>
      </div>

      {!selectedProject && <p className="empty">Select or create a bid project to start.</p>}
    </div>
  );
}
