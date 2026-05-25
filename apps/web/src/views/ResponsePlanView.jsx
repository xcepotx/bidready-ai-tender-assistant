import { L } from "../utils/i18n.js";
import { useState } from "react";
import ResponseItemDetail from "../components/ResponseItemDetail.jsx";
export default function ResponsePlanView({
  responsePlan,
  selectedResponseItem,
  setSelectedResponseItemId,
  busy,
  updateResponseItem,
  generateResponsePlan,
  requirements,
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [complianceFilter, setComplianceFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");

  const categories = Array.from(new Set(responsePlan.map((item) => item.category).filter(Boolean))).sort();

  const filteredItems = responsePlan.filter((item) => {
    const query = searchQuery.trim().toLowerCase();

    const matchesSearch =
      !query ||
      item.requirement_text?.toLowerCase().includes(query) ||
      item.draft_response?.toLowerCase().includes(query) ||
      item.response_strategy?.toLowerCase().includes(query) ||
      item.category?.toLowerCase().includes(query) ||
      item.owner?.toLowerCase().includes(query) ||
      item.status?.toLowerCase().includes(query) ||
      item.compliance_status?.toLowerCase().includes(query);

    const matchesCompliance = complianceFilter === "all" || item.compliance_status === complianceFilter;
    const matchesStatus = statusFilter === "all" || item.status === statusFilter;
    const matchesCategory = categoryFilter === "all" || item.category === categoryFilter;

    return matchesSearch && matchesCompliance && matchesStatus && matchesCategory;
  });

  return (
    <div className="workspaceView">
      <div className="viewHeader">
        <div>
          <h3>{L("Response Plan", "Rencana Respons")}</h3>
          <p className="muted">{L("Convert reviewed requirements into compliance status, response strategy, draft response, and evidence checklist.", "Konversi requirement yang sudah direview menjadi status kepatuhan, strategi respons, draft respons, dan checklist evidence.")}</p>
        </div>
        <div className="viewHeaderActions">
          <span className="filterResultCount">
            {filteredItems.length} / {responsePlan.length} {L("shown", "ditampilkan")}
          </span>
          <button disabled={busy || requirements.length === 0} onClick={generateResponsePlan}>
            Generate Response Plan
          </button>
        </div>
      </div>

      <div className="filterBar responsePlanFilterBar">
        <input
          className="filterInput"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search requirement, draft response, owner, category, or compliance..."
        />

        <select className="filterSelect" value={complianceFilter} onChange={(e) => setComplianceFilter(e.target.value)}>
          <option value="all">{L("All compliance", "Semua kepatuhan")}</option>
          <option value="likely_compliant">likely_compliant</option>
          <option value="partially_compliant">partially_compliant</option>
          <option value="non_compliant">non_compliant</option>
          <option value="needs_review">needs_review</option>
          <option value="needs_clarification">needs_clarification</option>
          <option value="blocked">blocked</option>
        </select>

        <select className="filterSelect" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">{L("All statuses", "Semua status")}</option>
          <option value="draft">draft</option>
          <option value="in_review">in_review</option>
          <option value="ready">ready</option>
          <option value="approved">approved</option>
          <option value="blocked">blocked</option>
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
            setComplianceFilter("all");
            setStatusFilter("all");
            setCategoryFilter("all");
          }}
        >
          Clear
        </button>
      </div>

      <div className="reviewWorkbench">
        <div className="reviewList">
          {filteredItems.map((item) => (
            <button
              key={item.id}
              className={selectedResponseItem?.id === item.id ? "reviewItem active" : "reviewItem"}
              onClick={() => setSelectedResponseItemId(item.id)}
            >
              <div className="reviewItemTop">
                <span className={`miniCompliance ${item.compliance_status}`}>{item.compliance_status}</span>
                <span className="miniCategory">{item.category}</span>
              </div>
              <strong>{item.requirement_text}</strong>
              <small>{item.owner || "No owner"} · {item.status}</small>
            </button>
          ))}
          {responsePlan.length === 0 && <p className="empty">No response plan generated yet.</p>}
          {responsePlan.length > 0 && filteredItems.length === 0 && <p className="empty">No matching response item.</p>}
        </div>

        <div className="detailPanel">
          {selectedResponseItem ? (
            <ResponseItemDetail
              item={selectedResponseItem}
              busy={busy}
              updateResponseItem={updateResponseItem}
            />
          ) : (
            <p className="empty">Select a response item.</p>
          )}
        </div>
      </div>
    </div>
  );
}
