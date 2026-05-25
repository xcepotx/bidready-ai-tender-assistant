export default function ActionStat({ label, value, tone = "neutral" }) {
  return (
    <div className={`actionStat ${tone}`}>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}
