export default function ProposalSectionDetail({ section, busy, updateProposalSection }) {
  return (
    <div className="detailContent proposalDetail">
      <div className="detailTitleRow">
        <div>
          <p className="eyebrow dark">Proposal Section #{section.id}</p>
          <h2>{section.title}</h2>
        </div>
        <span className={`proposalStatusBadge ${section.status}`}>{section.status}</span>
      </div>

      <div className="detailMeta">
        <span>Order: {section.section_order}</span>
        <span>Key: {section.section_key}</span>
        <span>Owner: {section.owner || "-"}</span>
        <span>Mode: {section.generation_mode}</span>
      </div>

      <div className="detailGrid">
        <label>
          Title
          <input
            defaultValue={section.title || ""}
            disabled={busy}
            onBlur={(e) => {
              if (e.target.value !== (section.title || "")) {
                updateProposalSection(section.id, { title: e.target.value });
              }
            }}
          />
        </label>

        <label>
          Status
          <select
            value={section.status || "draft"}
            disabled={busy}
            onChange={(e) => updateProposalSection(section.id, { status: e.target.value })}
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
            defaultValue={section.owner || ""}
            disabled={busy}
            onBlur={(e) => {
              if (e.target.value !== (section.owner || "")) {
                updateProposalSection(section.id, { owner: e.target.value });
              }
            }}
          />
        </label>

        <label>
          Source Response Items
          <input value={(section.source_response_item_ids || []).join(", ")} disabled readOnly />
        </label>
      </div>

      <label className="fullField">
        Purpose
        <textarea
          defaultValue={section.purpose || ""}
          disabled={busy}
          onBlur={(e) => {
            if (e.target.value !== (section.purpose || "")) {
              updateProposalSection(section.id, { purpose: e.target.value });
            }
          }}
        />
      </label>

      <div className="proposalLists">
        <ProposalList title="Content Outline" items={section.content_outline || []} />
        <ProposalList title="Evidence Needed" items={section.evidence_needed || []} />
        <ProposalList title="Risks" items={section.risks || []} />
      </div>

      <label className="fullField">
        Draft Content
        <textarea
          defaultValue={section.draft_content || ""}
          disabled={busy}
          onBlur={(e) => {
            if (e.target.value !== (section.draft_content || "")) {
              updateProposalSection(section.id, { draft_content: e.target.value });
            }
          }}
        />
      </label>

      <label className="fullField">
        Notes
        <textarea
          defaultValue={section.notes || ""}
          disabled={busy}
          onBlur={(e) => {
            if (e.target.value !== (section.notes || "")) {
              updateProposalSection(section.id, { notes: e.target.value });
            }
          }}
        />
      </label>
    </div>
  );
}
