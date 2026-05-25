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


class ActionItemResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    source_type: str
    source_id: int | None
    related_requirement_ids: list
    related_response_item_ids: list
    related_clarification_ids: list
    related_evidence_item_ids: list
    related_proposal_section_ids: list
    owner: str | None
    priority: str
    status: str
    due_date: str | None
    confidence: float | None
    notes: str | None
    generation_mode: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ActionItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    owner: str | None = None
    priority: str | None = None
    status: str | None = None
    due_date: str | None = None
    notes: str | None = None


class GenerateActionItemsResponse(BaseModel):
    generated_count: int
    items: list[ActionItemResponse]


class RiskItemResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    source_type: str
    source_id: int | None
    related_requirement_ids: list
    related_response_item_ids: list
    related_clarification_ids: list
    related_evidence_item_ids: list
    risk_category: str
    impact_area: str
    probability: str
    impact: str
    severity: str
    owner: str | None
    status: str
    due_date: str | None
    mitigation_plan: str | None
    contingency_plan: str | None
    trigger_event: str | None
    confidence: float | None
    notes: str | None
    generation_mode: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class RiskItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    risk_category: str | None = None
    impact_area: str | None = None
    probability: str | None = None
    impact: str | None = None
    severity: str | None = None
    owner: str | None = None
    status: str | None = None
    due_date: str | None = None
    mitigation_plan: str | None = None
    contingency_plan: str | None = None
    trigger_event: str | None = None
    notes: str | None = None


class GenerateRiskRegisterResponse(BaseModel):
    generated_count: int
    items: list[RiskItemResponse]

class ComplianceItemResponse(BaseModel):
    id: int
    project_id: int
    requirement_id: int | None
    response_item_id: int | None
    category: str
    requirement_text: str
    compliance_status: str
    score: int
    max_score: int
    weight: float
    owner: str | None
    priority: str
    risk_level: str
    evidence_item_ids: list
    evidence_coverage: str
    gap_summary: str | None
    recommended_action: str | None
    notes: str | None
    source_page: int | None
    confidence: float | None
    generation_mode: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ComplianceItemUpdate(BaseModel):
    compliance_status: str | None = None
    score: int | None = None
    owner: str | None = None
    evidence_coverage: str | None = None
    gap_summary: str | None = None
    recommended_action: str | None = None
    notes: str | None = None


class ComplianceScorecardSummary(BaseModel):
    total_items: int
    weighted_score: float
    score_percent: int
    max_score: float
    status_counts: dict
    category_scores: list
    evidence_coverage_counts: dict
    high_risk_gaps: int
    recommendation: str


class ComplianceScorecardResponse(BaseModel):
    summary: ComplianceScorecardSummary
    items: list[ComplianceItemResponse]


class GenerateComplianceScorecardResponse(BaseModel):
    generated_count: int
    summary: ComplianceScorecardSummary
    items: list[ComplianceItemResponse]

class ApprovalRequestResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    status: str
    current_step_order: int | None
    total_steps: int
    approved_steps: int
    submitted_by: str | None
    submitted_at: datetime | None
    completed_at: datetime | None
    final_decision: str | None
    notes: str | None
    generation_mode: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ApprovalStepResponse(BaseModel):
    id: int
    project_id: int
    approval_request_id: int
    step_order: int
    role: str
    approver_name: str | None
    approver_email: str | None
    status: str
    due_date: str | None
    decision_note: str | None
    decided_by: str | None
    decided_at: datetime | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ApprovalWorkflowSummary(BaseModel):
    status: str
    total_steps: int
    approved_steps: int
    pending_steps: int
    not_started_steps: int
    rejected_steps: int
    changes_requested_steps: int
    current_step_order: int | None
    current_role: str | None
    progress_percent: int


class ApprovalWorkflowResponse(BaseModel):
    summary: ApprovalWorkflowSummary
    request: ApprovalRequestResponse
    steps: list[ApprovalStepResponse]


class GenerateApprovalWorkflowResponse(ApprovalWorkflowResponse):
    pass


class ApprovalWorkflowSubmit(BaseModel):
    submitted_by: str | None = None
    notes: str | None = None


