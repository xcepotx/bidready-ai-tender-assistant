export default function ExecutiveStage({ label, value }) {
  return (
    <div className="executiveStage">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
