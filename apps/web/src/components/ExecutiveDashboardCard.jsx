import ExecutiveMetric from "./ExecutiveMetric.jsx";
import ExecutiveStage from "./ExecutiveStage.jsx";
export default function ExecutiveDashboardCard({
  readinessSummary,
  decisionGate,
  requirements = [],
  clarifications = [],
  responsePlan = [],
  proposalOutline = [],
  evidencePack = [],
}) {
  const highRiskRequirements = requirements.filter((item) => item.risk_level === "high").length;
  const needsReviewRequirements = requirements.filter((item) => item.status === "needs_review").length;
  const openClarifications = clarifications.filter((item) => item.status === "open").length;
  const highPriorityClarifications = clarifications.filter((item) => item.priority === "high").length;
  const openEvidence = evidencePack.filter((item) => ["open", "requested"].includes(item.status)).length;
  const highPriorityEvidence = evidencePack.filter((item) => item.priority === "high" && ["open", "requested"].includes(item.status)).length;
  const readyProposalSections = proposalOutline.filter((item) => ["ready", "approved"].includes(item.status)).length;
  const blockedResponseItems = responsePlan.filter((item) => item.status === "blocked" || item.compliance_status === "blocked").length;

  const readinessScore = decisionGate?.readiness_score ?? readinessSummary?.readiness_score ?? 0;
  const recommendation = decisionGate?.recommendation || readinessSummary?.recommendation || "No executive decision generated yet";
  const decisionStatus = decisionGate?.decision_status || "not_generated";

  const topBlockers = decisionGate?.blockers?.length
    ? decisionGate.blockers.slice(0, 3)
    : [
        highRiskRequirements ? `${highRiskRequirements} high-risk requirement(s) need review.` : null,
        openClarifications ? `${openClarifications} clarification question(s) are still open.` : null,
        highPriorityEvidence ? `${highPriorityEvidence} high-priority evidence item(s) are still open/requested.` : null,
      ].filter(Boolean);

  const nextActions = decisionGate?.next_actions?.length
    ? decisionGate.next_actions.slice(0, 4)
    : [
        needsReviewRequirements ? "Complete requirement owner review." : null,
        openClarifications ? "Resolve open clarification questions." : null,
        openEvidence ? "Collect and validate evidence pack items." : null,
        proposalOutline.length ? "Move proposal sections to ready/approved." : "Generate proposal outline.",
      ].filter(Boolean);

  return (
    <div className="executiveDashboardCard">
      <div className="executiveDashboardHeader">
        <div>
          <p className="eyebrow dark">Executive Dashboard</p>
          <h2>{recommendation}</h2>
          <p className="muted">
            One-page bid health view for owner review, approval, and next-action alignment.
          </p>
        </div>

        <div className={`executiveDecisionPill ${decisionStatus}`}>
          <span>Decision</span>
          <strong>{decisionStatus}</strong>
        </div>
      </div>

      <div className="executiveScoreRow">
        <div className="executiveScoreMain">
          <span>Readiness Score</span>
          <strong>{readinessScore}</strong>
          <small>{readinessSummary?.recommendation || "Readiness summary unavailable"}</small>
        </div>

        <ExecutiveMetric label="High Risk Req." value={highRiskRequirements} tone={highRiskRequirements ? "danger" : "ok"} />
        <ExecutiveMetric label="Needs Review" value={needsReviewRequirements} tone={needsReviewRequirements ? "warning" : "ok"} />
        <ExecutiveMetric label="Open Clarifications" value={openClarifications} tone={openClarifications ? "warning" : "ok"} />
        <ExecutiveMetric label="High Priority Evidence" value={highPriorityEvidence} tone={highPriorityEvidence ? "danger" : "ok"} />
        <ExecutiveMetric label="Blocked Responses" value={blockedResponseItems} tone={blockedResponseItems ? "danger" : "ok"} />
      </div>

      <div className="executivePipeline">
        <ExecutiveStage label="Requirements" value={requirements.length} />
        <ExecutiveStage label="Clarifications" value={clarifications.length} />
        <ExecutiveStage label="Response Plan" value={responsePlan.length} />
        <ExecutiveStage label="Proposal Sections" value={`${readyProposalSections}/${proposalOutline.length}`} />
        <ExecutiveStage label="Evidence Pack" value={evidencePack.length} />
      </div>

      <div className="executiveInsightGrid">
        <div className="executiveInsightBox danger">
          <h3>Top Blockers</h3>
          {topBlockers.length ? (
            <ul>
              {topBlockers.map((item, index) => (
                <li key={`blocker-${index}`}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="muted">No major blocker detected.</p>
          )}
        </div>

        <div className="executiveInsightBox">
          <h3>Next Actions</h3>
          {nextActions.length ? (
            <ul>
              {nextActions.map((item, index) => (
                <li key={`action-${index}`}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="muted">No pending action detected.</p>
          )}
        </div>
      </div>
    </div>
  );
}
