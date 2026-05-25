import DecisionList from "./DecisionList.jsx";

export default function DecisionGateCard({ gate, busy, generateDecisionGate, updateDecisionGate }) {
  if (!gate) {
    return (
      <div className="decisionGateCard emptyDecisionGate">
        <div className="decisionGateHeader">
          <div>
            <p className="eyebrow dark">Executive Decision Gate</p>
            <h2>No decision gate generated yet</h2>
            <p className="muted">
              Generate a Bid / No-Bid recommendation from readiness, requirements, clarifications, response plan, proposal outline, and evidence pack.
            </p>
          </div>

          <button type="button" className="decisionPrimaryButton" onClick={generateDecisionGate}>
            Generate Decision Gate
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="decisionGateCard">
      <div className="decisionGateHeader">
        <div>
          <p className="eyebrow dark">Executive Decision Gate</p>
          <h2>{gate.recommendation}</h2>
          <p className="muted">
            Mode: {gate.generation_mode} · Confidence: {Math.round((gate.confidence || 0) * 100)}%
          </p>
        </div>

        <div className="decisionHeaderRight">
          <button type="button" className="decisionSecondaryButton" onClick={generateDecisionGate}>
            Regenerate
          </button>

          <div className="decisionScoreBox">
            <span>Readiness</span>
            <strong>{gate.readiness_score}</strong>
          </div>
        </div>
      </div>

      <div className="decisionGateControls">
        <label>
          Decision Status
          <select
            value={gate.decision_status || "needs_executive_review"}
            disabled={busy}
            onChange={(e) => updateDecisionGate(gate.id, { decision_status: e.target.value })}
          >
            <option value="recommend_bid">recommend_bid</option>
            <option value="recommend_no_bid">recommend_no_bid</option>
            <option value="needs_executive_review">needs_executive_review</option>
            <option value="approved_to_bid">approved_to_bid</option>
            <option value="no_bid">no_bid</option>
            <option value="deferred">deferred</option>
          </select>
        </label>

        <label>
          Owner
          <input
            defaultValue={gate.owner || ""}
            disabled={busy}
            onBlur={(e) => {
              if (e.target.value !== (gate.owner || "")) {
                updateDecisionGate(gate.id, { owner: e.target.value });
              }
            }}
          />
        </label>

        <label>
          Due Date
          <input
            defaultValue={gate.due_date || ""}
            disabled={busy}
            onBlur={(e) => {
              if (e.target.value !== (gate.due_date || "")) {
                updateDecisionGate(gate.id, { due_date: e.target.value });
              }
            }}
          />
        </label>

        <span className={`decisionStatusBadge ${gate.decision_status}`}>
          {gate.decision_status}
        </span>
      </div>

      <div className="decisionExecutiveSummary">
        <strong>Executive Summary</strong>
        <p>{gate.executive_summary || "-"}</p>
      </div>

      <div className="decisionGrid">
        <DecisionList title="Key Reasons" items={gate.key_reasons || []} />
        <DecisionList title="Blockers" items={gate.blockers || []} danger />
        <DecisionList title="Required Approvals" items={gate.required_approvals || []} />
        <DecisionList title="Next Actions" items={gate.next_actions || []} />
      </div>

      <label className="decisionNotes">
        Notes
        <textarea
          defaultValue={gate.notes || ""}
          disabled={busy}
          onBlur={(e) => {
            if (e.target.value !== (gate.notes || "")) {
              updateDecisionGate(gate.id, { notes: e.target.value });
            }
          }}
        />
      </label>
    </div>
  );
}
