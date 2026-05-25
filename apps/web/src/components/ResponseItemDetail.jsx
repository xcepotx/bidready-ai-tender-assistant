import ResponseList from "./ResponseList.jsx";
export default function ResponseItemDetail({ item, busy, updateResponseItem }) {
  return (
    <div className="detailContent responseDetail">
      <div className="detailTitleRow">
        <div>
          <p className="eyebrow dark">Response Item #{item.id}</p>
          <h2>{item.requirement_text}</h2>
        </div>
        <span className={`responseBadge ${item.compliance_status}`}>{item.compliance_status}</span>
      </div>

      <div className="detailMeta">
        <span>Category: {item.category}</span>
        <span>Status: {item.status}</span>
        <span>Owner: {item.owner || "-"}</span>
        <span>Source page: {item.source_page || "-"}</span>
        <span>Mode: {item.generation_mode}</span>
      </div>

      {item.evidence_quote && (
        <div className="evidenceBox">
          <strong>Requirement Evidence</strong>
          <p>{item.evidence_quote}</p>
        </div>
      )}

      <div className="detailGrid">
        <label>
          Compliance
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
          Status
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
          Owner
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
          Confidence
          <input value={item.confidence} disabled readOnly />
        </label>
      </div>

      <label className="fullField">
        Response Strategy
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
        Draft Response
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
        <ResponseList title="Evidence Needed" items={item.evidence_needed || []} />
        <ResponseList title="Risks" items={item.risks || []} />
        <ResponseList title="Assumptions" items={item.assumptions || []} />
      </div>

      <label className="fullField">
        Notes
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
