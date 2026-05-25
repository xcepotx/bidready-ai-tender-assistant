import { apiFetch } from "../api/client.js";

export function useTenderGenerators({
  selectedProjectId,
  actorName,
  setBusy,
  setMessage,
  setActiveProjectView,
  setSelectedClarificationId,
  setSelectedResponseItemId,
  setSelectedProposalSectionId,
  setSelectedEvidenceItemId,
  loadProjectData,
}) {
  async function generateClarifications() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    if (requirements.length === 0) {
      setMessage("Analyze RFP first before generating clarification questions.");
      return;
    }

    setBusy(true);
    setMessage("");

    try {
      const generated = await apiFetch(`/api/v1/projects/${selectedProjectId}/generate-clarifications`, {
        method: "POST",
        headers: { "X-Actor": actorName },
      });

      await loadProjectData(selectedProjectId);
      if (generated.length > 0) setSelectedClarificationId(generated[0].id);
      setActiveProjectView("clarifications");
      setMessage(`Generated ${generated.length} clarification question(s).`);
    } catch (err) {
      setMessage(`Generate clarification failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function generateResponsePlan() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    if (requirements.length === 0) {
      setMessage("Analyze RFP first before generating response plan.");
      return;
    }

    setBusy(true);
    setMessage("");

    try {
      const result = await apiFetch(`/api/v1/projects/${selectedProjectId}/generate-response-plan`, {
        method: "POST",
        headers: {
          "X-Actor": actorName,
        },
      });

      await loadProjectData(selectedProjectId);
      if (result.items?.length > 0) setSelectedResponseItemId(result.items[0].id);
      setActiveProjectView("response");
      setMessage(`Generated ${result.generated_count} response plan item(s).`);
    } catch (err) {
      setMessage(`Generate response plan failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function generateProposalOutline() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    if (responsePlan.length === 0) {
      setMessage("Generate response plan first before creating proposal outline.");
      return;
    }

    setBusy(true);
    setMessage("");

    try {
      const result = await apiFetch(`/api/v1/projects/${selectedProjectId}/generate-proposal-outline`, {
        method: "POST",
        headers: {
          "X-Actor": actorName,
        },
      });

      await loadProjectData(selectedProjectId);
      if (result.sections?.length > 0) setSelectedProposalSectionId(result.sections[0].id);
      setActiveProjectView("proposal");
      setMessage(`Generated ${result.generated_count} proposal section(s).`);
    } catch (err) {
      setMessage(`Generate proposal outline failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function generateEvidencePack() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    if (!projectMetadata && responsePlan.length === 0 && proposalOutline.length === 0) {
      setMessage("Generate metadata, response plan, or proposal outline first before creating evidence pack.");
      return;
    }

    setBusy(true);
    setMessage("");

    try {
      const result = await apiFetch(`/api/v1/projects/${selectedProjectId}/generate-evidence-pack`, {
        method: "POST",
        headers: {
          "X-Actor": actorName,
        },
      });

      await loadProjectData(selectedProjectId);

      if (result.items?.length > 0) {
        setSelectedEvidenceItemId(result.items[0].id);
      }

      setActiveProjectView("evidence");
      setMessage(`Generated ${result.generated_count} evidence item(s).`);
    } catch (err) {
      setMessage(`Generate evidence pack failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    generateClarifications,
    generateResponsePlan,
    generateProposalOutline,
    generateEvidencePack,
  };
}
