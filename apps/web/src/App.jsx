import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { AlertTriangle, CheckCircle2, ClipboardCheck, FileQuestion, FileText, History, LayoutDashboard, MessageSquare, Plus, RefreshCw, ShieldCheck } from "lucide-react";
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
import ResponsePlanView from "./views/ResponsePlanView.jsx";
import ProposalOutlineView from "./views/ProposalOutlineView.jsx";
import EvidencePackView from "./views/EvidencePackView.jsx";
import ProposalTemplateView from "./views/ProposalTemplateView.jsx";
import ClarificationResponseTrackerView from "./views/ClarificationResponseTrackerView.jsx";
import AddendumImpactView from "./views/AddendumImpactView.jsx";
import ApprovalWorkflowView from "./views/ApprovalWorkflowView.jsx";
import TraceabilityMatrixView from "./views/TraceabilityMatrixView.jsx";

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
  const [workflowStatus, setWorkflowStatus] = useState(null);
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
      const [docs, reqs, qs, responseItems, proposalSections, evidenceItems, gate, gateHistory, addendumImpactData, clarificationTrackerData, proposalTemplateData, approvalData, complianceData, riskItemsData, actionItemsData, language, audits, summary, metadata, brief, workflowData] = await Promise.all([
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
        apiFetch(`/api/v1/projects/${projectId}/workflow-status`).catch(() => null),
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
      setWorkflowStatus(workflowData);

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
            requirements={requirements}
          />

          {activeProjectView === "summary" && (
            <SummaryView
              selectedProject={selectedProject}
              readinessSummary={readinessSummary}
              projectMetadata={projectMetadata}
              bidBrief={bidBrief}
              workflowStatus={workflowStatus}
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
              languageSetting={languageSetting}
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

          {activeProjectView === "traceability" && (
            <TraceabilityMatrixView
              requirements={requirements}
              responsePlan={responsePlan}
              evidencePack={evidencePack}
              proposalOutline={proposalOutline}
              clarifications={clarifications}
              complianceScorecard={complianceScorecard}
              riskItems={riskItems}
              actionItems={actionItems}
              languageSetting={languageSetting}
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
  const [quickFilter, setQuickFilter] = useState("all");

  const safeItems = Array.isArray(actionItems) ? actionItems : [];
  const doneStatuses = new Set(["done", "closed", "completed", "cancelled", "canceled"]);

  function parseActionDueDate(value) {
    if (!value) return null;
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
  }

  function isActionDone(item) {
    return doneStatuses.has(String(item.status || "").toLowerCase());
  }

  function isActionUnassigned(item) {
    return !String(item.owner || "").trim();
  }

  function isActionOverdue(item) {
    const dueDate = parseActionDueDate(item.due_date);
    if (!dueDate || isActionDone(item)) return false;

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    dueDate.setHours(0, 0, 0, 0);

    return dueDate < today;
  }

  function priorityRank(priority) {
    return { high: 0, medium: 1, low: 2 }[priority || "medium"] ?? 1;
  }

  function statusRank(status) {
    return {
      blocked: 0,
      open: 1,
      in_progress: 2,
      done: 5,
      cancelled: 6,
    }[status || "open"] ?? 3;
  }

  function actionSortRank(item) {
    if (isActionOverdue(item)) return -10;
    if (item.status === "blocked") return -5;
    if (isActionDone(item)) return 50;
    return statusRank(item.status);
  }

  const owners = useMemo(
    () => Array.from(new Set(safeItems.map((item) => item.owner).filter(Boolean))).sort(),
    [safeItems]
  );

  const sources = useMemo(
    () => Array.from(new Set(safeItems.map((item) => item.source_type).filter(Boolean))).sort(),
    [safeItems]
  );

  const filteredItems = safeItems
    .filter((item) => {
      if (quickFilter === "open" && item.status !== "open") return false;
      if (quickFilter === "overdue" && !isActionOverdue(item)) return false;
      if (quickFilter === "unassigned" && !isActionUnassigned(item)) return false;
      if (quickFilter === "blocked" && item.status !== "blocked") return false;
      if (quickFilter === "done" && !isActionDone(item)) return false;

      if (statusFilter !== "all" && item.status !== statusFilter) return false;
      if (priorityFilter !== "all" && item.priority !== priorityFilter) return false;
      if (ownerFilter !== "all" && item.owner !== ownerFilter) return false;
      if (sourceFilter !== "all" && item.source_type !== sourceFilter) return false;
      return true;
    })
    .sort((a, b) => {
      const rankDiff = actionSortRank(a) - actionSortRank(b);
      if (rankDiff !== 0) return rankDiff;

      const priorityDiff = priorityRank(a.priority) - priorityRank(b.priority);
      if (priorityDiff !== 0) return priorityDiff;

      return String(a.owner || "").localeCompare(String(b.owner || "")) || Number(a.id || 0) - Number(b.id || 0);
    });

  const counts = {
    open: safeItems.filter((item) => item.status === "open").length,
    inProgress: safeItems.filter((item) => item.status === "in_progress").length,
    done: safeItems.filter((item) => isActionDone(item)).length,
    blocked: safeItems.filter((item) => item.status === "blocked").length,
    high: safeItems.filter((item) => item.priority === "high").length,
    overdue: safeItems.filter((item) => isActionOverdue(item)).length,
    unassigned: safeItems.filter((item) => isActionUnassigned(item) && !isActionDone(item)).length,
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
        <ActionStat label="Overdue" value={counts.overdue} tone={counts.overdue > 0 ? "danger" : "ok"} />
        <ActionStat label="Unassigned" value={counts.unassigned} tone={counts.unassigned > 0 ? "warning" : "ok"} />
      </div>

      <div className="actionQuickFilterBar" aria-label="Action quick filters">
        {[
          ["all", "All"],
          ["open", "Open"],
          ["overdue", "Overdue"],
          ["unassigned", "Unassigned"],
          ["blocked", "Blocked"],
          ["done", "Done"],
        ].map(([key, label]) => (
          <button
            key={key}
            type="button"
            className={quickFilter === key ? "active" : ""}
            onClick={() => setQuickFilter(key)}
          >
            {label}
          </button>
        ))}
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
