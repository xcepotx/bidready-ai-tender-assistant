import { apiFetch } from "../api/client.js";

export function useTenderApprovalDecision({
  selectedProjectId,
  actorName,
  setBusy,
  setMessage,
  setApprovalWorkflow,
  setDecisionGate,
  setActiveProjectView,
  loadProjectData,
}) {
  async function submitApprovalWorkflow(workflowId) {
    if (!workflowId) {
      setMessage("Generate approval workflow first.");
      return;
    }

    setBusy(true);
    setMessage("Submitting approval workflow...");

    try {
      const result = await apiFetch(`/api/v1/approval-workflows/${workflowId}/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify({
          submitted_by: actorName,
        }),
      });

      setApprovalWorkflow(result || { summary: null, request: null, steps: [] });
      setMessage("Approval workflow submitted.");
    } catch (err) {
      setMessage(`Submit approval workflow failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function updateDecisionGate(gateId, patch) {
    if (!selectedProjectId || !gateId) return;

    setBusy(true);
    setMessage("");

    try {
      const updated = await apiFetch(`/api/v1/decision-gates/${gateId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify(patch),
      });

      setDecisionGate(updated);
      await loadProjectData(selectedProjectId);
      setMessage(`Decision gate #${gateId} updated.`);
    } catch (err) {
      setMessage(`Decision gate update failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    submitApprovalWorkflow,
    updateDecisionGate,
  };
}
