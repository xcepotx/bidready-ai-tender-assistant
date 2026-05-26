function parseActionDueDate(value) {
  if (!value) return null;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function isActionDone(item) {
  return ["done", "closed", "completed", "cancelled", "canceled"].includes(String(item.status || "").toLowerCase());
}

function isActionOverdue(item) {
  const dueDate = parseActionDueDate(item.due_date);
  if (!dueDate || isActionDone(item)) return false;

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  dueDate.setHours(0, 0, 0, 0);

  return dueDate < today;
}

function isActionUnassigned(item) {
  return !String(item.owner || "").trim();
}

export default function ActionItemCard({ item, busy, updateActionItem }) {
  const relatedCount =
    (item.related_requirement_ids?.length || 0) +
    (item.related_response_item_ids?.length || 0) +
    (item.related_clarification_ids?.length || 0) +
    (item.related_evidence_item_ids?.length || 0) +
    (item.related_proposal_section_ids?.length || 0);

  const overdue = isActionOverdue(item);
  const unassigned = isActionUnassigned(item);
  const done = isActionDone(item);

  return (
    <article className={`actionItemCard ${item.priority || "medium"} ${item.status || "open"} ${overdue ? "overdue" : ""} ${unassigned ? "unassigned" : ""} ${done ? "done" : ""}`}>
      <div className="actionItemTop">
        <div>
          <span className={`priorityPill ${item.priority}`}>{item.priority}</span>
          <span className="sourcePill">{item.source_type}</span>
          {overdue && <span className="actionAlertPill overdue">Overdue</span>}
          {unassigned && <span className="actionAlertPill unassigned">Unassigned</span>}
        </div>
        <select
          value={item.status || "open"}
          disabled={busy}
          onChange={(e) => updateActionItem(item.id, { status: e.target.value })}
        >
          <option value="open">Open</option>
          <option value="in_progress">In progress</option>
          <option value="done">Done</option>
          <option value="blocked">Blocked</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      <h3>{item.title}</h3>
      <p>{item.description || "No description."}</p>

      <div className="actionItemMetaGrid">
        <div>
          <span>Owner</span>
          <strong>{item.owner || "unassigned"}</strong>
        </div>
        <div>
          <span>Due Date</span>
          <strong>{item.due_date || "not set"}</strong>
        </div>
        <div>
          <span>Related</span>
          <strong>{relatedCount}</strong>
        </div>
        <div>
          <span>Source ID</span>
          <strong>{item.source_id || "-"}</strong>
        </div>
      </div>

      {item.notes && <p className="actionItemNotes">{item.notes}</p>}

      <div className="actionQuickControls">
        <button type="button" disabled={busy} onClick={() => updateActionItem(item.id, { status: "in_progress" })}>
          Start
        </button>
        <button type="button" disabled={busy} onClick={() => updateActionItem(item.id, { status: "done" })}>
          Mark Done
        </button>
        <button type="button" disabled={busy} onClick={() => updateActionItem(item.id, { status: "blocked" })}>
          Block
        </button>
      </div>
    </article>
  );
}
