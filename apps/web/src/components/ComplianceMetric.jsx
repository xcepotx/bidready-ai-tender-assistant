export default function ComplianceMetric({ label, value, tone = "" }) {
  return (
    <div className={`actionStat ${tone}`}>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}
