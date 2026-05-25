export default function ProposalTemplateView({
  proposalTemplate,
  busy,
  updateProposalTemplate,
  downloadExecutivePack,
}) {
  const template = proposalTemplate || {
    template_name: "Standard Executive Proposal",
    executive_title: "",
    cover_note: "",
    company_profile: "",
    win_theme: "",
    proposal_tone: "formal",
    section_order: [],
    excluded_section_keys: [],
    custom_sections: [],
    footer_note: "",
    notes: "",
  };

  const customSectionsText = JSON.stringify(template.custom_sections || [], null, 2);
  const sectionOrderText = (template.section_order || []).join(", ");
  const excludedSectionText = (template.excluded_section_keys || []).join(", ");

  function parseCsv(value) {
    return value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  function parseCustomSections(value) {
    try {
      const parsed = JSON.parse(value || "[]");
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return template.custom_sections || [];
    }
  }

  return (
    <div className="workspaceView proposalTemplateView">
      <div className="viewHeader proposalTemplateHeader">
        <div>
          <p className="eyebrow">Proposal Template Customization</p>
          <h2>Customize proposal structure and executive narrative</h2>
          <p className="muted">
            Control DOCX proposal title, cover note, company profile, win theme, tone, section order, excluded sections, custom sections, and footer.
          </p>
        </div>

        <button
          type="button"
          className="executivePackButton"
          disabled={busy}
          onClick={downloadExecutivePack}
        >
          Export Executive Pack
        </button>
      </div>

      <div className="proposalTemplateGrid">
        <div className="sectionBox proposalTemplatePanel">
          <h3>Template Identity</h3>

          <label>
            Template Name
            <input
              className="tableInput"
              defaultValue={template.template_name || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.template_name || "")) {
                  updateProposalTemplate({ template_name: e.target.value });
                }
              }}
            />
          </label>

          <label>
            Executive Title
            <input
              className="tableInput"
              defaultValue={template.executive_title || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.executive_title || "")) {
                  updateProposalTemplate({ executive_title: e.target.value });
                }
              }}
            />
          </label>

          <label>
            Proposal Tone
            <select
              value={template.proposal_tone || "formal"}
              disabled={busy}
              onChange={(e) => updateProposalTemplate({ proposal_tone: e.target.value })}
            >
              <option value="formal">Formal</option>
              <option value="concise">Concise</option>
              <option value="technical">Technical</option>
              <option value="executive">Executive</option>
            </select>
          </label>

          <label>
            Footer Note
            <textarea
              className="tableTextarea"
              defaultValue={template.footer_note || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.footer_note || "")) {
                  updateProposalTemplate({ footer_note: e.target.value });
                }
              }}
            />
          </label>
        </div>

        <div className="sectionBox proposalTemplatePanel">
          <h3>Executive Narrative</h3>

          <label>
            Cover Note
            <textarea
              className="tableTextarea"
              defaultValue={template.cover_note || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.cover_note || "")) {
                  updateProposalTemplate({ cover_note: e.target.value });
                }
              }}
            />
          </label>

          <label>
            Company Profile
            <textarea
              className="tableTextarea"
              defaultValue={template.company_profile || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.company_profile || "")) {
                  updateProposalTemplate({ company_profile: e.target.value });
                }
              }}
            />
          </label>

          <label>
            Win Theme
            <textarea
              className="tableTextarea"
              defaultValue={template.win_theme || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.win_theme || "")) {
                  updateProposalTemplate({ win_theme: e.target.value });
                }
              }}
            />
          </label>
        </div>
      </div>

      <div className="proposalTemplateGrid">
        <div className="sectionBox proposalTemplatePanel">
          <h3>Section Controls</h3>
          <p className="muted">
            Use proposal section keys separated by comma. Empty value keeps generated order.
          </p>

          <label>
            Section Order
            <input
              className="tableInput"
              defaultValue={sectionOrderText}
              disabled={busy}
              placeholder="executive_summary, scope, solution, timeline"
              onBlur={(e) => {
                if (e.target.value !== sectionOrderText) {
                  updateProposalTemplate({ section_order: parseCsv(e.target.value) });
                }
              }}
            />
          </label>

          <label>
            Excluded Section Keys
            <input
              className="tableInput"
              defaultValue={excludedSectionText}
              disabled={busy}
              placeholder="pricing, appendix"
              onBlur={(e) => {
                if (e.target.value !== excludedSectionText) {
                  updateProposalTemplate({ excluded_section_keys: parseCsv(e.target.value) });
                }
              }}
            />
          </label>

          <label>
            Internal Notes
            <textarea
              className="tableTextarea"
              defaultValue={template.notes || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.notes || "")) {
                  updateProposalTemplate({ notes: e.target.value });
                }
              }}
            />
          </label>
        </div>

        <div className="sectionBox proposalTemplatePanel">
          <h3>Custom Sections JSON</h3>
          <p className="muted">
            Example: [{`{"title":"Why Us","content":"Our differentiator..."}`}]
          </p>

          <textarea
            className="tableTextarea customSectionsTextarea"
            defaultValue={customSectionsText}
            disabled={busy}
            onBlur={(e) => {
              if (e.target.value !== customSectionsText) {
                updateProposalTemplate({ custom_sections: parseCustomSections(e.target.value) });
              }
            }}
          />

          <div className="actionQuickControls">
            <button
              type="button"
              disabled={busy}
              onClick={() =>
                updateProposalTemplate({
                  custom_sections: [
                    ...(template.custom_sections || []),
                    {
                      title: "Why We Win",
                      content: "Add tailored differentiators, proof points, and executive value here.",
                    },
                  ],
                })
              }
            >
              Add Sample Section
            </button>

            <button
              type="button"
              disabled={busy}
              onClick={() =>
                updateProposalTemplate({
                  executive_title: "Executive Proposal",
                  proposal_tone: "executive",
                  cover_note: "This proposal is tailored to the client priorities, requirements, and risk posture.",
                  win_theme: "We combine compliance, delivery confidence, and measurable business value.",
                })
              }
            >
              Apply Executive Preset
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
