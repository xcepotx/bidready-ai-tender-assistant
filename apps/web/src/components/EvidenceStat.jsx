export default function EvidenceStat({ label, value }) {
  return (
    <div className="evidenceStat">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}
