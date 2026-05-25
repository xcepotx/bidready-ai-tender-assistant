from datetime import datetime
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    title: str
    issuer: str | None = None
    tender_type: str | None = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    issuer: str | None
    tender_type: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    content_type: str | None
    file_size: int
    file_hash: str
    storage_path: str
    page_count: int
    extracted_text_path: str | None
    processing_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentPageResponse(BaseModel):
    id: int
    document_id: int
    page_number: int
    text: str
    char_count: int

    class Config:
        from_attributes = True


class RequirementResponse(BaseModel):
    id: int
    project_id: int
    document_id: int | None
    category: str
    requirement_text: str
    priority: str
    risk_level: str
    source_page: int | None
    evidence_quote: str | None
    confidence: float
    suggested_owner: str | None
    status: str
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class RequirementUpdate(BaseModel):
    category: str | None = None
    requirement_text: str | None = None
    priority: str | None = None
    risk_level: str | None = None
    suggested_owner: str | None = None
    status: str | None = None
    notes: str | None = None


class ClarificationQuestionResponse(BaseModel):
    id: int
    project_id: int
    requirement_id: int | None
    category: str
    question_text: str
    reason: str | None
    priority: str
    risk_level: str
    source_page: int | None
    owner: str | None
    status: str
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ClarificationQuestionUpdate(BaseModel):
    question_text: str | None = None
    reason: str | None = None
    priority: str | None = None
    risk_level: str | None = None
    owner: str | None = None
    status: str | None = None
    notes: str | None = None


class AuditLogResponse(BaseModel):
    id: int
    project_id: int | None
    actor: str | None
    action: str
    entity_type: str
    entity_id: int | None
    before_json: dict | None
    after_json: dict | None
    ip_address: str | None
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ReadinessSignal(BaseModel):
    severity: str
    label: str
    message: str


class ReadinessSummaryResponse(BaseModel):
    project_id: int
    project_title: str
    readiness_score: int
    recommendation: str
    document_count: int
    requirement_count: int
    clarification_count: int
    high_risk_requirement_count: int
    blocked_requirement_count: int
    needs_review_requirement_count: int
    accepted_requirement_count: int
    open_clarification_count: int
    high_priority_clarification_count: int
    signals: list[ReadinessSignal]


class RequirementEvidenceResponse(BaseModel):
    requirement_id: int
    project_id: int
    document_id: int | None
    filename: str | None
    source_page: int | None
    evidence_quote: str | None
    page_text: str | None


class AiGatewayConfigResponse(BaseModel):
    mode: str
    provider: str
    model: str
    external_call_enabled: bool


class BidBriefResponse(BaseModel):
    project_id: int
    project_title: str
    ai_mode: str
    generated_by: str
    executive_summary: str
    readiness_recommendation: str
    key_risks: list[str]
    clarification_focus: list[str]
    next_actions: list[str]
    assumptions: list[str]


class RequirementBulkUpdate(BaseModel):
    requirement_ids: list[int]
    status: str | None = None
    risk_level: str | None = None
    priority: str | None = None
    suggested_owner: str | None = None
    notes: str | None = None


class ClarificationBulkUpdate(BaseModel):
    question_ids: list[int]
    status: str | None = None
    risk_level: str | None = None
    priority: str | None = None
    owner: str | None = None
    notes: str | None = None


class BulkUpdateResponse(BaseModel):
    updated_count: int
    ids: list[int]


class ProjectMetadataResponse(BaseModel):
    id: int
    project_id: int
    package_name: str | None
    issuer: str | None
    submission_deadline: str | None
    clarification_deadline: str | None
    proposal_validity: str | None
    service_domain: str | None
    submission_requirements: list
    source_evidence: dict
    extraction_mode: str
    notes: str | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True



class ResponseItemResponse(BaseModel):
    id: int
    project_id: int
    requirement_id: int | None
    category: str
    requirement_text: str
    compliance_status: str
    response_strategy: str | None
    draft_response: str | None
    evidence_needed: list
    assumptions: list
    risks: list
    owner: str | None
    status: str
    confidence: float
    source_page: int | None
    evidence_quote: str | None
    notes: str | None
    generation_mode: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ResponseItemUpdate(BaseModel):
    compliance_status: str | None = None
    response_strategy: str | None = None
    draft_response: str | None = None
    evidence_needed: list | None = None
    assumptions: list | None = None
    risks: list | None = None
    owner: str | None = None
    status: str | None = None
    notes: str | None = None


class GenerateResponsePlanResponse(BaseModel):
    generated_count: int
    items: list[ResponseItemResponse]


class ProposalSectionResponse(BaseModel):
    id: int
    project_id: int
    section_key: str
    title: str
    section_order: int
    purpose: str | None
    content_outline: list
    draft_content: str | None
    source_response_item_ids: list
    evidence_needed: list
    risks: list
    owner: str | None
    status: str
    notes: str | None
    generation_mode: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ProposalSectionUpdate(BaseModel):
    title: str | None = None
    purpose: str | None = None
    content_outline: list | None = None
    draft_content: str | None = None
    evidence_needed: list | None = None
    risks: list | None = None
    owner: str | None = None
    status: str | None = None
    notes: str | None = None


class GenerateProposalOutlineResponse(BaseModel):
    generated_count: int
    sections: list[ProposalSectionResponse]


class EvidenceItemResponse(BaseModel):
    id: int
    project_id: int
    evidence_name: str
    evidence_category: str
    owner: str | None
    status: str
    priority: str
    source_type: str
    source_ids: list
    related_requirement_ids: list
    related_response_item_ids: list
    related_proposal_section_ids: list
    notes: str | None
    generation_mode: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class EvidenceItemUpdate(BaseModel):
    evidence_name: str | None = None
    evidence_category: str | None = None
    owner: str | None = None
    status: str | None = None
    priority: str | None = None
    notes: str | None = None


class GenerateEvidencePackResponse(BaseModel):
    generated_count: int
    items: list[EvidenceItemResponse]


class DecisionGateResponse(BaseModel):
    id: int
    project_id: int
    decision_status: str
    recommendation: str
    readiness_score: int
    confidence: float
    executive_summary: str | None
    key_reasons: list
    blockers: list
    required_approvals: list
    next_actions: list
    owner: str | None
    due_date: str | None
    notes: str | None
    generation_mode: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class DecisionGateUpdate(BaseModel):
    decision_status: str | None = None
    recommendation: str | None = None
    confidence: float | None = None
    executive_summary: str | None = None
    key_reasons: list | None = None
    blockers: list | None = None
    required_approvals: list | None = None
    next_actions: list | None = None
    owner: str | None = None
    due_date: str | None = None
    notes: str | None = None


class GenerateDecisionGateResponse(BaseModel):
    gate: DecisionGateResponse


class ProjectLanguageSettingResponse(BaseModel):
    id: int
    project_id: int
    input_language: str
    output_language: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ProjectLanguageSettingUpdate(BaseModel):
    input_language: str | None = None
    output_language: str | None = None
