import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { AlertTriangle, CheckCircle2, ClipboardCheck, FileQuestion, FileText, History, LayoutDashboard, MessageSquare, Plus, RefreshCw, ShieldCheck, Upload } from "lucide-react";
import "./style.css";
import ProjectViewTabs from "./components/ProjectViewTabs.jsx";
import RequirementsView from "./views/RequirementsView.jsx";
import ClarificationsView from "./views/ClarificationsView.jsx";
import ActionStat from "./components/ActionStat.jsx";
import ExecutiveMetric from "./components/ExecutiveMetric.jsx";
import ExecutiveStage from "./components/ExecutiveStage.jsx";
import EvidenceStat from "./components/EvidenceStat.jsx";
import RiskStat from "./components/RiskStat.jsx";
import ComplianceMetric from "./components/ComplianceMetric.jsx";
import ComplianceRelationBox from "./components/ComplianceRelationBox.jsx";
import DecisionList from "./components/DecisionList.jsx";
import MetadataField from "./components/MetadataField.jsx";
import BriefList from "./components/BriefList.jsx";
import RelationBox from "./components/RelationBox.jsx";
import ResponseList from "./components/ResponseList.jsx";
import ProposalList from "./components/ProposalList.jsx";
import ResponseItemDetail from "./components/ResponseItemDetail.jsx";
import ProposalSectionDetail from "./components/ProposalSectionDetail.jsx";
import EvidenceItemDetail from "./components/EvidenceItemDetail.jsx";
import ActionItemCard from "./components/ActionItemCard.jsx";
import DecisionGateCard from "./components/DecisionGateCard.jsx";
import RfpMetadataCard from "./components/RfpMetadataCard.jsx";
import BidBriefCard from "./components/BidBriefCard.jsx";
import ReadinessSummaryCard from "./components/ReadinessSummaryCard.jsx";
import LanguageSelector from "./components/LanguageSelector.jsx";
import ActorSelector from "./components/ActorSelector.jsx";
import AuditLogView from "./views/AuditLogView.jsx";
import DecisionGateHistoryView from "./views/DecisionGateHistoryView.jsx";
import { L, translateRequirementTextForUi } from "./utils/i18n.js";
import { apiFetch } from "./api/client.js";
import { useAuthSession } from "./hooks/useAuthSession.js";
import { useActorName } from "./hooks/useActorName.js";
import { useTenderDownloads } from "./hooks/useTenderDownloads.js";
import { useTenderSimpleUpdates } from "./hooks/useTenderSimpleUpdates.js";
import { useTenderItemUpdates } from "./hooks/useTenderItemUpdates.js";
import { useTenderBulkUpdates } from "./hooks/useTenderBulkUpdates.js";
import { useTenderGenerators } from "./hooks/useTenderGenerators.js";
import { useTenderPostMvpGenerators } from "./hooks/useTenderPostMvpGenerators.js";
import { useTenderPostMvpUpdates } from "./hooks/useTenderPostMvpUpdates.js";
import { useTenderScoreRiskActionUpdates } from "./hooks/useTenderScoreRiskActionUpdates.js";
import { useTenderScoreRiskActionGenerators } from "./hooks/useTenderScoreRiskActionGenerators.js";
import { useTenderMetadataDecisionGate } from "./hooks/useTenderMetadataDecisionGate.js";
import { useTenderLanguageTemplate } from "./hooks/useTenderLanguageTemplate.js";
import { useTenderApprovalDecision } from "./hooks/useTenderApprovalDecision.js";
import { useTenderProjectIntake } from "./hooks/useTenderProjectIntake.js";
import { useTenderRequirementEvidence } from "./hooks/useTenderRequirementEvidence.js";
import AuthPanel from "./components/AuthPanel.jsx";
import ExecutiveDashboardCard from "./components/ExecutiveDashboardCard.jsx";
import SummaryView from "./views/SummaryView.jsx";

const emptyProjectForm = {
  title: "",
  issuer: "",
  tender_type: "",
};

