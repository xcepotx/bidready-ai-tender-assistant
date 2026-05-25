import { apiFetch } from "../api/client.js";

export function useTenderProjectIntake({
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
}) {
  async function createProject(e) {
    e.preventDefault();

    if (!projectForm.title.trim()) {
      setMessage("Bid / RFP title is required.");
      return;
    }

    setBusy(true);
    setMessage("");

    try {
      const created = await apiFetch("/api/v1/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(projectForm),
      });

      setProjectForm(emptyProjectForm);
      await loadProjects();
      setSelectedProjectId(created.id);
      setActiveProjectView("summary");
      setMessage(`Bid project created: ${created.title}`);
    } catch (err) {
      setMessage(`Create bid project failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function uploadDocument(e) {
    e.preventDefault();

    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    if (!uploadFile) {
      setMessage("Choose a PDF file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", uploadFile);

    setBusy(true);
    setMessage("");

    try {
      const uploaded = await apiFetch(`/api/v1/projects/${selectedProjectId}/documents`, {
        method: "POST",
        body: formData,
      });

      setUploadFile(null);
      await loadProjects();
      await loadProjectData(selectedProjectId);
      setMessage(`RFP document processed: ${uploaded.filename}`);
    } catch (err) {
      setMessage(`Upload failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function analyzeRfp() {
    if (!selectedProjectId) {
      setMessage("Select a bid project first.");
      return;
    }

    setBusy(true);
    setMessage("");

    try {
      const extracted = await apiFetch(`/api/v1/projects/${selectedProjectId}/extract-requirements`, {
        method: "POST",
      });

      await loadProjects();
      await loadProjectData(selectedProjectId);
      if (extracted.length > 0) setSelectedRequirementId(extracted[0].id);
      setActiveProjectView("requirements");
      setMessage(`Analyzed ${extracted.length} requirement item(s).`);
    } catch (err) {
      setMessage(`Analysis failed: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return {
    createProject,
    uploadDocument,
    analyzeRfp,
  };
}
