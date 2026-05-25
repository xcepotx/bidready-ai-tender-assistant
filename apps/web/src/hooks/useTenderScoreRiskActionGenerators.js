import { apiFetch } from "../api/client.js";

export function useTenderScoreRiskActionGenerators({
  selectedProjectId,
  actorName,
  setBusy,
  setMessage,
  setActiveProjectView,
  setComplianceScorecard,
  setRiskItems,
  setActionItems,
}) {
  async function generateComplianceScorecard() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    setBusy(true);
    setMessage("Generating compliance scorecard...");

    try {
      const result = await apiFetch(`/api/v1/projects/${selectedProjectId}/generate-compliance-scorecard`, {
        method: "POST",
        headers: {
          "X-Actor": actorName,
        },
      });

      setComplianceScorecard({
        summary: result.summary || null,
        items: result.items || [],
      });
      setActiveProjectView("compliance");
      setMessage(`Generated ${result.generated_count || 0} compliance matrix item(s).`);
    } catch (err) {
      setMessage(`Generate compliance scorecard failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function generateRiskRegister() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    setBusy(true);
    setMessage("Generating risk register...");

    try {
      const result = await apiFetch(`/api/v1/projects/${selectedProjectId}/generate-risk-register`, {
        method: "POST",
        headers: {
          "X-Actor": actorName,
        },
      });

      setRiskItems(result.items || []);
      setActiveProjectView("risks");
      setMessage(`Generated ${result.generated_count || 0} risk item(s).`);
    } catch (err) {
      setMessage(`Generate risk register failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function generateActionItems() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    setBusy(true);
    setMessage("Generating action items...");

    try {
      const result = await apiFetch(`/api/v1/projects/${selectedProjectId}/generate-action-items`, {
        method: "POST",
        headers: {
          "X-Actor": actorName,
        },
      });

      setActionItems(result.items || []);
      setActiveProjectView("actions");
      setMessage(`Generated ${result.generated_count || 0} action item(s).`);
    } catch (err) {
      setMessage(`Generate action items failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    generateComplianceScorecard,
    generateRiskRegister,
    generateActionItems,
  };
}
