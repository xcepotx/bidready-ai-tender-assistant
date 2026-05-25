export default function ComplianceRelationBox({ title, values = [] }) {
  const safeValues = Array.isArray(values) ? values.filter((item) => item !== null && item !== undefined) : [];

  return (
    <div className="relationBox">
      <span>{title}</span>
      <strong>{safeValues.length ? safeValues.join(", ") : "-"}</strong>
    </div>
  );
}
