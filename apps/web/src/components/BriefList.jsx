export default function BriefList({ title, items }) {
  return (
    <div className="briefList">
      <h3>{title}</h3>
      {items.length === 0 ? (
        <p className="muted">No item available.</p>
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
