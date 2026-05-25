import { useState } from "react";
function translateRequirementTextForUi(text, uiLanguage = "en") {
  const lang = String(uiLanguage || "").toLowerCase();
  if (!lang.startsWith("id")) {
    return text || "";
  }

  const original = String(text || "").trim();

  const exact = {
    "Cloud engineers should hold relevant cloud certifications.": "Cloud engineer sebaiknya memiliki sertifikasi cloud yang relevan.",
    "Payment shall be milestone-based.": "Pembayaran harus berbasis milestone.",
    "Data must be encrypted in transit and at rest.": "Data harus dienkripsi saat transit dan saat tersimpan.",
    "Production data must remain within approved data residency locations.": "Data production harus tetap berada di lokasi data residency yang disetujui.",
    "Vendor must accept confidentiality and data protection obligations.": "Vendor harus menerima kewajiban kerahasiaan dan perlindungan data.",
    "Vendor must accept confidentiality and data": "Vendor harus menerima kewajiban kerahasiaan dan data",
    "Vendor shall provide application maintenance and support for existing enterprise": "Vendor harus menyediakan maintenance dan support aplikasi untuk enterprise yang sudah berjalan",
    "Vendor shall provide cloud infrastructure operation for production and non-cloud infrastructure": "Vendor harus menyediakan operasi infrastruktur cloud untuk production dan non-cloud infrastructure",
    "Vendor must submit the proposal by 30 June 2026 at 15:00 local time.": "Vendor harus mengirimkan proposal paling lambat 30 Juni 2026 pukul 15:00 waktu setempat.",
    "Vendor must provide at least 3 similar enterprise references.": "Vendor harus menyediakan minimal 3 referensi enterprise serupa.",
    "Proposal validity period must be at least 90 days.": "Masa berlaku proposal harus minimal 90 hari.",
    "Support must be available 24x7 for severity 1 incidents.": "Support harus tersedia 24x7 untuk insiden severity 1.",
    "Vendor must provide monthly service reports.": "Vendor harus menyediakan laporan layanan bulanan.",
    "Vendor must comply with ISO 27001 or equivalent standard.": "Vendor harus mematuhi ISO 27001 atau standar yang setara.",
    "Vendor must provide project transition plan.": "Vendor harus menyediakan rencana transisi proyek.",
    "Vendor must provide disaster recovery and backup procedure.": "Vendor harus menyediakan prosedur disaster recovery dan backup.",
    "Vendor must ensure data privacy and confidentiality.": "Vendor harus memastikan privasi dan kerahasiaan data.",
  };

  if (exact[original]) {
    return exact[original];
  }

  let output = original;

  const phraseMap = [
    ["Vendor shall provide", "Vendor harus menyediakan"],
    ["Vendor must provide", "Vendor harus menyediakan"],
    ["Vendor should provide", "Vendor sebaiknya menyediakan"],
    ["Vendor must submit", "Vendor harus mengirimkan"],
    ["Vendor must comply with", "Vendor harus mematuhi"],
    ["Vendor must ensure", "Vendor harus memastikan"],
    ["Vendor must accept", "Vendor harus menerima"],
    ["Proposal must include", "Proposal harus mencakup"],
    ["should hold", "sebaiknya memiliki"],
    ["must remain within", "harus tetap berada dalam"],
    ["must be", "harus"],
    ["shall be", "harus"],
    ["application maintenance and support", "maintenance dan support aplikasi"],
    ["cloud infrastructure operation", "operasi infrastruktur cloud"],
    ["existing enterprise", "enterprise yang sudah berjalan"],
    ["production and non-production", "production dan non-production"],
    ["relevant cloud certifications", "sertifikasi cloud yang relevan"],
    ["milestone-based", "berbasis milestone"],
    ["executive summary", "ringkasan eksekutif"],
    ["solution approach", "pendekatan solusi"],
    ["delivery model", "model delivery"],
    ["approved data residency locations", "lokasi data residency yang disetujui"],
    ["encrypted in transit and at rest", "dienkripsi saat transit dan saat tersimpan"],
    ["similar enterprise references", "referensi enterprise serupa"],
    ["proposal validity period", "masa berlaku proposal"],
    ["local time", "waktu setempat"],
    ["monthly service reports", "laporan layanan bulanan"],
    ["project transition plan", "rencana transisi proyek"],
    ["backup procedure", "prosedur backup"],
    ["confidentiality and data protection obligations", "kewajiban kerahasiaan dan perlindungan data"],
    ["data privacy and confidentiality", "privasi dan kerahasiaan data"],
  ];

  for (const [en, id] of phraseMap) {
    output = output.replaceAll(en, id);
  }

  return output;
}

function formatRequirementMeta(value, type, uiLanguage = "en") {
  return String(value || "").toLowerCase();
}

