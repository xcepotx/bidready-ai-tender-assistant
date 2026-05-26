import { translateRequirementTextForUi } from "../utils/i18n.js";
import ResponseList from "./ResponseList.jsx";
export default function ResponseItemDetail({ item, busy, updateResponseItem, uiLanguage = "en" }) {
  const isIndonesian = String(uiLanguage || "").toLowerCase().startsWith("id");
  const T = (en, id) => (isIndonesian ? id : en);
  const requirementText = translateRequirementTextForUi(item.requirement_text, uiLanguage);
  const evidenceQuote = translateRequirementTextForUi(item.evidence_quote, uiLanguage);
  return (
    <div className="detailContent responseDetail">
      <div className="detailTitleRow">
        <div>
          <p className="eyebrow dark">{T("Response Item", "Item Respons")} #{item.id}</p>
          <h2>{requirementText}</h2>
        </div>
        <span className={`responseBadge ${item.compliance_status}`}>{item.compliance_status}</span>
      </div>

      <div className="detailMeta">
        <span>{T("Category", "Kategori")}: {item.category}</span>
        <span>{T("Status", "Status")}: {item.status}</span>
        <span>{T("Owner", "Penanggung jawab")}: {item.owner || "-"}</span>
        <span>{T("Source page", "Halaman sumber")}: {item.source_page || "-"}</span>
        <span>{T("Mode", "Mode")}: {item.generation_mode}</span>
      </div>

      {item.evidence_quote && (
        <div className="evidenceBox">
          <strong>{T("Requirement Evidence", "Bukti Requirement")}</strong>
          <p>{evidenceQuote}</p>
        </div>
      )}

      <div className="detailGrid">
        <label>
          {T("Compliance", "Kepatuhan")}
          <select
            value={item.compliance_status || "needs_review"}
            disabled={busy}
            onChange={(e) => updateResponseItem(item.id, { compliance_status: e.target.value })}
          >
            <option value="likely_compliant">likely_compliant</option>
            <option value="partially_compliant">partially_compliant</option>
            <option value="non_compliant">non_compliant</option>
            <option value="needs_review">needs_review</option>
            <option value="needs_clarification">needs_clarification</option>
            <option value="blocked">blocked</option>
          </select>
        </label>

        <label>
          {T("Status", "Status")}
          <select
            value={item.status || "draft"}
            disabled={busy}
            onChange={(e) => updateResponseItem(item.id, { status: e.target.value })}
          >
            <option value="draft">draft</option>
            <option value="in_review">in_review</option>
            <option value="ready">ready</option>
            <option value="approved">approved</option>
            <option value="blocked">blocked</option>
          </select>
        </label>

        <label>
          {T("Owner", "Penanggung jawab")}
          <input
            defaultValue={item.owner || ""}
            disabled={busy}
            onBlur={(e) => {
              if (e.target.value !== (item.owner || "")) {
                updateResponseItem(item.id, { owner: e.target.value });
              }
            }}
          />
        </label>

        <label>
          {T("Confidence", "Tingkat keyakinan")}
          <input value={item.confidence} disabled readOnly />
        </label>
      </div>

      <label className="fullField">
        {T("Response Strategy", "Strategi Respons")}
        <textarea
          defaultValue={item.response_strategy || ""}
          disabled={busy}
          onBlur={(e) => {
            if (e.target.value !== (item.response_strategy || "")) {
              updateResponseItem(item.id, { response_strategy: e.target.value });
            }
          }}
        />
      </label>

      <label className="fullField">
        {T("Draft Response", "Draft Respons")}
        <textarea
          defaultValue={item.draft_response || ""}
          disabled={busy}
          onBlur={(e) => {
            if (e.target.value !== (item.draft_response || "")) {
              updateResponseItem(item.id, { draft_response: e.target.value });
            }
          }}
        />
      </label>

      <div className="responseLists">
        <ResponseList title={T("Evidence Needed", "Evidence yang Dibutuhkan")} items={item.evidence_needed || []} emptyText={T("No item.", "Tidak ada item.")} />
        <ResponseList title={T("Risks", "Risiko")} items={item.risks || []} emptyText={T("No item.", "Tidak ada item.")} />
        <ResponseList title={T("Assumptions", "Asumsi")} items={item.assumptions || []} emptyText={T("No item.", "Tidak ada item.")} />
      </div>

      <label className="fullField">
        {T("Notes", "Catatan")}
        <textarea
          defaultValue={item.notes || ""}
          disabled={busy}
          onBlur={(e) => {
            if (e.target.value !== (item.notes || "")) {
              updateResponseItem(item.id, { notes: e.target.value });
            }
          }}
        />
      </label>
    </div>
  );
}
