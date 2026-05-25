import MetadataField from "./MetadataField.jsx";

export default function RfpMetadataCard({ metadata }) {
  if (!metadata) {
    return (
      <div className="metadataCard">
        <div className="metadataHeader">
          <div>
            <p className="eyebrow dark">RFP Metadata</p>
            <h2>No metadata extracted yet</h2>
            <p className="muted">Click Extract Metadata to identify deadline, issuer, package name, service domain, and submission requirements.</p>
          </div>
          <span className="metadataMode">rules_only</span>
        </div>
      </div>
    );
  }

  const submissionRequirements = metadata.submission_requirements || [];

  return (
    <div className="metadataCard">
      <div className="metadataHeader">
        <div>
          <p className="eyebrow dark">RFP Metadata</p>
          <h2>{metadata.package_name || "Untitled Package"}</h2>
          <p className="muted">
            Extracted by {metadata.extraction_mode || "rules_only"}
          </p>
        </div>
        <span className="metadataMode">{metadata.extraction_mode || "rules_only"}</span>
      </div>

      <div className="metadataGrid">
        <MetadataField label="Issuer" value={metadata.issuer} />
        <MetadataField label="Submission Deadline" value={metadata.submission_deadline} highlight />
        <MetadataField label="Clarification Deadline" value={metadata.clarification_deadline} />
        <MetadataField label="Proposal Validity" value={metadata.proposal_validity} />
        <MetadataField label="Service Domain" value={metadata.service_domain} />
        <MetadataField label="Notes" value={metadata.notes} />
      </div>

      <div className="metadataRequirements">
        <h3>Submission Requirements</h3>
        {submissionRequirements.length === 0 ? (
          <p className="muted">No submission requirement detected yet.</p>
        ) : (
          <div className="metadataPills">
            {submissionRequirements.map((item, index) => (
              <span key={`${item}-${index}`}>{item}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
