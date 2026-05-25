import { apiFetch } from "../api/client.js";

export function useTenderItemUpdates({
  selectedProjectId,
  setBusy,
  setMessage,
  setSelectedResponseItemId,
  setSelectedProposalSectionId,
  setSelectedEvidenceItemId,
  loadProjectData,
}) {
  async function updateResponseItem(itemId, patch) {
    if (!selectedProjectId) return;

    setBusy(true);
    setMessage("");

    try {
      await apiFetch(`/api/v1/response-items/${itemId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify(patch),
      });

      await loadProjectData(selectedProjectId);
      setSelectedResponseItemId(itemId);
      setMessage(`Response item #${itemId} updated.`);
    } catch (err) {
      setMessage(`Response item update failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function updateProposalSection(sectionId, patch) {
    if (!selectedProjectId) return;

    setBusy(true);
    setMessage("");

    try {
      await apiFetch(`/api/v1/proposal-sections/${sectionId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify(patch),
      });

      await loadProjectData(selectedProjectId);
      setSelectedProposalSectionId(sectionId);
      setMessage(`Proposal section #${sectionId} updated.`);
    } catch (err) {
      setMessage(`Proposal section update failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function updateEvidenceItem(itemId, patch) {
    if (!selectedProjectId) return;

    setBusy(true);
    setMessage("");

    try {
      await apiFetch(`/api/v1/evidence-items/${itemId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify(patch),
      });

      await loadProjectData(selectedProjectId);
      setSelectedEvidenceItemId(itemId);
      setMessage(`Evidence item #${itemId} updated.`);
    } catch (err) {
      setMessage(`Evidence item update failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    updateResponseItem,
    updateProposalSection,
    updateEvidenceItem,
  };
}
