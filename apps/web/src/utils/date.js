export function formatWibDateTime(value) {
  if (!value) return "-";

  // Backend stores UTC-like datetime without timezone suffix.
  // Add Z so browser treats it as UTC, then display as Asia/Jakarta.
  const normalized = /Z$|[+-]\d{2}:\d{2}$/.test(value) ? value : `${value}Z`;
  const date = new Date(normalized);

  if (Number.isNaN(date.getTime())) return value;

  return `${new Intl.DateTimeFormat("id-ID", {
    dateStyle: "medium",
    timeStyle: "medium",
    timeZone: "Asia/Jakarta",
    hour12: false,
  }).format(date)} WIB`;
}
