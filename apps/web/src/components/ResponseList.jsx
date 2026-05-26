export default function ResponseList({ title, items, emptyText = "No item." }) {
  return (
    <div className="responseListBox">
      <h3>{title}</h3>
      {items.length === 0 ? (
        <p className="muted">{emptyText}</p>
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
