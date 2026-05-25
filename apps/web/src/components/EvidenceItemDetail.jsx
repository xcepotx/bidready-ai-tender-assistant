export default function EvidenceItemDetail({ item, busy, updateEvidenceItem }) {
  return (
    <div className="detailContent evidenceDetail">
      <div className="detailTitleRow">
        <div>
          <p className="eyebrow dark">Evidence Item #{item.id}</p>
          <h2>{item.evidence_name}</h2>
        </div>
        <span className={`evidenceStatusBadge ${item.status}`}>{item.status}</span>
      </div>

      <div className="detailMeta">
        <span>Category: {item.evidence_category}</span>
        <span>Priority: {item.priority}</span>
        <span>Owner: {item.owner || "-"}</span>
        <span>Mode: {item.generation_mode}</span>
      </div>

      <div className="detailGrid">
        <label>
          Evidence Name
          <input
            defaultValue={item.evidence_name || ""}
            disabled={busy}
            onBlur={(e) => {
              if (e.target.value !== (item.evidence_name || "")) {
                updateEvidenceItem(item.id, { evidence_name: e.target.value });
              }
            }}
          />
        </label>

        <label>
          Category
          <input
            defaultValue={item.evidence_category || ""}
            disabled={busy}
            onBlur={(e) => {
              if (e.target.value !== (item.evidence_category || "")) {
                updateEvidenceItem(item.id, { evidence_category: e.target.value });
              }
            }}
          />
        </label>

        <label>
          Status
          <select
            value={item.status || "open"}
            disabled={busy}
            onChange={(e) => updateEvidenceItem(item.id, { status: e.target.value })}
          >
            <option value="open">open</option>
            <option value="requested">requested</option>
            <option value="received">received</option>
            <option value="validated">validated</option>
            <option value="not_applicable">not_applicable</option>
            <option value="blocked">blocked</option>
          </select>
        </label>

        <label>
          Priority
          <select
            value={item.priority || "medium"}
            disabled={busy}
            onChange={(e) => updateEvidenceItem(item.id, { priority: e.target.value })}
          >
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
          </select>
        </label>

        <label>
          Owner
          <input
            defaultValue={item.owner || ""}
            disabled={busy}
            onBlur={(e) => {
              if (e.target.value !== (item.owner || "")) {
                updateEvidenceItem(item.id, { owner: e.target.value });
              }
            }}
          />
        </label>

        <label>
          Source Type
          <input value={item.source_type || "-"} disabled readOnly />
        </label>
      </div>

      <div className="evidenceRelationGrid">
        <RelationBox title="Requirement IDs" values={item.related_requirement_ids || []} />
        <RelationBox title="Response Item IDs" values={item.related_response_item_ids || []} />
        <RelationBox title="Proposal Section IDs" values={item.related_proposal_section_ids || []} />
        <RelationBox title="Source IDs" values={item.source_ids || []} />
      </div>

      <label className="fullField">
        Notes
        <textarea
          defaultValue={item.notes || ""}
          disabled={busy}
          onBlur={(e) => {
            if (e.target.value !== (item.notes || "")) {
              updateEvidenceItem(item.id, { notes: e.target.value });
            }
          }}
        />
      </label>
    </div>
  );
}
