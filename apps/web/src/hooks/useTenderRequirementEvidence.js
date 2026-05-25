import { apiFetch } from "../api/client.js";

export function useTenderRequirementEvidence({
  setMessage,
  setRequirementEvidence,
}) {
  async function loadRequirementEvidence(requirementId) {
    if (!requirementId) {
      setRequirementEvidence(null);
      return;
    }

    try {
      const evidence = await apiFetch(`/api/v1/requirements/${requirementId}/evidence`);
      setRequirementEvidence(evidence);
    } catch (err) {
      setRequirementEvidence(null);
      setMessage(`Failed to load requirement evidence: ${err.message}`);
    }
  }

  return {
    loadRequirementEvidence,
  };
}
