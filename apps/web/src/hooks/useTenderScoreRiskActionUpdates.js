import { apiFetch } from "../api/client.js";

export function useTenderScoreRiskActionUpdates({
  actorName,
  setBusy,
  setMessage,
  setComplianceScorecard,
  setRiskItems,
  setActionItems,
}) {
  async function updateComplianceItem(itemId, patch) {
    setBusy(true);
    setMessage("");

    try {
      const updated = await apiFetch(`/api/v1/compliance-items/${itemId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify(patch),
      });

      setComplianceScorecard((current) => ({
        ...(current || {}),
        items: (current?.items || []).map((item) => (item.id === updated.id ? updated : item)),
      }));

      setMessage("Compliance item updated.");
    } catch (err) {
      setMessage(`Update compliance item failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function updateRiskItem(itemId, patch) {
    setBusy(true);
    setMessage("");

    try {
      const updated = await apiFetch(`/api/v1/risk-items/${itemId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify(patch),
      });

      setRiskItems((items) =>
        items.map((item) => (item.id === updated.id ? updated : item))
      );

      setMessage("Risk item updated.");
    } catch (err) {
      setMessage(`Update risk item failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function updateActionItem(itemId, patch) {
    setBusy(true);
    setMessage("");

    try {
      const updated = await apiFetch(`/api/v1/action-items/${itemId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Actor": actorName,
        },
        body: JSON.stringify(patch),
      });

      setActionItems((items) =>
        items.map((item) => (item.id === updated.id ? updated : item))
      );

      setMessage("Action item updated.");
    } catch (err) {
      setMessage(`Update action item failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    updateComplianceItem,
    updateRiskItem,
    updateActionItem,
  };
}
