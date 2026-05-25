import { formatWibDateTime } from "../utils/date.js";

export default function AuditLogView({ auditLogs }) {
  return (
    <div className="workspaceView">
      <div className="viewHeader">
        <div>
          <h3>Audit Log</h3>
          <p className="muted">Track who changed what, before/after values, and timestamps.</p>
        </div>
      </div>

      <div className="auditPanel">
        {auditLogs.length === 0 && <p className="empty">No audit logs yet.</p>}

        {auditLogs.map((log) => (
          <div className="auditCard" key={log.id}>
            <div className="auditCardHeader">
              <div>
                <p className="eyebrow dark">Audit #{log.id}</p>
                <h3>{log.action}</h3>
              </div>
              <span className="auditActor">{log.actor || "unknown"}</span>
            </div>

            <div className="detailMeta">
              <span>Entity: {log.entity_type}</span>
              <span>ID: {log.entity_id || "-"}</span>
              <span>Project: {log.project_id || "-"}</span>
              <span>{formatWibDateTime(log.created_at)}</span>
            </div>

            <div className="auditGrid">
              <div className="auditJson">
                <strong>Before</strong>
                <pre>{JSON.stringify(log.before_json || {}, null, 2)}</pre>
              </div>
              <div className="auditJson">
                <strong>After</strong>
                <pre>{JSON.stringify(log.after_json || {}, null, 2)}</pre>
              </div>
            </div>

            {log.notes && (
              <div className="evidenceBox">
                <strong>Notes</strong>
                <p>{log.notes}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
