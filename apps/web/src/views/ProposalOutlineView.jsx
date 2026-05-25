import { L } from "../utils/i18n.js";
import { useState } from "react";
import ProposalSectionDetail from "../components/ProposalSectionDetail.jsx";
export default function ProposalOutlineView({
  proposalOutline,
  selectedProposalSection,
  setSelectedProposalSectionId,
  busy,
  updateProposalSection,
  generateProposalOutline,
  responsePlan,
  downloadProposalDraft,
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [ownerFilter, setOwnerFilter] = useState("all");

  const owners = Array.from(new Set(proposalOutline.map((item) => item.owner).filter(Boolean))).sort();

  const filteredSections = proposalOutline.filter((section) => {
    const query = searchQuery.trim().toLowerCase();

    const matchesSearch =
      !query ||
      section.title?.toLowerCase().includes(query) ||
      section.purpose?.toLowerCase().includes(query) ||
      section.draft_content?.toLowerCase().includes(query) ||
      section.owner?.toLowerCase().includes(query) ||
      section.status?.toLowerCase().includes(query) ||
      (section.content_outline || []).join(" ").toLowerCase().includes(query);

    const matchesStatus = statusFilter === "all" || section.status === statusFilter;
    const matchesOwner = ownerFilter === "all" || section.owner === ownerFilter;

    return matchesSearch && matchesStatus && matchesOwner;
  });

  return (
    <div className="workspaceView">
      <div className="viewHeader">
        <div>
          <h3>Proposal Outline</h3>
          <p className="muted">Build an editable proposal structure from the response plan, evidence checklist, risks, and owners.</p>
        </div>
        <div className="viewHeaderActions">
          <span className="filterResultCount">
            {filteredSections.length} / {proposalOutline.length} {L("shown", "ditampilkan")}
          </span>
          <button disabled={busy || responsePlan.length === 0} onClick={generateProposalOutline}>
            Generate Proposal Outline
          </button>
          <button disabled={busy || proposalOutline.length === 0} onClick={downloadProposalDraft}>
            Download DOCX
          </button>
        </div>
      </div>

      <div className="filterBar proposalOutlineFilterBar">
        <input
          className="filterInput"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search section, purpose, draft content, owner, or status..."
        />

        <select className="filterSelect" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">{L("All statuses", "Semua status")}</option>
          <option value="draft">draft</option>
          <option value="in_review">in_review</option>
          <option value="ready">ready</option>
          <option value="approved">approved</option>
          <option value="blocked">blocked</option>
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
            setOwnerFilter("all");
          }}
        >
          Clear
        </button>
      </div>

      <div className="reviewWorkbench proposalWorkbench">
        <div className="reviewList">
          {filteredSections.map((section) => (
            <button
              key={section.id}
              className={selectedProposalSection?.id === section.id ? "reviewItem active proposalItem" : "reviewItem proposalItem"}
              onClick={() => setSelectedProposalSectionId(section.id)}
            >
              <div className="reviewItemTop">
                <span className="sectionOrder">{section.section_order}</span>
                <span className={`miniProposalStatus ${section.status}`}>{section.status}</span>
              </div>
              <strong>{section.title}</strong>
              <small>{section.owner || "No owner"} · {section.section_key}</small>
            </button>
          ))}
          {proposalOutline.length === 0 && <p className="empty">No proposal outline generated yet.</p>}
          {proposalOutline.length > 0 && filteredSections.length === 0 && <p className="empty">No matching proposal section.</p>}
        </div>

        <div className="detailPanel">
          {selectedProposalSection ? (
            <ProposalSectionDetail
              section={selectedProposalSection}
              busy={busy}
              updateProposalSection={updateProposalSection}
            />
          ) : (
            <p className="empty">Select a proposal section.</p>
          )}
        </div>
      </div>
    </div>
  );
}
