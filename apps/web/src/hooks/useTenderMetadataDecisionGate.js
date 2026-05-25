import { apiFetch } from "../api/client.js";

export function useTenderMetadataDecisionGate({
  selectedProjectId,
  documents,
  actorName,
  setBusy,
  setMessage,
  setProjectMetadata,
  setDecisionGate,
  setActiveProjectView,
  loadProjectData,
}) {
  async function extractMetadata() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    if (documents.length === 0) {
      setMessage("Upload and parse an RFP document first before extracting metadata.");
      return;
    }

    setBusy(true);
    setMessage("");

    try {
      const metadata = await apiFetch(`/api/v1/projects/${selectedProjectId}/extract-metadata`, {
        method: "POST",
        headers: {
          "X-Actor": actorName,
        },
      });

      await loadProjectData(selectedProjectId);
      setProjectMetadata(metadata);
      setMessage("RFP metadata extracted.");
    } catch (err) {
      setMessage(`Metadata extraction failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function generateDecisionGate() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    setBusy(true);
    setMessage("Generating decision gate...");

    try {
      const result = await apiFetch(`/api/v1/projects/${selectedProjectId}/generate-decision-gate`, {
        method: "POST",
        headers: {
          "X-Actor": actorName,
        },
      });

      setDecisionGate(result.gate || null);
      await loadProjectData(selectedProjectId);
      setActiveProjectView("summary");
      setMessage(`Decision gate generated for project #${selectedProjectId}.`);
    } catch (err) {
      setMessage(`Generate decision gate failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    extractMetadata,
    generateDecisionGate,
  };
}