function App() {
  const [apiStatus, setApiStatus] = useState("checking");
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);

  const [projectForm, setProjectForm] = useState(emptyProjectForm);
  const [documents, setDocuments] = useState([]);
  const [requirements, setRequirements] = useState([]);
  const [clarifications, setClarifications] = useState([]);
  const [responsePlan, setResponsePlan] = useState([]);
  const [proposalOutline, setProposalOutline] = useState([]);
  const [evidencePack, setEvidencePack] = useState([]);
  const [decisionGate, setDecisionGate] = useState(null);
  const [decisionGateHistory, setDecisionGateHistory] = useState({ summary: null, events: [] });
  const [addendumImpacts, setAddendumImpacts] = useState({ summary: null, items: [] });
  const [clarificationTracker, setClarificationTracker] = useState({ summary: null, items: [] });
  const [proposalTemplate, setProposalTemplate] = useState(null);
  const [complianceScorecard, setComplianceScorecard] = useState({ summary: null, items: [] });
  const [approvalWorkflow, setApprovalWorkflow] = useState({ summary: null, request: null, steps: [] });
  const [riskItems, setRiskItems] = useState([]);
  const [actionItems, setActionItems] = useState([]);
  const [languageSetting, setLanguageSetting] = useState({
    input_language: "auto",
    output_language: "en",
  });
  const [auditLogs, setAuditLogs] = useState([]);
  const [readinessSummary, setReadinessSummary] = useState(null);
  const [projectMetadata, setProjectMetadata] = useState(null);
  const [bidBrief, setBidBrief] = useState(null);
  const [requirementEvidence, setRequirementEvidence] = useState(null);

  const [selectedRequirementId, setSelectedRequirementId] = useState(null);
  const [selectedClarificationId, setSelectedClarificationId] = useState(null);
  const [selectedResponseItemId, setSelectedResponseItemId] = useState(null);
  const [selectedProposalSectionId, setSelectedProposalSectionId] = useState(null);
  const [selectedEvidenceItemId, setSelectedEvidenceItemId] = useState(null);
  const [activeProjectView, setActiveProjectView] = useState("summary");

  const [uploadFile, setUploadFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [actorName, setActorName] = useActorName();

  const {
    authUser,
    authToken,
    authForm,
    setAuthForm,
    loginWithPassword,
    logoutUser,
  } = useAuthSession({ setBusy, setMessage, setActorName });

  const {
    downloadReadinessMatrix,
    downloadProposalDraft,
    downloadExecutivePack,
  } = useTenderDownloads({
    selectedProjectId,
    requirements,
    proposalOutline,
    setBusy,
    setMessage,
  });

  const {
    updateRequirement,
    updateClarification,
  } = useTenderSimpleUpdates({
    selectedProjectId,
    setBusy,
    setMessage,
    setSelectedRequirementId,
    setSelectedClarificationId,
    loadProjectData,
  });

  const {
    updateResponseItem,
    updateProposalSection,
    updateEvidenceItem,
  } = useTenderItemUpdates({
    selectedProjectId,
    setBusy,
    setMessage,
    setSelectedResponseItemId,
    setSelectedProposalSectionId,
    setSelectedEvidenceItemId,
    loadProjectData,
  });

  const {
    bulkUpdateRequirements,
    bulkUpdateClarifications,
  } = useTenderBulkUpdates({
    selectedProjectId,
    setBusy,
    setMessage,
    loadProjectData,
  });

  const {
    generateClarifications,
    generateResponsePlan,
    generateProposalOutline,
    generateEvidencePack,
  } = useTenderGenerators({
    selectedProjectId,
    actorName,
    setBusy,
    setMessage,
    setActiveProjectView,
    setSelectedClarificationId,
    setSelectedResponseItemId,
    setSelectedProposalSectionId,
    setSelectedEvidenceItemId,
    loadProjectData,
  });

  const {
    generateClarificationResponseTracker,
    generateAddendumImpactAnalysis,
    generateApprovalWorkflow,
  } = useTenderPostMvpGenerators({
    selectedProjectId,
    actorName,
    setBusy,
    setMessage,
    setActiveProjectView,
    setClarificationTracker,
    setAddendumImpacts,
    setApprovalWorkflow,
  });

  const {
    updateClarificationResponseItem,
    updateAddendumImpactItem,
    updateApprovalStep,
  } = useTenderPostMvpUpdates({
    selectedProjectId,
    actorName,
    setBusy,
    setMessage,
    setClarificationTracker,
    setAddendumImpacts,
    setApprovalWorkflow,
    loadProjectData,
  });

  const {
    updateComplianceItem,
    updateRiskItem,
    updateActionItem,
  } = useTenderScoreRiskActionUpdates({
    actorName,
    setBusy,
    setMessage,
    setComplianceScorecard,
    setRiskItems,
    setActionItems,
  });

  const {
    generateComplianceScorecard,
    generateRiskRegister,
    generateActionItems,
  } = useTenderScoreRiskActionGenerators({
    selectedProjectId,
    actorName,
    setBusy,
    setMessage,
    setActiveProjectView,
    setComplianceScorecard,
    setRiskItems,
    setActionItems,
  });

  const {
    extractMetadata,
    generateDecisionGate,
  } = useTenderMetadataDecisionGate({
    selectedProjectId,
    documents,
    actorName,
    setBusy,
    setMessage,
    setProjectMetadata,
    setDecisionGate,
    setActiveProjectView,
    loadProjectData,
  });

  const {
    updateLanguageSetting,
    updateProposalTemplate,
  } = useTenderLanguageTemplate({
    selectedProjectId,
    actorName,
    setBusy,
    setMessage,
    setLanguageSetting,
    setProposalTemplate,
  });

  const {
    submitApprovalWorkflow,
    updateDecisionGate,
  } = useTenderApprovalDecision({
    selectedProjectId,
    actorName,
    setBusy,
    setMessage,
    setApprovalWorkflow,
    setDecisionGate,
    setActiveProjectView,
    loadProjectData,
  });

  const {
    createProject,
    uploadDocument,
    analyzeRfp,
  } = useTenderProjectIntake({
    emptyProjectForm,
    selectedProjectId,
    projectForm,
    uploadFile,
    setBusy,
    setMessage,
    setProjectForm,
    setSelectedProjectId,
    setSelectedRequirementId,
    setActiveProjectView,
    setUploadFile,
    loadProjects,
    loadProjectData,
  });

  const {
    loadRequirementEvidence,
  } = useTenderRequirementEvidence({
    setMessage,
    setRequirementEvidence,
  });

  const selectedProject = useMemo(() => {
    return projects.find((item) => item.id === Number(selectedProjectId)) || null;
  }, [projects, selectedProjectId]);

  const selectedRequirement = useMemo(() => {
    return requirements.find((item) => item.id === Number(selectedRequirementId)) || requirements[0] || null;
  }, [requirements, selectedRequirementId]);

  const selectedClarification = useMemo(() => {
    return clarifications.find((item) => item.id === Number(selectedClarificationId)) || clarifications[0] || null;
  }, [clarifications, selectedClarificationId]);

  const selectedResponseItem = useMemo(() => {
    return responsePlan.find((item) => item.id === Number(selectedResponseItemId)) || responsePlan[0] || null;
  }, [responsePlan, selectedResponseItemId]);

  const selectedProposalSection = useMemo(() => {
    return proposalOutline.find((item) => item.id === Number(selectedProposalSectionId)) || proposalOutline[0] || null;
  }, [proposalOutline, selectedProposalSectionId]);

  const selectedEvidenceItem = useMemo(() => {
    return evidencePack.find((item) => item.id === Number(selectedEvidenceItemId)) || evidencePack[0] || null;
  }, [evidencePack, selectedEvidenceItemId]);

  async function checkHealth() {
    try {
      const data = await apiFetch("/api/health");
      setApiStatus(data.status || "unknown");
    } catch {
      setApiStatus("offline");
    }
  }

  async function loadProjects() {
    try {
      const data = await apiFetch("/api/v1/projects");
      setProjects(data);

      if (!selectedProjectId && data.length > 0) {
        setSelectedProjectId(data[0].id);
      }
    } catch (err) {
      setMessage(`Failed to load bid projects: ${err.message}`);
    }
  }

  async function loadProjectData(projectId) {
    if (!projectId) return;

    try {
      const [docs, reqs, qs, responseItems, proposalSections, evidenceItems, gate, gateHistory, addendumImpactData, clarificationTrackerData, proposalTemplateData, approvalData, complianceData, riskItemsData, actionItemsData, language, audits, summary, metadata, brief] = await Promise.all([
        apiFetch(`/api/v1/projects/${projectId}/documents`).catch(() => []),
        apiFetch(`/api/v1/projects/${projectId}/requirements`).catch(() => []),
        apiFetch(`/api/v1/projects/${projectId}/clarifications`).catch(() => []),
        apiFetch(`/api/v1/projects/${projectId}/response-plan`).catch(() => []),
        apiFetch(`/api/v1/projects/${projectId}/proposal-outline`).catch(() => []),
        apiFetch(`/api/v1/projects/${projectId}/evidence-pack`).catch(() => []),
        apiFetch(`/api/v1/projects/${projectId}/decision-gate`).catch(() => null),
        apiFetch(`/api/v1/projects/${projectId}/decision-gate-history`).catch(() => ({ summary: null, events: [] })),
        apiFetch(`/api/v1/projects/${projectId}/addendum-impacts`).catch(() => ({ summary: null, items: [] })),
        apiFetch(`/api/v1/projects/${projectId}/clarification-response-tracker`).catch(() => ({ summary: null, items: [] })),
        apiFetch(`/api/v1/projects/${projectId}/proposal-template`).catch(() => null),
        apiFetch(`/api/v1/projects/${projectId}/approval-workflow`).catch(() => ({ summary: null, request: null, steps: [] })),
        apiFetch(`/api/v1/projects/${projectId}/compliance-scorecard`).catch(() => ({ summary: null, items: [] })),
        apiFetch(`/api/v1/projects/${projectId}/risk-register`).catch(() => []),
        apiFetch(`/api/v1/projects/${projectId}/action-items`).catch(() => []),
        apiFetch(`/api/v1/projects/${projectId}/language`).catch(() => ({
          input_language: "auto",
          output_language: "en",
        })),
        apiFetch(`/api/v1/projects/${projectId}/audit-logs`).catch(() => []),
        apiFetch(`/api/v1/projects/${projectId}/readiness-summary`).catch(() => null),
        apiFetch(`/api/v1/projects/${projectId}/metadata`).catch(() => null),
        apiFetch(`/api/v1/projects/${projectId}/bid-brief`).catch(() => null),
      ]);

      setDocuments(docs);
      setRequirements(reqs);
      setClarifications(qs);
      setResponsePlan(responseItems);
      setProposalOutline(proposalSections);
      setEvidencePack(evidenceItems);
      setDecisionGate(gate);
      setDecisionGateHistory(gateHistory || { summary: null, events: [] });
      setAddendumImpacts(addendumImpactData || { summary: null, items: [] });
      setClarificationTracker(clarificationTrackerData || { summary: null, items: [] });
      setProposalTemplate(proposalTemplateData || null);
      setApprovalWorkflow(approvalData || { summary: null, request: null, steps: [] });
      setComplianceScorecard(complianceData || { summary: null, items: [] });
      setRiskItems(riskItemsData || []);
      setActionItems(actionItemsData || []);
      setLanguageSetting(language || { input_language: "auto", output_language: "en" });
      setAuditLogs(audits);
      setReadinessSummary(summary);
      setProjectMetadata(metadata);
      setBidBrief(brief);

      if (reqs.length > 0 && !reqs.find((item) => item.id === Number(selectedRequirementId))) {
        setSelectedRequirementId(reqs[0].id);
      }

      if (qs.length > 0 && !qs.find((item) => item.id === Number(selectedClarificationId))) {
        setSelectedClarificationId(qs[0].id);
      }

      if (responseItems.length > 0 && !responseItems.find((item) => item.id === Number(selectedResponseItemId))) {
        setSelectedResponseItemId(responseItems[0].id);
      }

      if (proposalSections.length > 0 && !proposalSections.find((item) => item.id === Number(selectedProposalSectionId))) {
        setSelectedProposalSectionId(proposalSections[0].id);
      }

      if (typeof evidenceItems !== "undefined" && evidenceItems.length > 0 && !evidenceItems.find((item) => item.id === Number(selectedEvidenceItemId))) {
        setSelectedEvidenceItemId(evidenceItems[0].id);
      }
    } catch (err) {
      setMessage(`Failed to load project data: ${err.message}`);
    }
  }


  useEffect(() => {
    checkHealth();
    loadProjects();
  }, []);

useEffect(() => {
    if (selectedProjectId) {
      loadProjectData(selectedProjectId);
    }
  }, [selectedProjectId]);

  useEffect(() => {
    if (selectedRequirementId) {
      loadRequirementEvidence(selectedRequirementId);
    } else {
      setRequirementEvidence(null);
    }
  }, [selectedRequirementId]);









  async function regenerateAllArtifacts() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    if (requirements.length === 0) {
      setMessage("Analyze RFP first before regenerating all artifacts.");
      return;
    }

    let currentStep = "starting";

    setBusy(true);
    setMessage("Regenerating all artifacts...");

    try {
      const steps = [
        {
          label: "clarifications",
          path: `/api/v1/projects/${selectedProjectId}/generate-clarifications`,
        },
        {
          label: "response plan",
          path: `/api/v1/projects/${selectedProjectId}/generate-response-plan`,
        },
        {
          label: "proposal outline",
          path: `/api/v1/projects/${selectedProjectId}/generate-proposal-outline`,
        },
        {
          label: "evidence pack",
          path: `/api/v1/projects/${selectedProjectId}/generate-evidence-pack`,
        },
        {
          label: "decision gate",
          path: `/api/v1/projects/${selectedProjectId}/generate-decision-gate`,
        },
        {
          label: "compliance scorecard",
          path: `/api/v1/projects/${selectedProjectId}/generate-compliance-scorecard`,
        },
        {
          label: "risk register",
          path: `/api/v1/projects/${selectedProjectId}/generate-risk-register`,
        },
        {
          label: "approval workflow",
          path: `/api/v1/projects/${selectedProjectId}/generate-approval-workflow`,
        },
        {
          label: "addendum impact analysis",
          path: `/api/v1/projects/${selectedProjectId}/generate-addendum-impact-analysis`,
        },
        {
          label: "clarification response tracker",
          path: `/api/v1/projects/${selectedProjectId}/generate-clarification-response-tracker`,
        },
      ];

      for (const step of steps) {
        currentStep = step.label;
        setMessage(`Regenerating ${step.label}...`);

        await apiFetch(step.path, {
          method: "POST",
          headers: {
            "X-Actor": actorName,
          },
        });
      }

      await loadProjectData(selectedProjectId);
      setActiveProjectView("summary");
      setMessage("All artifacts regenerated successfully.");
    } catch (err) {
      setMessage(`Regenerate all artifacts failed at ${currentStep}: ${err.message}`);
      await loadProjectData(selectedProjectId);
    } finally {
      setBusy(false);
    }
  }


  return (
    <main className="page workspacePage">
      <section className="hero brandHero">
        <img className="brandMark" src="/brand/bidready-mark.svg" alt="BidReady AI logo" />
        <div>
          <p className="eyebrow">Tender Intelligence Platform</p>
          <h1>BidReady AI</h1>
          <p className="subtitle">
            Tender Intelligence Platform for RFP analysis, bid readiness, clarification management, evidence tracking, and executive tender reporting.
          </p>
          <div className={`status ${apiStatus === "ok" ? "ok" : "bad"}`}>
            API Status: {apiStatus}
          </div>
        </div>
      </section>

      {message && <div className="notice">{message}</div>}

      <section className="layout workspaceLayout">
        <aside className="panel workspaceSidebar">
          <div className="panelHeader">
            <h2>Create Bid Project</h2>
            <Plus />
          </div>

          <form onSubmit={createProject} className="form">
            <label>
              Bid / RFP Title
              <input
                value={projectForm.title}
                onChange={(e) => setProjectForm({ ...projectForm, title: e.target.value })}
                placeholder="Enterprise RFP - Managed Services"
              />
            </label>

            <label>
              Client / Issuer
              <input
                value={projectForm.issuer}
                onChange={(e) => setProjectForm({ ...projectForm, issuer: e.target.value })}
                placeholder="Client / Issuer"
              />
            </label>

            <label>
              Service Domain
              <input
                value={projectForm.tender_type}
                onChange={(e) => setProjectForm({ ...projectForm, tender_type: e.target.value })}
                placeholder="Application / Cloud / Managed Services"
              />
            </label>

            



            <button disabled={busy} type="submit">
              Create Bid Project
            </button>
          </form>

          <div className="divider" />

          <div className="panelHeader">
            <h2>Bid Projects</h2>
            <button className="iconButton" onClick={loadProjects} disabled={busy}>
              <RefreshCw size={16} />
            </button>
          </div>

          <div className="projectList">
            {projects.map((project) => (
              <button
                key={project.id}
                className={`projectItem ${Number(selectedProjectId) === project.id ? "active" : ""}`}
                onClick={() => {
                  setSelectedProjectId(project.id);
                  setActiveProjectView("summary");
                }}
              >
                <strong>{project.title}</strong>
                <span>{project.issuer || "No issuer"} · {project.status}</span>
              </button>
            ))}

            {projects.length === 0 && <p className="empty">No bid project yet.</p>}
          </div>
        </aside>

        <section className="mainPanel projectWorkspace">
          <div className="workspaceTop">
            <div>
              <p className="eyebrow dark">Project Workspace</p>
              <h2>{selectedProject ? selectedProject.title : "Select a bid project"}</h2>
              {selectedProject && (
                <p className="muted">
                  Project #{selectedProject.id} · {selectedProject.issuer || "No issuer"} ·{" "}
                  {selectedProject.tender_type || "No domain"} · {selectedProject.status}
                </p>
              )}
            </div>

            <div className="workspaceHeaderControls">
              <LanguageSelector
                languageSetting={languageSetting}
                updateLanguageSetting={updateLanguageSetting}
                busy={busy}
              />
              <ActorSelector actorName={actorName} setActorName={setActorName} />
            </div>
          </div>
          <AuthPanel
            authUser={authUser}
            authToken={authToken}
            authForm={authForm}
            setAuthForm={setAuthForm}
            loginWithPassword={loginWithPassword}
            logoutUser={logoutUser}
            busy={busy}
          />

          <ProjectViewTabs
            activeProjectView={activeProjectView}
            setActiveProjectView={setActiveProjectView}
            busy={busy}
            downloadExecutivePack={downloadExecutivePack}
            selectedProjectId={selectedProjectId}
            proposalTemplate={proposalTemplate}
            clarificationTracker={clarificationTracker}
            addendumImpacts={addendumImpacts}
            decisionGateHistory={decisionGateHistory}
            approvalWorkflow={approvalWorkflow}
            complianceScorecard={complianceScorecard}
            riskItems={riskItems}
            actionItems={actionItems}
          />

          {activeProjectView === "summary" && (
            <SummaryView
              selectedProject={selectedProject}
              readinessSummary={readinessSummary}
              projectMetadata={projectMetadata}
              bidBrief={bidBrief}
              responsePlan={responsePlan}
              proposalOutline={proposalOutline}
              evidencePack={evidencePack}
              decisionGate={decisionGate}
              documents={documents}
              requirements={requirements}
              clarifications={clarifications}
              auditLogs={auditLogs}
              uploadFile={uploadFile}
              setUploadFile={setUploadFile}
              uploadDocument={uploadDocument}
              analyzeRfp={analyzeRfp}
              generateClarifications={generateClarifications}
              generateResponsePlan={generateResponsePlan}
              generateProposalOutline={generateProposalOutline}
              generateDecisionGate={generateDecisionGate}
              regenerateAllArtifacts={regenerateAllArtifacts}
              updateDecisionGate={updateDecisionGate}
              extractMetadata={extractMetadata}
              busy={busy}
              selectedProjectId={selectedProjectId}
              downloadReadinessMatrix={downloadReadinessMatrix}
              downloadProposalDraft={downloadProposalDraft}
            />
          )}

          {activeProjectView === "requirements" && (
            <RequirementsView
                uiLanguage={languageSetting?.output_language || languageSetting?.outputLanguage || languageSetting?.output || "en"}
              requirements={requirements}
              selectedRequirement={selectedRequirement}
              setSelectedRequirementId={setSelectedRequirementId}
              busy={busy}
              updateRequirement={updateRequirement}
              requirementEvidence={requirementEvidence}
              bulkUpdateRequirements={bulkUpdateRequirements}
            />
          )}

          {activeProjectView === "clarifications" && (
            <ClarificationsView
              clarifications={clarifications}
              selectedClarification={selectedClarification}
              setSelectedClarificationId={setSelectedClarificationId}
              busy={busy}
              updateClarification={updateClarification}
              generateClarifications={generateClarifications}
              requirements={requirements}
              bulkUpdateClarifications={bulkUpdateClarifications}
            />
          )}

          {activeProjectView === "response" && (
            <ResponsePlanView
              responsePlan={responsePlan}
              selectedResponseItem={selectedResponseItem}
              setSelectedResponseItemId={setSelectedResponseItemId}
              busy={busy}
              updateResponseItem={updateResponseItem}
              generateResponsePlan={generateResponsePlan}
              requirements={requirements}
            />
          )}

          {activeProjectView === "proposal" && (
            <ProposalOutlineView
              proposalOutline={proposalOutline}
              selectedProposalSection={selectedProposalSection}
              setSelectedProposalSectionId={setSelectedProposalSectionId}
              busy={busy}
              updateProposalSection={updateProposalSection}
              generateProposalOutline={generateProposalOutline}
              responsePlan={responsePlan}
              downloadProposalDraft={downloadProposalDraft}
            />
          )}

          {activeProjectView === "evidence" && (
            <EvidencePackView
              evidencePack={evidencePack}
              decisionGate={decisionGate}
              selectedEvidenceItem={selectedEvidenceItem}
              setSelectedEvidenceItemId={setSelectedEvidenceItemId}
              busy={busy}
              updateEvidenceItem={updateEvidenceItem}
              generateEvidencePack={generateEvidencePack}
              generateDecisionGate={generateDecisionGate}
              updateDecisionGate={updateDecisionGate}
              projectMetadata={projectMetadata}
              responsePlan={responsePlan}
              proposalOutline={proposalOutline}
            />
          )}

          {activeProjectView === "compliance" && (
            <ComplianceScorecardView
              complianceScorecard={complianceScorecard}
              busy={busy}
              generateComplianceScorecard={generateComplianceScorecard}
              updateComplianceItem={updateComplianceItem}
            />
          )}

          {activeProjectView === "approvals" && (
            <ApprovalWorkflowView
              approvalWorkflow={approvalWorkflow}
              busy={busy}
              actorName={actorName}
              generateApprovalWorkflow={generateApprovalWorkflow}
              submitApprovalWorkflow={submitApprovalWorkflow}
              updateApprovalStep={updateApprovalStep}
            />
          )}

          {activeProjectView === "risks" && (
            <RiskRegisterView
              riskItems={riskItems}
              busy={busy}
              generateRiskRegister={generateRiskRegister}
              updateRiskItem={updateRiskItem}
            />
          )}

          {activeProjectView === "actions" && (
            <ActionTrackerView
              actionItems={actionItems}
              busy={busy}
              generateActionItems={generateActionItems}
              updateActionItem={updateActionItem}
            />
          )}

          {activeProjectView === "gateHistory" && (
            <DecisionGateHistoryView decisionGateHistory={decisionGateHistory} />
          )}

          {activeProjectView === "addendum" && (
            <AddendumImpactView
              addendumImpacts={addendumImpacts}
              busy={busy}
              generateAddendumImpactAnalysis={generateAddendumImpactAnalysis}
              updateAddendumImpactItem={updateAddendumImpactItem}
            />
          )}

          {activeProjectView === "clarificationTracker" && (
            <ClarificationResponseTrackerView
              clarificationTracker={clarificationTracker}
              busy={busy}
              generateClarificationResponseTracker={generateClarificationResponseTracker}
              updateClarificationResponseItem={updateClarificationResponseItem}
            />
          )}

          {activeProjectView === "executivePack" && (
            <div className="workspaceView executivePackView">
              <div className="viewHeader">
                <div>
                  <p className="eyebrow">Executive Pack</p>
                  <h2>One-click executive export package</h2>
                  <p className="muted">
                    Download ZIP package containing Excel report, DOCX proposal draft, executive summary, governance snapshots, risks, actions, clarifications, addendum impact, and audit logs.
                  </p>
                </div>
              </div>

              <div className="sectionBox">
                <h3>Included Files</h3>
                <ul className="compactList">
                  <li>bidready_ai_tender_report.xlsx</li>
                  <li>bidready_ai_proposal_draft.docx</li>
                  <li>executive_summary.md / executive_summary.json</li>
                  <li>decision_gate.json and decision_gate_history.json</li>
                  <li>approval_workflow.json, compliance_scorecard.json, risk_register.json</li>
                  <li>action_tracker.json, clarification_response_tracker.json, addendum_impact_analysis.json</li>
                  <li>audit_logs.json</li>
                </ul>
              </div>
            </div>
          )}

          {activeProjectView === "template" && (
            <ProposalTemplateView
              proposalTemplate={proposalTemplate}
              busy={busy}
              updateProposalTemplate={updateProposalTemplate}
              downloadExecutivePack={downloadExecutivePack}
            />
          )}

          {activeProjectView === "audit" && (
            <AuditLogView auditLogs={auditLogs} />
          )}
        </section>
      </section>
    </main>
  );
}

