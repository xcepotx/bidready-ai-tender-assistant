import { apiFetch } from "../api/client.js";

export function useTenderPostMvpGenerators({
  selectedProjectId,
  actorName,
  setBusy,
  setMessage,
  setActiveProjectView,
  setClarificationTracker,
  setAddendumImpacts,
  setApprovalWorkflow,
}) {
  async function generateClarificationResponseTracker() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    setBusy(true);
    setMessage("Generating clarification response tracker...");

    try {
      const result = await apiFetch(`/api/v1/projects/${selectedProjectId}/generate-clarification-response-tracker`, {
        method: "POST",
        headers: {
          "X-Actor": actorName,
        },
      });

      setClarificationTracker({
        summary: result.summary || null,
        items: result.items || [],
      });
      setActiveProjectView("clarificationTracker");
      setMessage(`Generated ${result.generated_count || 0} clarification response item(s).`);
    } catch (err) {
      setMessage(`Generate clarification response tracker failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function generateAddendumImpactAnalysis() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    setBusy(true);
    setMessage("Generating addendum impact analysis...");

    try {
      const result = await apiFetch(`/api/v1/projects/${selectedProjectId}/generate-addendum-impact-analysis`, {
        method: "POST",
        headers: {
          "X-Actor": actorName,
        },
      });

      setAddendumImpacts({
        summary: result.summary || null,
        items: result.items || [],
      });
      setActiveProjectView("addendum");
      setMessage(`Generated ${result.generated_count || 0} addendum impact item(s).`);
    } catch (err) {
      setMessage(`Generate addendum impact analysis failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function generateApprovalWorkflow() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    setBusy(true);
    setMessage("Generating approval workflow...");

    try {
      const result = await apiFetch(`/api/v1/projects/${selectedProjectId}/generate-approval-workflow`, {
        method: "POST",
        headers: {
          "X-Actor": actorName,
        },
      });

      setApprovalWorkflow(result || { summary: null, request: null, steps: [] });
      setActiveProjectView("approvals");
      setMessage("Approval workflow generated.");
    } catch (err) {
      setMessage(`Generate approval workflow failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    generateClarificationResponseTracker,
    generateAddendumImpactAnalysis,
    generateApprovalWorkflow,
  };
}
