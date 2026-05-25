import { downloadApiFile } from "../api/client.js";

export function useTenderDownloads({
  selectedProjectId,
  requirements,
  proposalOutline,
  setBusy,
  setMessage,
}) {
  async function downloadReadinessMatrix() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    if (requirements.length === 0) {
      setMessage("Analyze RFP first before exporting the readiness matrix.");
      return;
    }

    setBusy(true);
    setMessage("");

    try {
        await downloadApiFile(
          `/api/v1/projects/${selectedProjectId}/exports/checklist.xlsx`,
          `bidready_ai_tender_report_project_${selectedProjectId}.xlsx`
        );

      setMessage("Readiness matrix exported.");
    } catch (err) {
      setMessage(`Export failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function downloadProposalDraft() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    if (proposalOutline.length === 0) {
      setMessage("Generate proposal outline first before exporting proposal draft.");
      return;
    }

    setBusy(true);
    setMessage("");

    try {
        await downloadApiFile(
          `/api/v1/projects/${selectedProjectId}/exports/proposal-draft.docx`,
          `bidready_ai_proposal_draft_project_${selectedProjectId}.docx`
        );

      setMessage("Proposal draft exported.");
    } catch (err) {
      setMessage(`Proposal draft export failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function downloadExecutivePack() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    setBusy(true);
    setMessage("Preparing executive pack export...");

    try {
      await downloadApiFile(
        `/api/v1/projects/${selectedProjectId}/exports/executive-pack.zip`,
        `bidready_ai_executive_pack_project_${selectedProjectId}.zip`
      );
      setMessage("Executive pack export downloaded.");
    } catch (err) {
      setMessage(`Executive pack export failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    downloadReadinessMatrix,
    downloadProposalDraft,
    downloadExecutivePack,
  };
}