function ResponsePlanView({
  responsePlan,
  selectedResponseItem,
  setSelectedResponseItemId,
  busy,
  updateResponseItem,
  generateResponsePlan,
  requirements,
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [complianceFilter, setComplianceFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");

  const categories = Array.from(new Set(responsePlan.map((item) => item.category).filter(Boolean))).sort();

  const filteredItems = responsePlan.filter((item) => {
    const query = searchQuery.trim().toLowerCase();

    const matchesSearch =
      !query ||
      item.requirement_text?.toLowerCase().includes(query) ||
      item.draft_response?.toLowerCase().includes(query) ||
      item.response_strategy?.toLowerCase().includes(query) ||
      item.category?.toLowerCase().includes(query) ||
      item.owner?.toLowerCase().includes(query) ||
      item.status?.toLowerCase().includes(query) ||
      item.compliance_status?.toLowerCase().includes(query);

    const matchesCompliance = complianceFilter === "all" || item.compliance_status === complianceFilter;
    const matchesStatus = statusFilter === "all" || item.status === statusFilter;
    const matchesCategory = categoryFilter === "all" || item.category === categoryFilter;

    return matchesSearch && matchesCompliance && matchesStatus && matchesCategory;
  });

  return (
    <div className="workspaceView">
      <div className="viewHeader">
        <div>
          <h3>Response Plan</h3>
          <p className="muted">Convert reviewed requirements into compliance status, response strategy, draft response, and evidence checklist.</p>
        </div>
        <div className="viewHeaderActions">
          <span className="filterResultCount">
            {filteredItems.length} / {responsePlan.length} {L("shown", "ditampilkan")}
          </span>
          <button disabled={busy || requirements.length === 0} onClick={generateResponsePlan}>
            Generate Response Plan
          </button>
        </div>
      </div>

      <div className="filterBar responsePlanFilterBar">
        <input
          className="filterInput"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search requirement, draft response, owner, category, or compliance..."
        />

        <select className="filterSelect" value={complianceFilter} onChange={(e) => setComplianceFilter(e.target.value)}>
          <option value="all">All compliance</option>
          <option value="likely_compliant">likely_compliant</option>
          <option value="partially_compliant">partially_compliant</option>
          <option value="non_compliant">non_compliant</option>
          <option value="needs_review">needs_review</option>
          <option value="needs_clarification">needs_clarification</option>
          <option value="blocked">blocked</option>
        </select>

        <select className="filterSelect" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">{L("All statuses", "Semua status")}</option>
          <option value="draft">draft</option>
          <option value="in_review">in_review</option>
          <option value="ready">ready</option>
          <option value="approved">approved</option>
          <option value="blocked">blocked</option>
        </select>

        <select className="filterSelect" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
          <option value="all">{L("All categories", "Semua kategori")}</option>
          {categories.map((category) => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>

        <button
          type="button"
          className="clearFilterButton"
          onClick={() => {
            setSearchQuery("");
            setComplianceFilter("all");
            setStatusFilter("all");
            setCategoryFilter("all");
          }}
        >
          Clear
        </button>
      </div>

      <div className="reviewWorkbench">
        <div className="reviewList">
          {filteredItems.map((item) => (
            <button
              key={item.id}
              className={selectedResponseItem?.id === item.id ? "reviewItem active" : "reviewItem"}
              onClick={() => setSelectedResponseItemId(item.id)}
            >
              <div className="reviewItemTop">
                <span className={`miniCompliance ${item.compliance_status}`}>{item.compliance_status}</span>
                <span className="miniCategory">{item.category}</span>
              </div>
              <strong>{item.requirement_text}</strong>
              <small>{item.owner || "No owner"} · {item.status}</small>
            </button>
          ))}
          {responsePlan.length === 0 && <p className="empty">No response plan generated yet.</p>}
          {responsePlan.length > 0 && filteredItems.length === 0 && <p className="empty">No matching response item.</p>}
        </div>

        <div className="detailPanel">
          {selectedResponseItem ? (
            <ResponseItemDetail
              item={selectedResponseItem}
              busy={busy}
              updateResponseItem={updateResponseItem}
            />
          ) : (
            <p className="empty">Select a response item.</p>
          )}
        </div>
      </div>
    </div>
  );
}

function ProposalOutlineView({
  proposalOutline,
  selectedProposalSection,
  setSelectedProposalSectionId,
  busy,
  updateProposalSection,
  generateProposalOutline,
  responsePlan,
  downloadProposalDraft,
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [ownerFilter, setOwnerFilter] = useState("all");

  const owners = Array.from(new Set(proposalOutline.map((item) => item.owner).filter(Boolean))).sort();

  const filteredSections = proposalOutline.filter((section) => {
    const query = searchQuery.trim().toLowerCase();

    const matchesSearch =
      !query ||
      section.title?.toLowerCase().includes(query) ||
      section.purpose?.toLowerCase().includes(query) ||
      section.draft_content?.toLowerCase().includes(query) ||
      section.owner?.toLowerCase().includes(query) ||
      section.status?.toLowerCase().includes(query) ||
      (section.content_outline || []).join(" ").toLowerCase().includes(query);

    const matchesStatus = statusFilter === "all" || section.status === statusFilter;
    const matchesOwner = ownerFilter === "all" || section.owner === ownerFilter;

    return matchesSearch && matchesStatus && matchesOwner;
  });

  return (
    <div className="workspaceView">
      <div className="viewHeader">
        <div>
          <h3>Proposal Outline</h3>
          <p className="muted">Build an editable proposal structure from the response plan, evidence checklist, risks, and owners.</p>
        </div>
        <div className="viewHeaderActions">
          <span className="filterResultCount">
            {filteredSections.length} / {proposalOutline.length} {L("shown", "ditampilkan")}
          </span>
          <button disabled={busy || responsePlan.length === 0} onClick={generateProposalOutline}>
            Generate Proposal Outline
          </button>
          <button disabled={busy || proposalOutline.length === 0} onClick={downloadProposalDraft}>
            Download DOCX
          </button>
        </div>
      </div>

      <div className="filterBar proposalOutlineFilterBar">
        <input
          className="filterInput"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search section, purpose, draft content, owner, or status..."
        />

        <select className="filterSelect" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">{L("All statuses", "Semua status")}</option>
          <option value="draft">draft</option>
          <option value="in_review">in_review</option>
          <option value="ready">ready</option>
          <option value="approved">approved</option>
          <option value="blocked">blocked</option>
        </select>

        <select className="filterSelect" value={ownerFilter} onChange={(e) => setOwnerFilter(e.target.value)}>
          <option value="all">All owners</option>
          {owners.map((owner) => (
            <option key={owner} value={owner}>{owner}</option>
          ))}
        </select>

        <button
          type="button"
          className="clearFilterButton"
          onClick={() => {
            setSearchQuery("");
            setStatusFilter("all");
            setOwnerFilter("all");
          }}
        >
          Clear
        </button>
      </div>

      <div className="reviewWorkbench proposalWorkbench">
        <div className="reviewList">
          {filteredSections.map((section) => (
            <button
              key={section.id}
              className={selectedProposalSection?.id === section.id ? "reviewItem active proposalItem" : "reviewItem proposalItem"}
              onClick={() => setSelectedProposalSectionId(section.id)}
            >
              <div className="reviewItemTop">
                <span className="sectionOrder">{section.section_order}</span>
                <span className={`miniProposalStatus ${section.status}`}>{section.status}</span>
              </div>
              <strong>{section.title}</strong>
              <small>{section.owner || "No owner"} · {section.section_key}</small>
            </button>
          ))}
          {proposalOutline.length === 0 && <p className="empty">No proposal outline generated yet.</p>}
          {proposalOutline.length > 0 && filteredSections.length === 0 && <p className="empty">No matching proposal section.</p>}
        </div>

        <div className="detailPanel">
          {selectedProposalSection ? (
            <ProposalSectionDetail
              section={selectedProposalSection}
              busy={busy}
              updateProposalSection={updateProposalSection}
            />
          ) : (
            <p className="empty">Select a proposal section.</p>
          )}
        </div>
      </div>
    </div>
  );
}

function EvidencePackView({
  evidencePack = [],
  selectedEvidenceItem,
  setSelectedEvidenceItemId,
  busy,
  updateEvidenceItem,
  generateEvidencePack,
  projectMetadata,
  responsePlan = [],
  proposalOutline = [],
}) {
  const safeEvidencePack = Array.isArray(evidencePack) ? evidencePack : [];
  const safeResponsePlan = Array.isArray(responsePlan) ? responsePlan : [];
  const safeProposalOutline = Array.isArray(proposalOutline) ? proposalOutline : [];

  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [ownerFilter, setOwnerFilter] = useState("all");

  const canGenerate = Boolean(projectMetadata) || safeResponsePlan.length > 0 || safeProposalOutline.length > 0;

  const owners = Array.from(
    new Set(safeEvidencePack.map((item) => item.owner).filter(Boolean))
  ).sort();

  const categories = Array.from(
    new Set(safeEvidencePack.map((item) => item.evidence_category).filter(Boolean))
  ).sort();

  const filteredItems = safeEvidencePack.filter((item) => {
    const query = searchQuery.trim().toLowerCase();

    const matchesSearch =
      !query ||
      item.evidence_name?.toLowerCase().includes(query) ||
      item.evidence_category?.toLowerCase().includes(query) ||
      item.owner?.toLowerCase().includes(query) ||
      item.status?.toLowerCase().includes(query) ||
      item.priority?.toLowerCase().includes(query) ||
      item.notes?.toLowerCase().includes(query);

    const matchesStatus = statusFilter === "all" || item.status === statusFilter;
    const matchesPriority = priorityFilter === "all" || item.priority === priorityFilter;
    const matchesCategory = categoryFilter === "all" || item.evidence_category === categoryFilter;
    const matchesOwner = ownerFilter === "all" || item.owner === ownerFilter;

    return matchesSearch && matchesStatus && matchesPriority && matchesCategory && matchesOwner;
  });

  const activeItem = selectedEvidenceItem || filteredItems[0] || safeEvidencePack[0] || null;

  return (
    <div className="workspaceView">
      <div className="viewHeader">
        <div>
          <h3>Evidence Pack</h3>
          <p className="muted">
            Track supporting documents, proof, attachments, owners, status, and missing evidence for tender submission.
          </p>
        </div>

        <div className="viewHeaderActions">
          <span className="filterResultCount">
            {filteredItems.length} / {safeEvidencePack.length} {L("shown", "ditampilkan")}
          </span>

          <button
            type="button"
            disabled={busy || !canGenerate}
            onClick={generateEvidencePack}
          >
            Generate Evidence Pack
          </button>
        </div>
      </div>

      {!canGenerate && safeEvidencePack.length === 0 && (
        <div className="emptyStateCard">
          <h3>Evidence Pack belum bisa dibuat</h3>
          <p className="muted">
            Generate metadata, response plan, atau proposal outline dulu sebelum membuat evidence pack.
          </p>
        </div>
      )}

      <div className="evidenceStats">
        <EvidenceStat label="Open" value={safeEvidencePack.filter((item) => item.status === "open").length} />
        <EvidenceStat label="Requested" value={safeEvidencePack.filter((item) => item.status === "requested").length} />
        <EvidenceStat label="Received" value={safeEvidencePack.filter((item) => item.status === "received").length} />
        <EvidenceStat label="Validated" value={safeEvidencePack.filter((item) => item.status === "validated").length} />
        <EvidenceStat label="Blocked" value={safeEvidencePack.filter((item) => item.status === "blocked").length} />
      </div>

      <div className="filterBar evidencePackFilterBar">
        <input
          className="filterInput"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search evidence, category, owner, status, priority, or notes..."
        />

        <select className="filterSelect" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="all">{L("All statuses", "Semua status")}</option>
          <option value="open">open</option>
          <option value="requested">requested</option>
          <option value="received">received</option>
          <option value="validated">validated</option>
          <option value="not_applicable">not_applicable</option>
          <option value="blocked">blocked</option>
        </select>

        <select className="filterSelect" value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
          <option value="all">All priorities</option>
          <option value="high">high</option>
          <option value="medium">medium</option>
          <option value="low">low</option>
        </select>

        <select className="filterSelect" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
          <option value="all">{L("All categories", "Semua kategori")}</option>
          {categories.map((category) => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>

        <select className="filterSelect" value={ownerFilter} onChange={(e) => setOwnerFilter(e.target.value)}>
          <option value="all">All owners</option>
          {owners.map((owner) => (
            <option key={owner} value={owner}>{owner}</option>
          ))}
        </select>

        <button
          type="button"
          className="clearFilterButton"
          onClick={() => {
            setSearchQuery("");
            setStatusFilter("all");
            setPriorityFilter("all");
            setCategoryFilter("all");
            setOwnerFilter("all");
          }}
        >
          Clear
        </button>
      </div>

      <div className="reviewWorkbench evidenceWorkbench">
        <div className="reviewList">
          {filteredItems.map((item) => (
            <button
              key={item.id}
              type="button"
              className={activeItem?.id === item.id ? "reviewItem active evidenceItem" : "reviewItem evidenceItem"}
              onClick={() => setSelectedEvidenceItemId(item.id)}
            >
              <div className="reviewItemTop">
                <span className={`miniEvidencePriority ${item.priority}`}>{item.priority}</span>
                <span className={`miniEvidenceStatus ${item.status}`}>{item.status}</span>
              </div>
              <strong>{item.evidence_name}</strong>
              <small>{item.evidence_category} · {item.owner || "No owner"}</small>
            </button>
          ))}

          {safeEvidencePack.length === 0 && (
            <div className="emptyStateMini">
              <strong>No evidence pack generated yet.</strong>
              <span>Click Generate Evidence Pack to create evidence checklist.</span>
            </div>
          )}

          {safeEvidencePack.length > 0 && filteredItems.length === 0 && (
            <p className="empty">No matching evidence item.</p>
          )}
        </div>

        <div className="detailPanel">
          {activeItem ? (
            <EvidenceItemDetail
              item={activeItem}
              busy={busy}
              updateEvidenceItem={updateEvidenceItem}
            />
          ) : (
            <div className="emptyStateCard">
              <h3>Select an evidence item</h3>
              <p className="muted">Evidence details will appear here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ProposalTemplateView({
  proposalTemplate,
  busy,
  updateProposalTemplate,
  downloadExecutivePack,
}) {
  const template = proposalTemplate || {
    template_name: "Standard Executive Proposal",
    executive_title: "",
    cover_note: "",
    company_profile: "",
    win_theme: "",
    proposal_tone: "formal",
    section_order: [],
    excluded_section_keys: [],
    custom_sections: [],
    footer_note: "",
    notes: "",
  };

  const customSectionsText = JSON.stringify(template.custom_sections || [], null, 2);
  const sectionOrderText = (template.section_order || []).join(", ");
  const excludedSectionText = (template.excluded_section_keys || []).join(", ");

  function parseCsv(value) {
    return value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  function parseCustomSections(value) {
    try {
      const parsed = JSON.parse(value || "[]");
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return template.custom_sections || [];
    }
  }

  return (
    <div className="workspaceView proposalTemplateView">
      <div className="viewHeader proposalTemplateHeader">
        <div>
          <p className="eyebrow">Proposal Template Customization</p>
          <h2>Customize proposal structure and executive narrative</h2>
          <p className="muted">
            Control DOCX proposal title, cover note, company profile, win theme, tone, section order, excluded sections, custom sections, and footer.
          </p>
        </div>

        <button
          type="button"
          className="executivePackButton"
          disabled={busy}
          onClick={downloadExecutivePack}
        >
          Export Executive Pack
        </button>
      </div>

      <div className="proposalTemplateGrid">
        <div className="sectionBox proposalTemplatePanel">
          <h3>Template Identity</h3>

          <label>
            Template Name
            <input
              className="tableInput"
              defaultValue={template.template_name || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.template_name || "")) {
                  updateProposalTemplate({ template_name: e.target.value });
                }
              }}
            />
          </label>

          <label>
            Executive Title
            <input
              className="tableInput"
              defaultValue={template.executive_title || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.executive_title || "")) {
                  updateProposalTemplate({ executive_title: e.target.value });
                }
              }}
            />
          </label>

          <label>
            Proposal Tone
            <select
              value={template.proposal_tone || "formal"}
              disabled={busy}
              onChange={(e) => updateProposalTemplate({ proposal_tone: e.target.value })}
            >
              <option value="formal">Formal</option>
              <option value="concise">Concise</option>
              <option value="technical">Technical</option>
              <option value="executive">Executive</option>
            </select>
          </label>

          <label>
            Footer Note
            <textarea
              className="tableTextarea"
              defaultValue={template.footer_note || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.footer_note || "")) {
                  updateProposalTemplate({ footer_note: e.target.value });
                }
              }}
            />
          </label>
        </div>

        <div className="sectionBox proposalTemplatePanel">
          <h3>Executive Narrative</h3>

          <label>
            Cover Note
            <textarea
              className="tableTextarea"
              defaultValue={template.cover_note || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.cover_note || "")) {
                  updateProposalTemplate({ cover_note: e.target.value });
                }
              }}
            />
          </label>

          <label>
            Company Profile
            <textarea
              className="tableTextarea"
              defaultValue={template.company_profile || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.company_profile || "")) {
                  updateProposalTemplate({ company_profile: e.target.value });
                }
              }}
            />
          </label>

          <label>
            Win Theme
            <textarea
              className="tableTextarea"
              defaultValue={template.win_theme || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.win_theme || "")) {
                  updateProposalTemplate({ win_theme: e.target.value });
                }
              }}
            />
          </label>
        </div>
      </div>

      <div className="proposalTemplateGrid">
        <div className="sectionBox proposalTemplatePanel">
          <h3>Section Controls</h3>
          <p className="muted">
            Use proposal section keys separated by comma. Empty value keeps generated order.
          </p>

          <label>
            Section Order
            <input
              className="tableInput"
              defaultValue={sectionOrderText}
              disabled={busy}
              placeholder="executive_summary, scope, solution, timeline"
              onBlur={(e) => {
                if (e.target.value !== sectionOrderText) {
                  updateProposalTemplate({ section_order: parseCsv(e.target.value) });
                }
              }}
            />
          </label>

          <label>
            Excluded Section Keys
            <input
              className="tableInput"
              defaultValue={excludedSectionText}
              disabled={busy}
              placeholder="pricing, appendix"
              onBlur={(e) => {
                if (e.target.value !== excludedSectionText) {
                  updateProposalTemplate({ excluded_section_keys: parseCsv(e.target.value) });
                }
              }}
            />
          </label>

          <label>
            Internal Notes
            <textarea
              className="tableTextarea"
              defaultValue={template.notes || ""}
              disabled={busy}
              onBlur={(e) => {
                if (e.target.value !== (template.notes || "")) {
                  updateProposalTemplate({ notes: e.target.value });
                }
              }}
            />
          </label>
        </div>

        <div className="sectionBox proposalTemplatePanel">
          <h3>Custom Sections JSON</h3>
          <p className="muted">
            Example: [{`{"title":"Why Us","content":"Our differentiator..."}`}]
          </p>

          <textarea
            className="tableTextarea customSectionsTextarea"
            defaultValue={customSectionsText}
            disabled={busy}
            onBlur={(e) => {
              if (e.target.value !== customSectionsText) {
                updateProposalTemplate({ custom_sections: parseCustomSections(e.target.value) });
              }
            }}
          />

          <div className="actionQuickControls">
            <button
              type="button"
              disabled={busy}
              onClick={() =>
                updateProposalTemplate({
                  custom_sections: [
                    ...(template.custom_sections || []),
                    {
                      title: "Why We Win",
                      content: "Add tailored differentiators, proof points, and executive value here.",
                    },
                  ],
                })
              }
            >
              Add Sample Section
            </button>

            <button
              type="button"
              disabled={busy}
              onClick={() =>
                updateProposalTemplate({
                  executive_title: "Executive Proposal",
                  proposal_tone: "executive",
                  cover_note: "This proposal is tailored to the client priorities, requirements, and risk posture.",
                  win_theme: "We combine compliance, delivery confidence, and measurable business value.",
                })
              }
            >
              Apply Executive Preset
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ClarificationResponseTrackerView({
  clarificationTracker = { summary: null, items: [] },
  busy,
  generateClarificationResponseTracker,
  updateClarificationResponseItem,
}) {
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [ownerFilter, setOwnerFilter] = useState("all");

  const summary = clarificationTracker?.summary || {};
  const safeItems = Array.isArray(clarificationTracker?.items) ? clarificationTracker.items : [];

  const owners = useMemo(
    () => Array.from(new Set(safeItems.map((item) => item.owner).filter(Boolean))).sort(),
    [safeItems]
  );

  const statusRank = { overdue: 0, open: 1, sent: 2, answered: 3, incorporated: 4, closed: 5 };
  const priorityRank = { high: 0, medium: 1, low: 2 };

  const filteredItems = safeItems
    .filter((item) => {
      if (statusFilter !== "all" && item.response_status !== statusFilter) return false;
      if (priorityFilter !== "all" && item.priority !== priorityFilter) return false;
      if (ownerFilter !== "all" && item.owner !== ownerFilter) return false;
      return true;
    })
    .sort((a, b) => {
      const statusDiff = (statusRank[a.response_status] ?? 9) - (statusRank[b.response_status] ?? 9);
      if (statusDiff !== 0) return statusDiff;
      return (priorityRank[a.priority] ?? 1) - (priorityRank[b.priority] ?? 1);
    });

  const statusCounts = summary.status_counts || {};

  return (
    <div className="workspaceView clarificationTrackerView">
      <div className="viewHeader clarificationTrackerHeader">
        <div>
          <p className="eyebrow">Clarification Response Tracker</p>
          <h2>Client response lifecycle tracker</h2>
          <p className="muted">
            Track clarification answers, follow-ups, owner accountability, and downstream artifact impact.
          </p>
        </div>

        <button
          type="button"
          className="regenerateAllButton"
          disabled={busy}
          onClick={generateClarificationResponseTracker}
        >
          Generate Tracker
        </button>
      </div>

      <div className="clarificationTrackerHero">
        <div className="clarificationProgressCard">
          <strong>{summary.completion_percent ?? 0}%</strong>
          <span>Completion</span>
          <p>{summary.recommendation || "Generate tracker after clarification questions are available."}</p>
        </div>

        <div className="clarificationProgressCard warning">
          <strong>{summary.open_items ?? 0}</strong>
          <span>Open Items</span>
          <p>High priority: {summary.high_priority_items ?? 0}. High risk: {summary.high_risk_items ?? 0}.</p>
        </div>
      </div>

      <div className="actionStatGrid clarificationTrackerStats">
        <ComplianceMetric label="Total" value={summary.total_items ?? safeItems.length} />
        <ComplianceMetric label="Open" value={statusCounts.open || 0} tone="warning" />
        <ComplianceMetric label="Sent" value={statusCounts.sent || 0} />
        <ComplianceMetric label="Answered" value={statusCounts.answered || 0} />
        <ComplianceMetric label="Incorporated" value={statusCounts.incorporated || 0} />
        <ComplianceMetric label="Overdue" value={statusCounts.overdue || 0} tone="danger" />
      </div>

      <div className="actionFilterBar clarificationTrackerFilterBar">
        <label>
          Status
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="all">{L("All statuses", "Semua status")}</option>
            <option value="open">Open</option>
            <option value="sent">Sent</option>
            <option value="answered">Answered</option>
            <option value="incorporated">Incorporated</option>
            <option value="closed">Closed</option>
            <option value="overdue">Overdue</option>
          </select>
        </label>

        <label>
          Priority
          <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
            <option value="all">All priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </label>

        <label>
          Owner
          <select value={ownerFilter} onChange={(e) => setOwnerFilter(e.target.value)}>
            <option value="all">All owners</option>
            {owners.map((owner) => (
              <option key={owner} value={owner}>{owner}</option>
            ))}
          </select>
        </label>
      </div>

      <p className="actionTrackerMeta">
        Showing {filteredItems.length} of {safeItems.length} clarification response item(s).
      </p>

      {filteredItems.length === 0 ? (
        <div className="sectionBox actionEmptyState">
          <h3>No clarification response tracker yet</h3>
          <p className="muted">Generate tracker after clarification questions are available.</p>
        </div>
      ) : (
        <div className="clarificationTrackerList">
          {filteredItems.map((item) => (
            <article key={item.id} className={`clarificationTrackerCard ${item.response_status}`}>
              <div className="clarificationTrackerTop">
                <div>
                  <span className={`clarificationStatusPill ${item.response_status}`}>{item.response_status}</span>
                  <span className={`priorityPill ${item.priority}`}>{item.priority}</span>
                  <span className="sourcePill">{item.category}</span>
                </div>

                <select
                  value={item.response_status || "open"}
                  disabled={busy}
                  onChange={(e) => updateClarificationResponseItem(item.id, { response_status: e.target.value })}
                >
                  <option value="open">Open</option>
                  <option value="sent">Sent</option>
                  <option value="answered">Answered</option>
                  <option value="incorporated">Incorporated</option>
                  <option value="closed">Closed</option>
                  <option value="overdue">Overdue</option>
                </select>
              </div>

              <h3>Clarification #{item.clarification_id || "-"}</h3>
              <p>{item.question_text}</p>

              <div className="actionItemMetaGrid">
                <div>
                  <span>Owner</span>
                  <strong>{item.owner || "Unassigned"}</strong>
                </div>
                <div>
                  <span>Due Date</span>
                  <strong>{item.due_date || "-"}</strong>
                </div>
                <div>
                  <span>Risk</span>
                  <strong>{item.risk_level}</strong>
                </div>
                <div>
                  <span>Impacts</span>
                  <strong>{(item.impacted_artifacts || []).join(", ") || "-"}</strong>
                </div>
              </div>

              <div className="clarificationInlineGrid">
                <label>
                  Owner
                  <input
                    className="tableInput"
                    defaultValue={item.owner || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.owner || "")) {
                        updateClarificationResponseItem(item.id, { owner: e.target.value });
                      }
                    }}
                  />
                </label>

                <label>
                  Due Date
                  <input
                    className="tableInput"
                    defaultValue={item.due_date || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.due_date || "")) {
                        updateClarificationResponseItem(item.id, { due_date: e.target.value });
                      }
                    }}
                  />
                </label>

                <label>
                  Sent At
                  <input
                    className="tableInput"
                    defaultValue={item.sent_at || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.sent_at || "")) {
                        updateClarificationResponseItem(item.id, { sent_at: e.target.value });
                      }
                    }}
                  />
                </label>
              </div>

              <div className="riskPlanGrid">
                <label>
                  Client Response
                  <textarea
                    className="tableTextarea"
                    defaultValue={item.client_response || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.client_response || "")) {
                        updateClarificationResponseItem(item.id, { client_response: e.target.value });
                      }
                    }}
                  />
                </label>

                <label>
                  Recommended Follow-up
                  <textarea
                    className="tableTextarea"
                    defaultValue={item.recommended_follow_up || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.recommended_follow_up || "")) {
                        updateClarificationResponseItem(item.id, { recommended_follow_up: e.target.value });
                      }
                    }}
                  />
                </label>
              </div>

              <div className="evidenceRelationGrid">
                <ComplianceRelationBox title="Response IDs" values={item.related_response_item_ids || []} />
                <ComplianceRelationBox title="Compliance IDs" values={item.related_compliance_item_ids || []} />
                <ComplianceRelationBox title="Risk IDs" values={item.related_risk_item_ids || []} />
                <ComplianceRelationBox title="Addendum IDs" values={item.related_addendum_impact_ids || []} />
              </div>

              <div className="actionQuickControls">
                <button type="button" disabled={busy} onClick={() => updateClarificationResponseItem(item.id, { response_status: "sent" })}>
                  Mark Sent
                </button>
                <button type="button" disabled={busy} onClick={() => updateClarificationResponseItem(item.id, { response_status: "answered" })}>
                  Mark Answered
                </button>
                <button type="button" disabled={busy} onClick={() => updateClarificationResponseItem(item.id, { response_status: "incorporated" })}>
                  Mark Incorporated
                </button>
                <button type="button" disabled={busy} onClick={() => updateClarificationResponseItem(item.id, { response_status: "closed" })}>
                  Close
                </button>
                <button type="button" disabled={busy} onClick={() => updateClarificationResponseItem(item.id, { response_status: "overdue" })}>
                  Mark Overdue
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

