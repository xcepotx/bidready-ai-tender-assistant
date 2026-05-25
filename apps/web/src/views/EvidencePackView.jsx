import { L } from "../utils/i18n.js";
import { useState } from "react";
import EvidenceStat from "../components/EvidenceStat.jsx";
import EvidenceItemDetail from "../components/EvidenceItemDetail.jsx";
export default function EvidencePackView({
  evidencePack = [],
  selectedEvidenceItem,
  setSelectedEvidenceItemId,
  busy,
  updateEvidenceItem,
  generateEvidencePack,
  projectMetadata,
  responsePlan = [],
  proposalOutline = [],
}) {
  const safeEvidencePack = Array.isArray(evidencePack) ? evidencePack : [];
  const safeResponsePlan = Array.isArray(responsePlan) ? responsePlan : [];
  const safeProposalOutline = Array.isArray(proposalOutline) ? proposalOutline : [];

  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [ownerFilter, setOwnerFilter] = useState("all");

  const canGenerate = Boolean(projectMetadata) || safeResponsePlan.length > 0 || safeProposalOutline.length > 0;

  const owners = Array.from(
    new Set(safeEvidencePack.map((item) => item.owner).filter(Boolean))
  ).sort();

  const categories = Array.from(
    new Set(safeEvidencePack.map((item) => item.evidence_category).filter(Boolean))
  ).sort();

  const filteredItems = safeEvidencePack.filter((item) => {
    const query = searchQuery.trim().toLowerCase();

    const matchesSearch =
      !query ||
      item.evidence_name?.toLowerCase().includes(query) ||
      item.evidence_category?.toLowerCase().includes(query) ||
      item.owner?.toLowerCase().includes(query) ||
      item.status?.toLowerCase().includes(query) ||
      item.priority?.toLowerCase().includes(query) ||
      item.notes?.toLowerCase().includes(query);

    const matchesStatus = statusFilter === "all" || item.status === statusFilter;
    const matchesPriority = priorityFilter === "all" || item.priority === priorityFilter;
    const matchesCategory = categoryFilter === "all" || item.evidence_category === categoryFilter;
    const matchesOwner = ownerFilter === "all" || item.owner === ownerFilter;

    return matchesSearch && matchesStatus && matchesPriority && matchesCategory && matchesOwner;
  });

  const activeItem = selectedEvidenceItem || filteredItems[0] || safeEvidencePack[0] || null;

  return (
    <div className="workspaceView">
      <div className="viewHeader">
        <div>
          <h3>Evidence Pack</h3>
          <p className="muted">
            Track supporting documents, proof, attachments, owners, status, and missing evidence for tender submission.
          </p>
        </div>

        <div className="viewHeaderActions">
          <span className="filterResultCount">
            {filteredItems.length} / {safeEvidencePack.length} {L("shown", "ditampilkan")}
          </span>

          <button
            type="button"
            disabled={busy || !canGenerate}
            onClick={generateEvidencePack}
          >
            Generate Evidence Pack
          </button>
        </div>
      </div>

      {!canGenerate && safeEvidencePack.length === 0 && (
        <div className="emptyStateCard">
          <h3>Evidence Pack belum bisa dibuat</h3>
          <p className="muted">
            Generate metadata, response plan, atau proposal outline dulu sebelum membuat evidence pack.
          </p>
        </div>
      )}

      <div className="evidenceStats">
        <EvidenceStat label="Open" value={safeEvidencePack.filter((item) => item.status === "open").length} />
        <EvidenceStat label="Requested" value={safeEvidencePack.filter((item) => item.status === "requested").length} />
        <EvidenceStat label="Received" value={safeEvidencePack.filter((item) => item.status === "received").length} />
        <EvidenceStat label="Validated" value={safeEvidencePack.filter((item) => item.status === "validated").length} />
        <EvidenceStat label="Blocked" value={safeEvidencePack.filter((item) => item.status === "blocked").length} />
      </div>

      <div className="filterBar evidencePackFilterBar">
        <input
          className="filterInput"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search evidence, category, owner, status, priority, or notes..."
        />

        <select className="filterSelect" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">{L("All statuses", "Semua status")}</option>
          <option value="open">open</option>
          <option value="requested">requested</option>
          <option value="received">received</option>
          <option value="validated">validated</option>
          <option value="not_applicable">not_applicable</option>
          <option value="blocked">blocked</option>
        </select>

        <select className="filterSelect" value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
          <option value="all">All priorities</option>
          <option value="high">high</option>
          <option value="medium">medium</option>
          <option value="low">low</option>
        </select>

        <select className="filterSelect" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
          <option value="all">{L("All categories", "Semua kategori")}</option>
          {categories.map((category) => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>

        <select className="filterSelect" value={ownerFilter} onChange={(e) => setOwnerFilter(e.target.value)}>
          <option value="all">All owners</option>
          {owners.map((owner) => (
            <option key={owner} value={owner}>{owner}</option>
          ))}
        </select>

        <button
          type="button"
          className="clearFilterButton"
          onClick={() => {
            setSearchQuery("");
            setStatusFilter("all");
            setPriorityFilter("all");
            setCategoryFilter("all");
            setOwnerFilter("all");
          }}
        >
          Clear
        </button>
      </div>

      <div className="reviewWorkbench evidenceWorkbench">
        <div className="reviewList">
          {filteredItems.map((item) => (
            <button
              key={item.id}
              type="button"
              className={activeItem?.id === item.id ? "reviewItem active evidenceItem" : "reviewItem evidenceItem"}
              onClick={() => setSelectedEvidenceItemId(item.id)}
            >
              <div className="reviewItemTop">
                <span className={`miniEvidencePriority ${item.priority}`}>{item.priority}</span>
                <span className={`miniEvidenceStatus ${item.status}`}>{item.status}</span>
              </div>
              <strong>{item.evidence_name}</strong>
              <small>{item.evidence_category} · {item.owner || "No owner"}</small>
            </button>
          ))}

          {safeEvidencePack.length === 0 && (
            <div className="emptyStateMini">
              <strong>No evidence pack generated yet.</strong>
              <span>Click Generate Evidence Pack to create evidence checklist.</span>
            </div>
          )}

          {safeEvidencePack.length > 0 && filteredItems.length === 0 && (
            <p className="empty">No matching evidence item.</p>
          )}
        </div>

        <div className="detailPanel">
          {activeItem ? (
            <EvidenceItemDetail
              item={activeItem}
              busy={busy}
              updateEvidenceItem={updateEvidenceItem}
            />
          ) : (
            <div className="emptyStateCard">
              <h3>Select an evidence item</h3>
              <p className="muted">Evidence details will appear here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
