export default function RelationBox({ title, values }) {
  return (
    <div className="relationBox">
      <strong>{title}</strong>
      {values.length === 0 ? <span>-</span> : <span>{values.join(", ")}</span>}
    </div>
  );
}
