export default function ReadinessSummaryCard({ summary }) {
  if (!summary) {
    return (
      <div className="readinessCard summaryReadiness">
        <div>
          <p className="eyebrow dark">Readiness Summary</p>
          <h2>No readiness data yet</h2>
          <p className="muted">Upload and analyze an RFP document to generate bid readiness signals.</p>
        </div>
      </div>
    );
  }

  const score = Number(summary.readiness_score || 0);
  const scoreClass = score >= 85 ? "good" : score >= 65 ? "medium" : score >= 40 ? "warning" : "bad";

  return (
    <div className="readinessCard summaryReadiness">
      <div className="readinessScoreBlock">
        <p className="eyebrow dark">Readiness Summary</p>
        <div className={`scoreCircle ${scoreClass}`}>
          <span>{score}</span>
          <small>/100</small>
        </div>
        <h2>{summary.recommendation}</h2>
        <p className="muted">{summary.project_title}</p>
      </div>

      <div className="readinessMetrics">
        <div>
          <strong>{summary.requirement_count}</strong>
          <span>Requirements</span>
        </div>
        <div>
          <strong>{summary.high_risk_requirement_count}</strong>
          <span>High Risk</span>
        </div>
        <div>
          <strong>{summary.needs_review_requirement_count}</strong>
          <span>Needs Review</span>
        </div>
        <div>
          <strong>{summary.open_clarification_count}</strong>
          <span>Open Clarifications</span>
        </div>
        <div>
          <strong>{summary.blocked_requirement_count}</strong>
          <span>Blocked</span>
        </div>
        <div>
          <strong>{summary.accepted_requirement_count}</strong>
          <span>Accepted</span>
        </div>
      </div>

      <div className="readinessSignals">
        <h3>Top Signals</h3>
        <div className="signalList">
          {(summary.signals || []).map((signal, index) => (
            <div className={`signalItem ${signal.severity}`} key={`${signal.label}-${index}`}>
              <strong>{signal.label}</strong>
              <span>{signal.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
