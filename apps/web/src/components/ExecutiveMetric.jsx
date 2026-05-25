export default function ExecutiveMetric({ label, value, tone = "neutral" }) {
  return (
    <div className={`executiveMetric ${tone}`}>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}