function RequirementsView({
  uiLanguage = "en",
  requirements,
  selectedRequirement,
  setSelectedRequirementId,
  busy,
  updateRequirement,
  requirementEvidence,
  bulkUpdateRequirements,
}) {
  const isIdUi = uiLanguage === "id";
  const L = (en, id) => (isIdUi ? id : en);

  const [searchQuery, setSearchQuery] = useState("");
  const [riskFilter, setRiskFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [selectedIds, setSelectedIds] = useState([]);
  const [bulkStatus, setBulkStatus] = useState("");
  const [bulkRisk, setBulkRisk] = useState("");
  const [bulkOwner, setBulkOwner] = useState("");
  const [bulkNotes, setBulkNotes] = useState("");

  const categories = Array.from(new Set(requirements.map((item) => item.category).filter(Boolean))).sort();

  const isIndonesianUi = String(uiLanguage || "").toLowerCase().startsWith("id");

  function humanizeToken(value) {
    return String(value || "general")
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }

  function formatRequirementRisk(value) {
  return value || "medium";
}

  function formatRequirementStatus(value) {
  return value || "needs_review";
}

  function formatRequirementCategory(value) {
  return value || "general";
}


  const filteredRequirements = requirements.filter((req) => {
    const query = searchQuery.trim().toLowerCase();

    const matchesSearch =
      !query ||
      req.requirement_text?.toLowerCase().includes(query) ||
      translateRequirementTextForUi(req.requirement_text, uiLanguage).toLowerCase().includes(query) ||
      req.category?.toLowerCase().includes(query) ||
      req.evidence_quote?.toLowerCase().includes(query) ||
      req.suggested_owner?.toLowerCase().includes(query) ||
      req.status?.toLowerCase().includes(query);

    const matchesRisk = riskFilter === "all" || req.risk_level === riskFilter;
    const matchesStatus = statusFilter === "all" || req.status === statusFilter;
    const matchesCategory = categoryFilter === "all" || req.category === categoryFilter;

    return matchesSearch && matchesRisk && matchesStatus && matchesCategory;
  });

  const filteredIds = filteredRequirements.map((item) => item.id);
  const allFilteredSelected = filteredIds.length > 0 && filteredIds.every((id) => selectedIds.includes(id));

  function toggleSelected(id) {
    setSelectedIds((current) =>
      current.includes(id)
        ? current.filter((item) => item !== id)
        : [...current, id]
    );
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
    if (bulkOwner.trim()) patch.suggested_owner = bulkOwner.trim();
    if (bulkNotes.trim()) patch.notes = bulkNotes.trim();

    if (Object.keys(patch).length === 0 || selectedIds.length === 0) return;

    await bulkUpdateRequirements(selectedIds, patch);
    setSelectedIds([]);
    setBulkStatus("");
    setBulkRisk("");
    setBulkOwner("");
    setBulkNotes("");
  }

  return (
    <div className="workspaceView requirementsView">
      <div className="viewHeader">
        <div>
          <h3>{L("Requirements", "Requirement")}</h3>
          <p className="muted">{L("Review extracted requirements, evidence, owner, risk, and status.", "Review requirement yang diekstrak, evidence, owner, risiko, dan status.")}</p>
        </div>
        <span className="filterResultCount">
          {filteredRequirements.length} / {requirements.length} {L("shown", "ditampilkan")}
        </span>
      </div>

      <div className="filterBar">
        <input
          className="filterInput"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={L("Search requirement, owner, evidence, or status...", "Cari requirement, owner, evidence, atau status...")}
        />

        <select className="filterSelect" value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)}>
          <option value="all">{L("All risks", "Semua risiko")}</option>
          <option value="high">{L("High risk", "Risiko tinggi")}</option>
          <option value="medium">{L("Medium risk", "Risiko sedang")}</option>
          <option value="low">{L("Low risk", "Risiko rendah")}</option>
        </select>

        <select className="filterSelect" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">{L("All statuses", "Semua status")}</option>
          <option value="needs_review">needs_review</option>
          <option value="accepted">accepted</option>
          <option value="rejected">rejected</option>
          <option value="done">done</option>
          <option value="blocked">blocked</option>
          <option value="not_applicable">not_applicable</option>
          <option value="needs_clarification">needs_clarification</option>
        </select>

        <select className="filterSelect" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
          <option value="all">{L("All categories", "Semua kategori")}</option>
          {categories.map((category) => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>
      </div>

      <div className="bulkActionBar">
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
          <option value="needs_review">needs_review</option>
          <option value="accepted">accepted</option>
          <option value="rejected">rejected</option>
          <option value="done">done</option>
          <option value="blocked">blocked</option>
          <option value="not_applicable">not_applicable</option>
          <option value="needs_clarification">needs_clarification</option>
        </select>

        <select value={bulkRisk} onChange={(e) => setBulkRisk(e.target.value)}>
          <option value="">{L("Risk...", "Risiko...")}</option>
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
          className="primaryButton"
          disabled={busy || selectedIds.length === 0}
          onClick={applyBulkUpdate}
        >
          Apply
        </button>
      </div>

      <div className="reviewWorkbench">
        <div className="reviewList">
          {filteredRequirements.map((req) => (
            <div
              key={req.id}
              className={selectedRequirement?.id === req.id ? "reviewItemWrap active" : "reviewItemWrap"}
            >
              <label className="rowCheck">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(req.id)}
                  onChange={() => toggleSelected(req.id)}
                />
              </label>

              <button
                type="button"
                className={selectedRequirement?.id === req.id ? "reviewItem active" : "reviewItem"}
                onClick={() => setSelectedRequirementId(req.id)}
              >
                <div className="reviewItemTop">
                  <span className={`miniRisk ${req.risk_level || "medium"}`}>
                    {formatRequirementRisk(req.risk_level)}
                  </span>
                  <span className="miniCategory">{formatRequirementCategory(req.category)}</span>
                </div>
                <strong>{translateRequirementTextForUi(req.requirement_text, uiLanguage)}</strong>
                <small>{L("Page", "Halaman")} {req.source_page || "-"} · {req.status || "needs_review"}</small>
              </button>
            </div>
          ))}

          {requirements.length === 0 && <p className="empty">{L("No requirements analyzed yet.", "Belum ada requirement yang dianalisis.")}</p>}
          {requirements.length > 0 && filteredRequirements.length === 0 && <p className="empty">{L("No matching requirement.", "Tidak ada requirement yang cocok.")}</p>}
        </div>

        <div className="detailPanel">
          {selectedRequirement ? (
            <RequirementDetail
              req={selectedRequirement}
              uiLanguage={uiLanguage}
              busy={busy}
              updateRequirement={updateRequirement}
              requirementEvidence={requirementEvidence}
            />
          ) : (
            <p className="empty">{L("Select a requirement.", "Pilih requirement.")}</p>
          )}
        </div>
      </div>
    </div>
  );
}

