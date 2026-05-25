export default function RiskStat({ label, value, tone = "" }) {
  return (
    <div className={`actionStat ${tone}`}>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}
