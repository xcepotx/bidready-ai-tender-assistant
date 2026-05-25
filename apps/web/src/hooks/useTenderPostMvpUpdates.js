import { apiFetch } from "../api/client.js";

export function useTenderPostMvpUpdates({
  selectedProjectId,
  actorName,
  setBusy,
  setMessage,
  setClarificationTracker,
  setAddendumImpacts,
  setApprovalWorkflow,
  loadProjectData,
}) {
  async function updateClarificationResponseItem(itemId, patch) {
    setBusy(true);
    setMessage("");

    try {
      const updated = await apiFetch(`/api/v1/clarification-response-items/${itemId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify(patch),
      });

      setClarificationTracker((current) => ({
        ...(current || {}),
        items: (current?.items || []).map((item) => (item.id === updated.id ? updated : item)),
      }));

      setMessage("Clarification response item updated.");
    } catch (err) {
      setMessage(`Update clarification response item failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function updateAddendumImpactItem(itemId, patch) {
    setBusy(true);
    setMessage("");

    try {
      const updated = await apiFetch(`/api/v1/addendum-impact-items/${itemId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify(patch),
      });

      setAddendumImpacts((current) => ({
        ...(current || {}),
        items: (current?.items || []).map((item) => (item.id === updated.id ? updated : item)),
      }));

      setMessage("Addendum impact item updated.");
    } catch (err) {
      setMessage(`Update addendum impact item failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function updateApprovalStep(stepId, patch) {
    setBusy(true);
    setMessage("");

    try {
      const updated = await apiFetch(`/api/v1/approval-steps/${stepId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify({
          decided_by: actorName,
          ...patch,
        }),
      });

      setApprovalWorkflow((current) => ({
        ...(current || {}),
        steps: (current?.steps || []).map((item) => (item.id === updated.id ? updated : item)),
      }));

      await loadProjectData(selectedProjectId);
      setMessage("Approval step updated.");
    } catch (err) {
      setMessage(`Update approval step failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    updateClarificationResponseItem,
    updateAddendumImpactItem,
    updateApprovalStep,
  };
}