function AddendumImpactView({
  addendumImpacts = { summary: null, items: [] },
  busy,
  generateAddendumImpactAnalysis,
  updateAddendumImpactItem,
}) {
  const [severityFilter, setSeverityFilter] = useState("all");
  const [artifactFilter, setArtifactFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const summary = addendumImpacts?.summary || {};
  const safeItems = Array.isArray(addendumImpacts?.items) ? addendumImpacts.items : [];

  const artifacts = useMemo(
    () => Array.from(new Set(safeItems.map((item) => item.impacted_artifact).filter(Boolean))).sort(),
    [safeItems]
  );

  const severityRank = { critical: 0, high: 1, medium: 2, low: 3 };

  const filteredItems = safeItems
    .filter((item) => {
      if (severityFilter !== "all" && item.severity !== severityFilter) return false;
      if (artifactFilter !== "all" && item.impacted_artifact !== artifactFilter) return false;
      if (statusFilter !== "all" && item.status !== statusFilter) return false;
      return true;
    })
    .sort((a, b) => (severityRank[a.severity] ?? 2) - (severityRank[b.severity] ?? 2));

  const severityCounts = summary.severity_counts || {};
  const statusCounts = summary.status_counts || {};

  return (
    <div className="workspaceView addendumImpactView">
      <div className="viewHeader addendumHeader">
        <div>
          <p className="eyebrow">Addendum / Document Impact Analysis</p>
          <h2>Document change impact tracker</h2>
          <p className="muted">
            Analyze revised tender documents against requirements, response plan, compliance, risks, and approvals.
          </p>
        </div>

        <button
          type="button"
          className="regenerateAllButton"
          disabled={busy}
          onClick={generateAddendumImpactAnalysis}
        >
          Generate Impact Analysis
        </button>
      </div>

      <div className="addendumHero">
        <div className="addendumHeroCard">
          <span>Total Impacts</span>
          <strong>{summary.total_items ?? safeItems.length}</strong>
          <p>{summary.recommendation || "Generate impact analysis after an addendum or revised document is uploaded."}</p>
        </div>

        <div className="addendumHeroCard warning">
          <span>Critical / High</span>
          <strong>{summary.critical_items ?? 0} / {summary.high_items ?? 0}</strong>
          <p>Open items: {summary.open_items ?? statusCounts.open ?? 0}</p>
        </div>
      </div>

      <div className="actionStatGrid addendumStatGrid">
        <ComplianceMetric label="Critical" value={severityCounts.critical || 0} tone="danger" />
        <ComplianceMetric label="High" value={severityCounts.high || 0} tone="danger" />
        <ComplianceMetric label="Medium" value={severityCounts.medium || 0} tone="warning" />
        <ComplianceMetric label="Low" value={severityCounts.low || 0} />
        <ComplianceMetric label="Resolved" value={statusCounts.resolved || 0} />
      </div>

      <div className="actionFilterBar addendumFilterBar">
        <label>
          Severity
          <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
            <option value="all">All severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </label>

        <label>
          Artifact
          <select value={artifactFilter} onChange={(e) => setArtifactFilter(e.target.value)}>
            <option value="all">All artifacts</option>
            {artifacts.map((artifact) => (
              <option key={artifact} value={artifact}>{artifact}</option>
            ))}
          </select>
        </label>

        <label>
          Status
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="all">{L("All statuses", "Semua status")}</option>
            <option value="open">Open</option>
            <option value="reviewed">Reviewed</option>
            <option value="accepted">Accepted</option>
            <option value="resolved">Resolved</option>
            <option value="rejected">Rejected</option>
          </select>
        </label>
      </div>

      <p className="actionTrackerMeta">
        Showing {filteredItems.length} of {safeItems.length} addendum impact item(s).
      </p>

      {filteredItems.length === 0 ? (
        <div className="sectionBox actionEmptyState">
          <h3>No addendum impacts yet</h3>
          <p className="muted">Generate impact analysis after uploading or selecting a revised tender document.</p>
        </div>
      ) : (
        <div className="addendumImpactList">
          {filteredItems.map((item) => (
            <article key={item.id} className={`addendumImpactCard ${item.severity}`}>
              <div className="addendumImpactTop">
                <div>
                  <span className={`priorityPill ${item.severity}`}>{item.severity}</span>
                  <span className="sourcePill">{item.impacted_artifact}</span>
                  <span className="sourcePill">{item.impact_type}</span>
                </div>

                <select
                  value={item.status || "open"}
                  disabled={busy}
                  onChange={(e) => updateAddendumImpactItem(item.id, { status: e.target.value })}
                >
                  <option value="open">Open</option>
                  <option value="reviewed">Reviewed</option>
                  <option value="accepted">Accepted</option>
                  <option value="resolved">Resolved</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>

              <h3>{item.title}</h3>
              {item.summary && <p>{item.summary}</p>}

              <div className="actionItemMetaGrid">
                <div>
                  <span>Source Document</span>
                  <strong>{item.source_document_name || "-"}</strong>
                </div>
                <div>
                  <span>Owner</span>
                  <strong>{item.owner || "Unassigned"}</strong>
                </div>
                <div>
                  <span>Due Date</span>
                  <strong>{item.due_date || "-"}</strong>
                </div>
                <div>
                  <span>Confidence</span>
                  <strong>{item.confidence ?? "-"}</strong>
                </div>
              </div>

              <div className="riskPlanGrid">
                <label>
                  Recommended Action
                  <textarea
                    className="tableTextarea"
                    defaultValue={item.recommended_action || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.recommended_action || "")) {
                        updateAddendumImpactItem(item.id, { recommended_action: e.target.value });
                      }
                    }}
                  />
                </label>

                <label>
                  Notes
                  <textarea
                    className="tableTextarea"
                    defaultValue={item.notes || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.notes || "")) {
                        updateAddendumImpactItem(item.id, { notes: e.target.value });
                      }
                    }}
                  />
                </label>
              </div>

              {item.source_excerpt && (
                <p className="actionItemNotes">
                  <strong>Source:</strong> {item.source_excerpt}
                </p>
              )}

              <div className="evidenceRelationGrid">
                <ComplianceRelationBox title="Requirement IDs" values={item.related_requirement_ids || []} />
                <ComplianceRelationBox title="Response IDs" values={item.related_response_item_ids || []} />
                <ComplianceRelationBox title="Clarification IDs" values={item.related_clarification_ids || []} />
                <ComplianceRelationBox title="Risk IDs" values={item.related_risk_item_ids || []} />
              </div>

              <div className="actionQuickControls">
                <button type="button" disabled={busy} onClick={() => updateAddendumImpactItem(item.id, { status: "reviewed" })}>
                  Mark Reviewed
                </button>
                <button type="button" disabled={busy} onClick={() => updateAddendumImpactItem(item.id, { status: "accepted" })}>
                  Accept
                </button>
                <button type="button" disabled={busy} onClick={() => updateAddendumImpactItem(item.id, { status: "resolved" })}>
                  Resolve
                </button>
                <button type="button" disabled={busy} onClick={() => updateAddendumImpactItem(item.id, { severity: "critical" })}>
                  Escalate Critical
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

function ApprovalWorkflowView({
  approvalWorkflow = { summary: null, request: null, steps: [] },
  busy,
  actorName,
  generateApprovalWorkflow,
  submitApprovalWorkflow,
  updateApprovalStep,
}) {
  const summary = approvalWorkflow?.summary || {};
  const request = approvalWorkflow?.request || null;
  const steps = Array.isArray(approvalWorkflow?.steps) ? approvalWorkflow.steps : [];

  const statusCounts = steps.reduce((acc, step) => {
    acc[step.status] = (acc[step.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="workspaceView approvalWorkflowView">
      <div className="viewHeader approvalHeader">
        <div>
          <p className="eyebrow">Approval Workflow</p>
          <h2>Bid approval routing and sign-off</h2>
          <p className="muted">
            Generate approval steps from decision gate, compliance scorecard, risk register, and action tracker.
          </p>
        </div>

        <div className="approvalHeaderActions">
          <button
            type="button"
            className="regenerateAllButton"
            disabled={busy}
            onClick={generateApprovalWorkflow}
          >
            Generate Workflow
          </button>

          <button
            type="button"
            className="secondaryButton"
            disabled={busy || !request?.id || request?.status !== "draft"}
            onClick={() => submitApprovalWorkflow(request?.id)}
          >
            Submit for Approval
          </button>
        </div>
      </div>

      <div className="approvalSummaryHero">
        <div className="approvalProgressRing">
          <strong>{summary.progress_percent ?? 0}%</strong>
          <span>Approved</span>
        </div>

        <div className="approvalSummaryCopy">
          <h3>{request?.title || "No approval workflow generated yet"}</h3>
          <p className="muted">
            {request?.description || "Generate an approval workflow after compliance, risks, and decision gate are ready."}
          </p>
          <div className={`approvalStatusPill ${request?.status || "not_generated"}`}>
            {request?.status || "not_generated"}
          </div>
        </div>
      </div>

      <div className="actionStatGrid approvalStatGrid">
        <ComplianceMetric label="Total Steps" value={summary.total_steps ?? steps.length} />
        <ComplianceMetric label="Pending" value={summary.pending_steps ?? statusCounts.pending ?? 0} tone="warning" />
        <ComplianceMetric label="Approved" value={summary.approved_steps ?? statusCounts.approved ?? 0} />
        <ComplianceMetric label="Changes" value={summary.changes_requested_steps ?? statusCounts.changes_requested ?? 0} tone="warning" />
        <ComplianceMetric label="Rejected" value={summary.rejected_steps ?? statusCounts.rejected ?? 0} tone="danger" />
      </div>

      {steps.length === 0 ? (
        <div className="sectionBox actionEmptyState">
          <h3>No approval steps yet</h3>
          <p className="muted">Generate the approval workflow after the decision gate and scorecards are available.</p>
        </div>
      ) : (
        <div className="approvalStepTimeline">
          {steps.map((step) => (
            <article key={step.id} className={`approvalStepCard ${step.status}`}>
              <div className="approvalStepOrder">{step.step_order}</div>

              <div className="approvalStepBody">
                <div className="approvalStepTop">
                  <div>
                    <span className={`approvalStatusPill ${step.status}`}>{step.status}</span>
                    <span className="sourcePill">{step.role}</span>
                  </div>

                  <strong>{step.approver_name || step.role}</strong>
                </div>

                <div className="approvalInlineGrid">
                  <label>
                    Approver
                    <input
                      className="tableInput"
                      defaultValue={step.approver_name || ""}
                      disabled={busy}
                      onBlur={(e) => {
                        if (e.target.value !== (step.approver_name || "")) {
                          updateApprovalStep(step.id, { approver_name: e.target.value });
                        }
                      }}
                    />
                  </label>

                  <label>
                    Email
                    <input
                      className="tableInput"
                      defaultValue={step.approver_email || ""}
                      disabled={busy}
                      onBlur={(e) => {
                        if (e.target.value !== (step.approver_email || "")) {
                          updateApprovalStep(step.id, { approver_email: e.target.value });
                        }
                      }}
                    />
                  </label>

                  <label>
                    Due Date
                    <input
                      className="tableInput"
                      defaultValue={step.due_date || ""}
                      disabled={busy}
                      onBlur={(e) => {
                        if (e.target.value !== (step.due_date || "")) {
                          updateApprovalStep(step.id, { due_date: e.target.value });
                        }
                      }}
                    />
                  </label>
                </div>

                <label className="approvalDecisionNote">
                  Decision Note
                  <textarea
                    className="tableTextarea"
                    defaultValue={step.decision_note || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (step.decision_note || "")) {
                        updateApprovalStep(step.id, { decision_note: e.target.value });
                      }
                    }}
                  />
                </label>

                <div className="approvalQuickControls">
                  <button type="button" disabled={busy} onClick={() => updateApprovalStep(step.id, { status: "pending" })}>
                    Mark Pending
                  </button>
                  <button type="button" disabled={busy} onClick={() => updateApprovalStep(step.id, { status: "approved", decision_note: step.decision_note || `Approved by ${actorName}` })}>
                    Approve
                  </button>
                  <button type="button" disabled={busy} onClick={() => updateApprovalStep(step.id, { status: "changes_requested", decision_note: step.decision_note || "Changes requested" })}>
                    Request Changes
                  </button>
                  <button type="button" disabled={busy} onClick={() => updateApprovalStep(step.id, { status: "rejected", decision_note: step.decision_note || "Rejected" })}>
                    Reject
                  </button>
                </div>

                {step.decided_at && (
                  <p className="approvalDecisionMeta">
                    Decided by {step.decided_by || "-"} at {new Date(step.decided_at).toLocaleString()}
                  </p>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

function ComplianceScorecardView({
  complianceScorecard = { summary: null, items: [] },
  busy,
  generateComplianceScorecard,
  updateComplianceItem,
}) {
  const [statusFilter, setStatusFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [ownerFilter, setOwnerFilter] = useState("all");

  const summary = complianceScorecard?.summary || {};
  const safeItems = Array.isArray(complianceScorecard?.items) ? complianceScorecard.items : [];

  const categories = useMemo(
    () => Array.from(new Set(safeItems.map((item) => item.category).filter(Boolean))).sort(),
    [safeItems]
  );

  const owners = useMemo(
    () => Array.from(new Set(safeItems.map((item) => item.owner).filter(Boolean))).sort(),
    [safeItems]
  );

  const filteredItems = safeItems
    .filter((item) => {
      if (statusFilter !== "all" && item.compliance_status !== statusFilter) return false;
      if (categoryFilter !== "all" && item.category !== categoryFilter) return false;
      if (ownerFilter !== "all" && item.owner !== ownerFilter) return false;
      return true;
    })
    .sort((a, b) => (a.score ?? 0) - (b.score ?? 0));

  const statusCounts = summary.status_counts || {};
  const evidenceCounts = summary.evidence_coverage_counts || {};

  return (
    <div className="workspaceView complianceScorecardView">
      <div className="viewHeader complianceHeader">
        <div>
          <p className="eyebrow">Compliance Matrix Scorecard</p>
          <h2>Requirement compliance matrix and scoring</h2>
          <p className="muted">
            Scores every requirement against response status, evidence coverage, clarification dependency, risk, and priority.
          </p>
        </div>

        <button
          type="button"
          className="regenerateAllButton"
          disabled={busy}
          onClick={generateComplianceScorecard}
        >
          Generate Scorecard
        </button>
      </div>

      <div className="complianceScoreHero">
        <div className="complianceScoreCircle">
          <strong>{summary.score_percent ?? 0}%</strong>
          <span>Compliance Score</span>
        </div>

        <div className="complianceScoreCopy">
          <h3>{summary.recommendation || "Generate the compliance scorecard to review bid gaps."}</h3>
          <p className="muted">
            Weighted score: {summary.weighted_score ?? 0} / {summary.max_score ?? 0}. High-risk gaps: {summary.high_risk_gaps ?? 0}.
          </p>
        </div>
      </div>

      <div className="actionStatGrid complianceStatGrid">
        <ComplianceMetric label="Total Items" value={summary.total_items ?? safeItems.length} />
        <ComplianceMetric label="Compliant" value={statusCounts.compliant || 0} />
        <ComplianceMetric label="Partial" value={statusCounts.partially_compliant || 0} tone="warning" />
        <ComplianceMetric label="Need Review" value={statusCounts.needs_review || 0} tone="warning" />
        <ComplianceMetric label="Need Clarify" value={statusCounts.needs_clarification || 0} tone="warning" />
        <ComplianceMetric label="Non-Compliant" value={statusCounts.non_compliant || 0} tone="danger" />
      </div>

      <div className="complianceMiniGrid">
        <div className="sectionBox">
          <h3>Evidence Coverage</h3>
          <div className="miniMetricList">
            <span>Covered <strong>{evidenceCounts.covered || 0}</strong></span>
            <span>Partial <strong>{evidenceCounts.partial || 0}</strong></span>
            <span>Missing <strong>{evidenceCounts.missing || 0}</strong></span>
          </div>
        </div>

        <div className="sectionBox">
          <h3>Lowest Category Scores</h3>
          <div className="miniMetricList">
            {(summary.category_scores || []).slice(0, 5).map((item) => (
              <span key={item.category}>{item.category} <strong>{item.score_percent}%</strong></span>
            ))}
            {!(summary.category_scores || []).length && <span>No category score yet.</span>}
          </div>
        </div>
      </div>

      <div className="actionFilterBar complianceFilterBar">
        <label>
          Status
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="all">{L("All statuses", "Semua status")}</option>
            <option value="compliant">Compliant</option>
            <option value="partially_compliant">Partially compliant</option>
            <option value="needs_review">Needs review</option>
            <option value="needs_clarification">Needs clarification</option>
            <option value="non_compliant">Non-compliant</option>
            <option value="not_started">Not started</option>
          </select>
        </label>

        <label>
          Category
          <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
            <option value="all">{L("All categories", "Semua kategori")}</option>
            {categories.map((category) => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </label>

        <label>
          Owner
          <select value={ownerFilter} onChange={(e) => setOwnerFilter(e.target.value)}>
            <option value="all">All owners</option>
            {owners.map((owner) => (
              <option key={owner} value={owner}>{owner}</option>
            ))}
          </select>
        </label>
      </div>

      <p className="actionTrackerMeta">
        Showing {filteredItems.length} of {safeItems.length} compliance item(s).
      </p>

      {filteredItems.length === 0 ? (
        <div className="sectionBox actionEmptyState">
          <h3>No compliance matrix yet</h3>
          <p className="muted">Generate the scorecard after requirements, response plan, and evidence pack are available.</p>
        </div>
      ) : (
        <div className="complianceMatrixList">
          {filteredItems.map((item) => (
            <article key={item.id} className={`complianceMatrixCard ${item.compliance_status}`}>
              <div className="complianceCardTop">
                <div>
                  <span className={`complianceStatusPill ${item.compliance_status}`}>{item.compliance_status}</span>
                  <span className="sourcePill">{item.category}</span>
                  <span className={`sourcePill ${item.evidence_coverage}`}>Evidence: {item.evidence_coverage}</span>
                </div>

                <div className="complianceScorePill">
                  <strong>{item.score}</strong>
                  <span>/ {item.max_score}</span>
                </div>
              </div>

              <h3>Requirement #{item.requirement_id || "-"}</h3>
              <p>{item.requirement_text}</p>

              <div className="actionItemMetaGrid">
                <div>
                  <span>Owner</span>
                  <strong>{item.owner || "Unassigned"}</strong>
                </div>
                <div>
                  <span>Priority</span>
                  <strong>{item.priority}</strong>
                </div>
                <div>
                  <span>Risk</span>
                  <strong>{item.risk_level}</strong>
                </div>
                <div>
                  <span>Weight</span>
                  <strong>{item.weight}</strong>
                </div>
              </div>

              <div className="complianceInlineGrid">
                <label>
                  Status
                  <select
                    value={item.compliance_status || "needs_review"}
                    disabled={busy}
                    onChange={(e) => updateComplianceItem(item.id, { compliance_status: e.target.value })}
                  >
                    <option value="compliant">Compliant</option>
                    <option value="partially_compliant">Partially compliant</option>
                    <option value="needs_review">Needs review</option>
                    <option value="needs_clarification">Needs clarification</option>
                    <option value="non_compliant">Non-compliant</option>
                    <option value="not_started">Not started</option>
                  </select>
                </label>

                <label>
                  Score
                  <input
                    className="tableInput"
                    type="number"
                    min="0"
                    max="100"
                    defaultValue={item.score ?? 0}
                    disabled={busy}
                    onBlur={(e) => {
                      const value = Number(e.target.value);
                      if (Number.isFinite(value) && value !== item.score) {
                        updateComplianceItem(item.id, { score: value });
                      }
                    }}
                  />
                </label>

                <label>
                  Owner
                  <input
                    className="tableInput"
                    defaultValue={item.owner || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.owner || "")) {
                        updateComplianceItem(item.id, { owner: e.target.value });
                      }
                    }}
                  />
                </label>
              </div>

              <div className="riskPlanGrid">
                <label>
                  Gap Summary
                  <textarea
                    className="tableTextarea"
                    defaultValue={item.gap_summary || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.gap_summary || "")) {
                        updateComplianceItem(item.id, { gap_summary: e.target.value });
                      }
                    }}
                  />
                </label>

                <label>
                  Recommended Action
                  <textarea
                    className="tableTextarea"
                    defaultValue={item.recommended_action || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.recommended_action || "")) {
                        updateComplianceItem(item.id, { recommended_action: e.target.value });
                      }
                    }}
                  />
                </label>
              </div>

              <div className="evidenceRelationGrid">
                <ComplianceRelationBox title="Requirement ID" values={item.requirement_id ? [item.requirement_id] : []} />
                <ComplianceRelationBox title="Response Item ID" values={item.response_item_id ? [item.response_item_id] : []} />
                <ComplianceRelationBox title="Evidence IDs" values={item.evidence_item_ids || []} />
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

function RiskRegisterView({
  riskItems = [],
  busy,
  generateRiskRegister,
  updateRiskItem,
}) {
  const [statusFilter, setStatusFilter] = useState("all");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [ownerFilter, setOwnerFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");

  const safeItems = Array.isArray(riskItems) ? riskItems : [];
  const severityRank = { critical: 0, high: 1, medium: 2, low: 3 };

  const owners = useMemo(
    () => Array.from(new Set(safeItems.map((item) => item.owner).filter(Boolean))).sort(),
    [safeItems]
  );

  const categories = useMemo(
    () => Array.from(new Set(safeItems.map((item) => item.risk_category).filter(Boolean))).sort(),
    [safeItems]
  );

  const filteredItems = safeItems
    .filter((item) => {
      if (statusFilter !== "all" && item.status !== statusFilter) return false;
      if (severityFilter !== "all" && item.severity !== severityFilter) return false;
      if (ownerFilter !== "all" && item.owner !== ownerFilter) return false;
      if (categoryFilter !== "all" && item.risk_category !== categoryFilter) return false;
      return true;
    })
    .sort((a, b) => {
      const severityDiff = (severityRank[a.severity] ?? 2) - (severityRank[b.severity] ?? 2);
      if (severityDiff !== 0) return severityDiff;
      return String(a.owner || "").localeCompare(String(b.owner || ""));
    });

  const counts = {
    critical: safeItems.filter((item) => item.severity === "critical").length,
    high: safeItems.filter((item) => item.severity === "high").length,
    open: safeItems.filter((item) => item.status === "open").length,
    mitigating: safeItems.filter((item) => item.status === "mitigating").length,
    escalated: safeItems.filter((item) => item.status === "escalated").length,
  };

  return (
    <div className="workspaceView actionTrackerView riskRegisterView">
      <div className="viewHeader actionTrackerHeader">
        <div>
          <p className="eyebrow">Risk Register</p>
          <h2>Tender risk register and mitigation tracker</h2>
          <p className="muted">
            Generated from high-risk requirements, clarifications, response risks, evidence gaps, and decision gate blockers.
          </p>
        </div>

        <button
          type="button"
          className="regenerateAllButton"
          disabled={busy}
          onClick={generateRiskRegister}
        >
          Generate Risk Register
        </button>
      </div>

      <div className="actionStatGrid riskStatGrid">
        <RiskStat label="Total" value={safeItems.length} />
        <RiskStat label="Critical" value={counts.critical} tone="danger" />
        <RiskStat label="High" value={counts.high} tone="danger" />
        <RiskStat label="Open" value={counts.open} tone="warning" />
        <RiskStat label="Mitigating" value={counts.mitigating} />
        <RiskStat label="Escalated" value={counts.escalated} tone="danger" />
      </div>

      <div className="actionFilterBar riskFilterBar">
        <label>
          Status
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="all">{L("All statuses", "Semua status")}</option>
            <option value="open">Open</option>
            <option value="mitigating">Mitigating</option>
            <option value="monitored">Monitored</option>
            <option value="accepted">Accepted</option>
            <option value="closed">Closed</option>
            <option value="escalated">Escalated</option>
          </select>
        </label>

        <label>
          Severity
          <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
            <option value="all">All severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </label>

        <label>
          Owner
          <select value={ownerFilter} onChange={(e) => setOwnerFilter(e.target.value)}>
            <option value="all">All owners</option>
            {owners.map((owner) => (
              <option key={owner} value={owner}>{owner}</option>
            ))}
          </select>
        </label>

        <label>
          Category
          <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
            <option value="all">{L("All categories", "Semua kategori")}</option>
            {categories.map((category) => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </label>
      </div>

      <p className="actionTrackerMeta">
        Showing {filteredItems.length} of {safeItems.length} risk item(s).
      </p>

      {filteredItems.length === 0 ? (
        <div className="sectionBox actionEmptyState">
          <h3>No risks yet</h3>
          <p className="muted">Generate the risk register after requirements, response plan, evidence pack, and decision gate are available.</p>
        </div>
      ) : (
        <div className="actionItemGrid riskItemGrid">
          {filteredItems.map((item) => (
            <article
              key={item.id}
              className={`actionItemCard riskItemCard ${item.severity || "medium"} ${item.status === "closed" ? "done" : ""}`}
            >
              <div className="actionItemTop">
                <div>
                  <span className={`priorityPill ${item.severity || "medium"}`}>{item.severity || "medium"}</span>
                  <span className="sourcePill">{item.source_type || "source"}</span>
                  <span className="sourcePill">{item.impact_area || "impact"}</span>
                </div>

                <select
                  value={item.status || "open"}
                  disabled={busy}
                  onChange={(e) => updateRiskItem(item.id, { status: e.target.value })}
                >
                  <option value="open">Open</option>
                  <option value="mitigating">Mitigating</option>
                  <option value="monitored">Monitored</option>
                  <option value="accepted">Accepted</option>
                  <option value="closed">Closed</option>
                  <option value="escalated">Escalated</option>
                </select>
              </div>

              <h3>{item.title}</h3>
              {item.description && <p>{item.description}</p>}

              <div className="actionItemMetaGrid">
                <div>
                  <span>Category</span>
                  <strong>{item.risk_category || "-"}</strong>
                </div>
                <div>
                  <span>Probability</span>
                  <strong>{item.probability || "-"}</strong>
                </div>
                <div>
                  <span>Impact</span>
                  <strong>{item.impact || "-"}</strong>
                </div>
                <div>
                  <span>Owner</span>
                  <strong>{item.owner || "Unassigned"}</strong>
                </div>
              </div>

              <div className="riskInlineEditGrid">
                <label>
                  Owner
                  <input
                    className="tableInput"
                    defaultValue={item.owner || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.owner || "")) {
                        updateRiskItem(item.id, { owner: e.target.value });
                      }
                    }}
                  />
                </label>

                <label>
                  Due Date
                  <input
                    className="tableInput"
                    defaultValue={item.due_date || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.due_date || "")) {
                        updateRiskItem(item.id, { due_date: e.target.value });
                      }
                    }}
                  />
                </label>
              </div>

              <div className="riskPlanGrid">
                <label>
                  Mitigation Plan
                  <textarea
                    className="tableTextarea"
                    defaultValue={item.mitigation_plan || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.mitigation_plan || "")) {
                        updateRiskItem(item.id, { mitigation_plan: e.target.value });
                      }
                    }}
                  />
                </label>

                <label>
                  Contingency Plan
                  <textarea
                    className="tableTextarea"
                    defaultValue={item.contingency_plan || ""}
                    disabled={busy}
                    onBlur={(e) => {
                      if (e.target.value !== (item.contingency_plan || "")) {
                        updateRiskItem(item.id, { contingency_plan: e.target.value });
                      }
                    }}
                  />
                </label>
              </div>

              {item.trigger_event && (
                <p className="actionItemNotes">
                  <strong>Trigger:</strong> {item.trigger_event}
                </p>
              )}

              <div className="evidenceRelationGrid">
                <RelationBox title="Requirement IDs" values={item.related_requirement_ids || []} />
                <RelationBox title="Response Item IDs" values={item.related_response_item_ids || []} />
                <RelationBox title="Clarification IDs" values={item.related_clarification_ids || []} />
                <RelationBox title="Evidence IDs" values={item.related_evidence_item_ids || []} />
              </div>

              <div className="actionQuickControls">
                <button type="button" disabled={busy} onClick={() => updateRiskItem(item.id, { status: "mitigating" })}>
                  Mark Mitigating
                </button>
                <button type="button" disabled={busy} onClick={() => updateRiskItem(item.id, { status: "monitored" })}>
                  Monitor
                </button>
                <button type="button" disabled={busy} onClick={() => updateRiskItem(item.id, { status: "accepted" })}>
                  Accept
                </button>
                <button type="button" disabled={busy} onClick={() => updateRiskItem(item.id, { status: "closed" })}>
                  Close
                </button>
                <button type="button" disabled={busy} onClick={() => updateRiskItem(item.id, { status: "escalated", severity: "critical" })}>
                  Escalate
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

function ActionTrackerView({
  actionItems = [],
  busy,
  generateActionItems,
  updateActionItem,
}) {
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [ownerFilter, setOwnerFilter] = useState("all");
  const [sourceFilter, setSourceFilter] = useState("all");

  const safeItems = Array.isArray(actionItems) ? actionItems : [];

  const owners = useMemo(
    () => Array.from(new Set(safeItems.map((item) => item.owner).filter(Boolean))).sort(),
    [safeItems]
  );

  const sources = useMemo(
    () => Array.from(new Set(safeItems.map((item) => item.source_type).filter(Boolean))).sort(),
    [safeItems]
  );

  const filteredItems = safeItems.filter((item) => {
    if (statusFilter !== "all" && item.status !== statusFilter) return false;
    if (priorityFilter !== "all" && item.priority !== priorityFilter) return false;
    if (ownerFilter !== "all" && item.owner !== ownerFilter) return false;
    if (sourceFilter !== "all" && item.source_type !== sourceFilter) return false;
    return true;
  });

  const counts = {
    open: safeItems.filter((item) => item.status === "open").length,
    inProgress: safeItems.filter((item) => item.status === "in_progress").length,
    done: safeItems.filter((item) => item.status === "done").length,
    blocked: safeItems.filter((item) => item.status === "blocked").length,
    high: safeItems.filter((item) => item.priority === "high").length,
  };

  return (
    <div className="workspaceView actionTrackerView">
      <div className="viewHeader actionTrackerHeader">
        <div>
          <p className="eyebrow">Action Tracker</p>
          <h2>Operational task list for bid execution</h2>
          <p className="muted">
            Generated from high-risk requirements, open clarifications, response plan, evidence pack, and decision gate actions.
          </p>
        </div>

        <button
          type="button"
          className="regenerateAllButton"
          disabled={busy}
          onClick={generateActionItems}
        >
          Generate Action Items
        </button>
      </div>

      <div className="actionStatGrid">
        <ActionStat label="Total" value={safeItems.length} />
        <ActionStat label="Open" value={counts.open} tone="warning" />
        <ActionStat label="In Progress" value={counts.inProgress} />
        <ActionStat label="Done" value={counts.done} tone="ok" />
        <ActionStat label="Blocked" value={counts.blocked} tone="danger" />
        <ActionStat label="High Priority" value={counts.high} tone="danger" />
      </div>

      <div className="actionFilterBar">
        <label>
          Status
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="all">All status</option>
            <option value="open">Open</option>
            <option value="in_progress">In progress</option>
            <option value="done">Done</option>
            <option value="blocked">Blocked</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </label>

        <label>
          Priority
          <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
            <option value="all">All priority</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </label>

        <label>
          Owner
          <select value={ownerFilter} onChange={(e) => setOwnerFilter(e.target.value)}>
            <option value="all">All owners</option>
            {owners.map((owner) => (
              <option key={owner} value={owner}>{owner}</option>
            ))}
          </select>
        </label>

        <label>
          Source
          <select value={sourceFilter} onChange={(e) => setSourceFilter(e.target.value)}>
            <option value="all">All sources</option>
            {sources.map((source) => (
              <option key={source} value={source}>{source}</option>
            ))}
          </select>
        </label>
      </div>

      <div className="actionTrackerMeta">
        Showing <strong>{filteredItems.length}</strong> of <strong>{safeItems.length}</strong> action item(s)
      </div>

      {safeItems.length === 0 && (
        <div className="emptyState actionEmptyState">
          <h3>No action items yet</h3>
          <p>Generate action items from the latest tender artifacts to create an operational task list.</p>
          <button type="button" disabled={busy} onClick={generateActionItems}>
            Generate Action Items
          </button>
        </div>
      )}

      {safeItems.length > 0 && filteredItems.length === 0 && (
        <div className="emptyState actionEmptyState">
          <h3>No matching action items</h3>
          <p>Try adjusting the filters.</p>
        </div>
      )}

      <div className="actionItemGrid">
        {filteredItems.map((item) => (
          <ActionItemCard
            key={item.id}
            item={item}
            busy={busy}
            updateActionItem={updateActionItem}
          />
        ))}
      </div>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