class ApprovalStepUpdate(BaseModel):
    status: str | None = None
    approver_name: str | None = None
    approver_email: str | None = None
    due_date: str | None = None
    decision_note: str | None = None
    decided_by: str | None = None

class DecisionGateHistoryEventResponse(BaseModel):
    id: int
    project_id: int | None
    created_at: datetime
    actor: str | None
    action: str
    event_type: str
    title: str
    summary: str | None
    entity_type: str
    entity_id: int | None
    status_from: str | None
    status_to: str | None
    score_from: int | None = None
    score_to: int | None = None
    target: str | None = None
    changed_fields: list
    details: dict
    before_json: dict | None
    after_json: dict | None
    notes: str | None


class DecisionGateHistorySummaryResponse(BaseModel):
    total_events: int
    decision_events: int
    approval_events: int
    latest_decision_status: str | None
    latest_recommendation: str | None
    readiness_score: int | None
    latest_approval_status: str | None
    approved_steps: int
    pending_steps: int
    rejected_steps: int
    changes_requested_steps: int
    last_event_at: datetime | None
    last_actor: str | None


class DecisionGateApprovalHistoryResponse(BaseModel):
    summary: DecisionGateHistorySummaryResponse
    events: list[DecisionGateHistoryEventResponse]

class AddendumImpactItemResponse(BaseModel):
    id: int
    project_id: int
    document_id: int | None
    source_document_name: str | None
    title: str
    summary: str | None
    impact_type: str
    impacted_artifact: str
    severity: str
    status: str
    source_excerpt: str | None
    recommended_action: str | None
    owner: str | None
    due_date: str | None
    related_requirement_ids: list
    related_response_item_ids: list
    related_clarification_ids: list
    related_compliance_item_ids: list
    related_risk_item_ids: list
    related_approval_step_ids: list
    confidence: float | None
    notes: str | None
    generation_mode: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class AddendumImpactItemUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None
    impact_type: str | None = None
    impacted_artifact: str | None = None
    severity: str | None = None
    status: str | None = None
    recommended_action: str | None = None
    owner: str | None = None
    due_date: str | None = None
    notes: str | None = None


class AddendumImpactGenerateRequest(BaseModel):
    document_id: int | None = None
    notes: str | None = None


class AddendumImpactSummaryResponse(BaseModel):
    total_items: int
    open_items: int
    critical_items: int
    high_items: int
    severity_counts: dict
    artifact_counts: dict
    status_counts: dict
    recommendation: str


class AddendumImpactAnalysisResponse(BaseModel):
    summary: AddendumImpactSummaryResponse
    items: list[AddendumImpactItemResponse]


class AddendumImpactGenerateResponse(AddendumImpactAnalysisResponse):
    generated_count: int

class ClarificationResponseItemResponse(BaseModel):
    id: int
    project_id: int
    clarification_id: int | None
    requirement_id: int | None
    category: str
    question_text: str
    reason: str | None
    client_response: str | None
    response_status: str
    priority: str
    risk_level: str
    owner: str | None
    due_date: str | None
    sent_at: str | None
    response_received_at: str | None
    incorporated_at: str | None
    impacted_artifacts: list
    related_response_item_ids: list
    related_compliance_item_ids: list
    related_risk_item_ids: list
    related_addendum_impact_ids: list
    recommended_follow_up: str | None
    notes: str | None
    confidence: float | None
    generation_mode: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ClarificationResponseItemUpdate(BaseModel):
    client_response: str | None = None
    response_status: str | None = None
    priority: str | None = None
    risk_level: str | None = None
    owner: str | None = None
    due_date: str | None = None
    sent_at: str | None = None
    response_received_at: str | None = None
    incorporated_at: str | None = None
    recommended_follow_up: str | None = None
    notes: str | None = None


class ClarificationResponseSummaryResponse(BaseModel):
    total_items: int
    open_items: int
    answered_items: int
    overdue_items: int
    high_priority_items: int
    high_risk_items: int
    completion_percent: int
    status_counts: dict
    priority_counts: dict
    risk_counts: dict
    recommendation: str


class ClarificationResponseTrackerResponse(BaseModel):
    summary: ClarificationResponseSummaryResponse
    items: list[ClarificationResponseItemResponse]


class ClarificationResponseGenerateResponse(ClarificationResponseTrackerResponse):
    generated_count: int

