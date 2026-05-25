import { useState } from "react";

function ClarificationsView({
  clarifications,
  selectedClarification,
  setSelectedClarificationId,
  busy,
  updateClarification,
  generateClarifications,
  requirements,
  bulkUpdateClarifications,
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [riskFilter, setRiskFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [selectedIds, setSelectedIds] = useState([]);
  const [bulkStatus, setBulkStatus] = useState("");
  const [bulkRisk, setBulkRisk] = useState("");
  const [bulkPriority, setBulkPriority] = useState("");
  const [bulkOwner, setBulkOwner] = useState("");
  const [bulkNotes, setBulkNotes] = useState("");

  const categories = Array.from(new Set(clarifications.map((item) => item.category).filter(Boolean))).sort();

  const filteredClarifications = clarifications.filter((q) => {
    const query = searchQuery.trim().toLowerCase();

    const matchesSearch =
      !query ||
      q.question_text?.toLowerCase().includes(query) ||
      q.reason?.toLowerCase().includes(query) ||
      q.category?.toLowerCase().includes(query) ||
      q.owner?.toLowerCase().includes(query) ||
      q.status?.toLowerCase().includes(query);

    const matchesPriority = priorityFilter === "all" || q.priority === priorityFilter;
    const matchesRisk = riskFilter === "all" || q.risk_level === riskFilter;
    const matchesStatus = statusFilter === "all" || q.status === statusFilter;
    const matchesCategory = categoryFilter === "all" || q.category === categoryFilter;

    return matchesSearch && matchesPriority && matchesRisk && matchesStatus && matchesCategory;
  });

  const filteredIds = filteredClarifications.map((item) => item.id);
  const allFilteredSelected = filteredIds.length > 0 && filteredIds.every((id) => selectedIds.includes(id));

  function toggleSelected(id) {
    setSelectedIds((current) => (
      current.includes(id)
        ? current.filter((item) => item !== id)
        : [...current, id]
    ));
  }

  function toggleSelectFiltered() {
    setSelectedIds((current) => {
      if (allFilteredSelected) {
        return current.filter((id) => !filteredIds.includes(id));
      }
      return Array.from(new Set([...current, ...filteredIds]));
    });
  }

  async function applyBulkUpdate() {
    const patch = {};

    if (bulkStatus) patch.status = bulkStatus;
    if (bulkRisk) patch.risk_level = bulkRisk;
    if (bulkPriority) patch.priority = bulkPriority;
    if (bulkOwner.trim()) patch.owner = bulkOwner.trim();
    if (bulkNotes.trim()) patch.notes = bulkNotes.trim();

    if (Object.keys(patch).length === 0) return;

    await bulkUpdateClarifications(selectedIds, patch);
    setSelectedIds([]);
    setBulkStatus("");
    setBulkRisk("");
    setBulkPriority("");
    setBulkOwner("");
    setBulkNotes("");
  }

  return (
    <div className="workspaceView">
      <div className="viewHeader">
        <div>
          <h3>Clarifications</h3>
          <p className="muted">Manage clarification questions generated from high-risk and ambiguous requirements.</p>
        </div>
        <div className="viewHeaderActions">
          <span className="filterResultCount">
            {filteredClarifications.length} / {clarifications.length} {L("shown", "ditampilkan")}
          </span>
          <button disabled={busy || requirements.length === 0} onClick={generateClarifications}>
            Generate Clarifications
          </button>
        </div>
      </div>

      <div className="filterBar clarificationFilterBar">
        <input
          className="filterInput"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search question, owner, reason, category, or status..."
        />

        <select className="filterSelect" value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
          <option value="all">All priorities</option>
          <option value="high">High priority</option>
          <option value="medium">Medium priority</option>
          <option value="low">Low priority</option>
        </select>

        <select className="filterSelect" value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)}>
          <option value="all">{L("All risks", "Semua risiko")}</option>
          <option value="high">{L("High risk", "Risiko tinggi")}</option>
          <option value="medium">{L("Medium risk", "Risiko sedang")}</option>
          <option value="low">{L("Low risk", "Risiko rendah")}</option>
        </select>

        <select className="filterSelect" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">{L("All statuses", "Semua status")}</option>
          <option value="open">open</option>
          <option value="needs_internal_review">needs_internal_review</option>
          <option value="answered">answered</option>
          <option value="closed">closed</option>
          <option value="cancelled">cancelled</option>
        </select>

        <select className="filterSelect" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
          <option value="all">{L("All categories", "Semua kategori")}</option>
          {categories.map((category) => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>

        <button
          type="button"
          className="clearFilterButton"
          onClick={() => {
            setSearchQuery("");
            setPriorityFilter("all");
            setRiskFilter("all");
            setStatusFilter("all");
            setCategoryFilter("all");
          }}
        >
          Clear
        </button>
      </div>

      <div className="bulkActionBar clarificationBulkBar">
        <label className="bulkSelectAll">
          <input
            type="checkbox"
            checked={allFilteredSelected}
            onChange={toggleSelectFiltered}
            disabled={filteredIds.length === 0}
          />
          {L("Select filtered", "Pilih hasil filter")}
        </label>

        <span className="bulkCount">{selectedIds.length} {L("selected", "dipilih")}</span>

        <select value={bulkStatus} onChange={(e) => setBulkStatus(e.target.value)}>
          <option value="">{L("Status...", "Status...")}</option>
          <option value="open">open</option>
          <option value="needs_internal_review">needs_internal_review</option>
          <option value="answered">answered</option>
          <option value="closed">closed</option>
          <option value="cancelled">cancelled</option>
        </select>

        <select value={bulkRisk} onChange={(e) => setBulkRisk(e.target.value)}>
          <option value="">{L("Risk...", "Risiko...")}</option>
          <option value="low">low</option>
          <option value="medium">medium</option>
          <option value="high">high</option>
        </select>

        <select value={bulkPriority} onChange={(e) => setBulkPriority(e.target.value)}>
          <option value="">Priority...</option>
          <option value="low">low</option>
          <option value="medium">medium</option>
          <option value="high">high</option>
        </select>

        <input
          value={bulkOwner}
          onChange={(e) => setBulkOwner(e.target.value)}
          placeholder={L("Owner...", "Owner...")}
        />

        <input
          value={bulkNotes}
          onChange={(e) => setBulkNotes(e.target.value)}
          placeholder={L("Notes...", "Catatan...")}
        />

        <button
          type="button"
          disabled={busy || selectedIds.length === 0 || (!bulkStatus && !bulkRisk && !bulkPriority && !bulkOwner.trim() && !bulkNotes.trim())}
          onClick={applyBulkUpdate}
        >
          Apply Bulk
        </button>
      </div>

      <div className="reviewWorkbench">
        <div className="reviewList">
          {filteredClarifications.map((q) => (
            <div
              key={q.id}
              className={selectedClarification?.id === q.id ? "reviewItemWrap active" : "reviewItemWrap"}
            >
              <label className="rowCheck">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(q.id)}
                  onChange={() => toggleSelected(q.id)}
                />
              </label>

              <button
                className={selectedClarification?.id === q.id ? "reviewItem active" : "reviewItem"}
                onClick={() => setSelectedClarificationId(q.id)}
              >
                <div className="reviewItemTop">
                  <span className={`miniRisk ${q.risk_level}`}>{q.risk_level}</span>
                  <span className={`miniPriority ${q.priority}`}>{q.priority}</span>
                </div>
                <strong>{q.question_text}</strong>
                <small>{q.category} · {q.status}</small>
              </button>
            </div>
          ))}
          {clarifications.length === 0 && <p className="empty">No clarification questions generated yet.</p>}
          {clarifications.length > 0 && filteredClarifications.length === 0 && <p className="empty">No matching clarification.</p>}
        </div>

        <div className="detailPanel">
          {selectedClarification ? (
            <ClarificationDetail q={selectedClarification} busy={busy} updateClarification={updateClarification} />
          ) : (
            <p className="empty">Select a clarification question.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default ClarificationsView;
