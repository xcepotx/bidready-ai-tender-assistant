import { apiFetch } from "../api/client.js";

export function useTenderSimpleUpdates({
  selectedProjectId,
  setBusy,
  setMessage,
  setSelectedRequirementId,
  setSelectedClarificationId,
  loadProjectData,
}) {
  async function updateRequirement(requirementId, patch) {
    if (!selectedProjectId) return;

    setBusy(true);
    setMessage("");

    try {
      await apiFetch(`/api/v1/requirements/${requirementId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify(patch),
      });

      await loadProjectData(selectedProjectId);
      setSelectedRequirementId(requirementId);
      setMessage(`Requirement #${requirementId} updated.`);
    } catch (err) {
      setMessage(`Update failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function updateClarification(questionId, patch) {
    if (!selectedProjectId) return;

    setBusy(true);
    setMessage("");

    try {
      await apiFetch(`/api/v1/clarifications/${questionId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify(patch),
      });

      await loadProjectData(selectedProjectId);
      setSelectedClarificationId(questionId);
      setMessage(`Clarification question #${questionId} updated.`);
    } catch (err) {
      setMessage(`Clarification update failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    updateRequirement,
    updateClarification,
  };
}