function RequirementDetail({ req, uiLanguage = "en", busy, updateRequirement, requirementEvidence }) {
  return (
    <div className="detailContent">
      <div className="detailTitleRow">
        <div>
          <p className="eyebrow dark">Requirement #{req.id}</p>
          <h2>{translateRequirementTextForUi(req.requirement_text, uiLanguage)}</h2>
        </div>
        <span className={`riskBadge ${req.risk_level}`}>{req.risk_level}</span>
      </div>

      <div className="detailMeta">
        <span>Category: {req.category}</span>
        <span>Priority: {req.priority}</span>
        <span>Source page: {req.source_page || "-"}</span>
        <span>Confidence: {req.confidence}</span>
      </div>

      {req.evidence_quote && (
        <div className="evidenceBox">
          <strong>Evidence Quote</strong>
          <p>{req.evidence_quote}</p>
        </div>
      )}

      <div className="sourceEvidenceBox">
        <div className="sourceEvidenceHeader">
          <div>
            <strong>Source Evidence</strong>
            <p>
              {requirementEvidence?.filename || "No document filename"} · Page{" "}
              {requirementEvidence?.source_page || req.source_page || "-"}
            </p>
          </div>
        </div>

        {requirementEvidence?.page_text ? (
          <pre>{requirementEvidence.page_text}</pre>
        ) : (
          <p className="muted">Full page evidence is not available for this requirement.</p>
        )}
      </div>

      <div className="detailGrid">
        <label>
          Risk Level
          <select
            value={req.risk_level || "medium"}
            disabled={busy}
            onChange={(e) => updateRequirement(req.id, { risk_level: e.target.value })}
          >
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
          </select>
        </label>

        <label>
          Status
          <select
            value={req.status || "needs_review"}
            disabled={busy}
            onChange={(e) => updateRequirement(req.id, { status: e.target.value })}
          >
            <option value="needs_review">needs_review</option>
            <option value="accepted">accepted</option>
            <option value="rejected">rejected</option>
            <option value="done">done</option>
            <option value="blocked">blocked</option>
            <option value="not_applicable">not_applicable</option>
            <option value="needs_clarification">needs_clarification</option>
          </select>
        </label>

        <label>
          Owner
          <input
            defaultValue={req.suggested_owner || ""}
            disabled={busy}
            onBlur={(e) => {
              if (e.target.value !== (req.suggested_owner || "")) {
                updateRequirement(req.id, { suggested_owner: e.target.value });
              }
            }}
          />
        </label>

        <label>
          Priority
          <select
            value={req.priority || "needs_review"}
            disabled={busy}
            onChange={(e) => updateRequirement(req.id, { priority: e.target.value })}
          >
            <option value="mandatory">mandatory</option>
            <option value="optional">optional</option>
            <option value="needs_review">needs_review</option>
          </select>
        </label>
      </div>

      <label className="fullField">
        Reviewer Notes
        <textarea
          defaultValue={req.notes || ""}
          disabled={busy}
          onBlur={(e) => {
            if (e.target.value !== (req.notes || "")) {
              updateRequirement(req.id, { notes: e.target.value });
            }
          }}
        />
      </label>
    </div>
  );
}

export default RequirementsView;
