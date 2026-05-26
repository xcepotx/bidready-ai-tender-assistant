import { apiFetch } from "../api/client.js";

export function useTenderLanguageTemplate({
  selectedProjectId,
  actorName,
  setBusy,
  setMessage,
  setLanguageSetting,
  setProposalTemplate,
}) {
  async function updateLanguageSetting(patch) {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    setBusy(true);
    setMessage("");

    try {
      const updated = await apiFetch(`/api/v1/projects/${selectedProjectId}/language`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify(patch),
      });

      setLanguageSetting(updated);
      window.localStorage.setItem("bidreadyUiLanguage", updated.output_language || "en");
      setMessage(`Language updated: output ${updated.output_language === "id" ? "Indonesia" : "English"}. Regenerate analysis artifacts to apply it.`);
    } catch (err) {
      setMessage(`Language update failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function updateProposalTemplate(patch) {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    setBusy(true);
    setMessage("");

    try {
      const updated = await apiFetch(`/api/v1/projects/${selectedProjectId}/proposal-template`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify(patch),
      });

      setProposalTemplate(updated);
      setMessage("Proposal template updated.");
    } catch (err) {
      setMessage(`Update proposal template failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    updateLanguageSetting,
    updateProposalTemplate,
  };
}
