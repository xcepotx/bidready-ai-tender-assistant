import { apiFetch } from "../api/client.js";

export function useTenderBulkUpdates({
  selectedProjectId,
  setBusy,
  setMessage,
  loadProjectData,
}) {
  async function bulkUpdateRequirements(requirementIds, patch) {
    if (!selectedProjectId || requirementIds.length === 0) return;

    setBusy(true);
    setMessage("");

    try {
      await apiFetch("/api/v1/requirements/bulk-update", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify({
          requirement_ids: requirementIds,
          ...patch,
        }),
      });

      await loadProjectData(selectedProjectId);
      setMessage(`Bulk updated ${requirementIds.length} requirement(s).`);
    } catch (err) {
      setMessage(`Bulk requirement update failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function bulkUpdateClarifications(questionIds, patch) {
    if (!selectedProjectId || questionIds.length === 0) return;

    setBusy(true);
    setMessage("");

    try {
      await apiFetch("/api/v1/clarifications/bulk-update", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify({
          question_ids: questionIds,
          ...patch,
        }),
      });

      await loadProjectData(selectedProjectId);
      setMessage(`Bulk updated ${questionIds.length} clarification question(s).`);
    } catch (err) {
      setMessage(`Bulk clarification update failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    bulkUpdateRequirements,
    bulkUpdateClarifications,
  };
}
