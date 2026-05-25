export default function DecisionList({ title, items, danger = false }) {
  return (
    <div className={danger ? "decisionList danger" : "decisionList"}>
      <h3>{title}</h3>
      {items.length === 0 ? (
        <p className="muted">No item.</p>
      ) : (
        <ul>
          {items.map((item, index) => (
            <li key={`${title}-${index}`}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
