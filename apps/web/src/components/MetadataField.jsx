export default function MetadataField({ label, value, highlight = false }) {
  return (
    <div className={highlight ? "metadataField highlight" : "metadataField"}>
      <span>{label}</span>
      <strong>{value || "-"}</strong>
    </div>
  );
}
