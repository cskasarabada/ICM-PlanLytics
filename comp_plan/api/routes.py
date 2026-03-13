"""comp_plan API routes - Plan analysis with inherent PII security.

POST /plan/analyze       - Upload document + get secured analysis
GET  /plan/ui            - HTML upload form
POST /plan/oracle-export - Prepare secured data for Oracle
GET  /plan/healthz       - Health check
"""

import json
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from comp_plan.models.schemas import TemplateName
from comp_plan.security.secure_pipeline import run_secure_analysis
from comp_plan.security.oracle_security import prepare_oracle_export
from comp_plan.security.pii_scrubber import auto_protect

router = APIRouter()

DATA_DIR = Path("data")
UPLOADS = DATA_DIR / "uploads"
OUTPUTS = DATA_DIR / "outputs"
UPLOADS.mkdir(parents=True, exist_ok=True)
OUTPUTS.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTS = {".docx", ".pdf", ".txt"}


def _file_url(p: Path) -> str:
    return f"/files/{p.name}"


async def _save_upload(file: UploadFile, dest_dir: Path, job_id: str) -> Path:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(400, f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTS}")

    max_bytes = 50 * 1024 * 1024  # 50MB default
    dest = dest_dir / f"{job_id}__{file.filename}"

    size = 0
    with open(dest, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                dest.unlink(missing_ok=True)
                raise HTTPException(413, f"File exceeds 50 MB limit")
            f.write(chunk)
    return dest


@router.get("/healthz")
def healthz():
    return {"status": "ok", "subsystem": "comp_plan"}


@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    template: TemplateName = Form("master"),
    tenant_id: Optional[str] = Form(None),
    org_id: Optional[str] = Form(None),
):
    """Upload a compensation plan document and get secured AI analysis.

    PII is automatically scrubbed at every stage of processing.
    """
    job_id = uuid.uuid4().hex[:12]

    try:
        src_path = await _save_upload(file, UPLOADS, job_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {e}")

    try:
        analysis = run_secure_analysis(
            file_path=src_path,
            template=template,
            tenant_id=tenant_id,
            org_id=org_id,
        )
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {e}")

    # Export results
    try:
        from comp_plan.core.exports import to_excel, simple_html_summary

        excel_path = OUTPUTS / f"{job_id}__analysis.xlsx"
        to_excel(analysis, excel_path)

        json_path = OUTPUTS / f"{job_id}__analysis.json"
        export_analysis = {k: v for k, v in analysis.items() if not k.startswith("_")}
        json_path.write_text(json.dumps(export_analysis, indent=2, default=str))

        html_path = OUTPUTS / f"{job_id}__analysis.html"
        html_content = simple_html_summary(analysis)
        html_path.write_text(html_content)
    except Exception as e:
        raise HTTPException(500, f"Export failed: {e}")

    return JSONResponse({
        "message": "ok",
        "template": str(template),
        "excel_url": _file_url(excel_path),
        "html_url": _file_url(html_path),
        "analysis_json_url": _file_url(json_path),
        "security": analysis.get("_security", {}),
    })


@router.post("/oracle-export")
async def oracle_export(
    file: UploadFile = File(...),
    template: TemplateName = Form("master"),
    tenant_id: Optional[str] = Form(None),
    org_id: Optional[str] = Form(None),
):
    """Analyze a document and return Oracle-export-ready data.

    Additional security pass specifically for Oracle ICM integration.
    PII scrubbing is inherent and automatic.
    """
    job_id = uuid.uuid4().hex[:12]

    try:
        src_path = await _save_upload(file, UPLOADS, job_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {e}")

    try:
        analysis = run_secure_analysis(
            file_path=src_path,
            template=template,
            tenant_id=tenant_id,
            org_id=org_id,
        )
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {e}")

    security = auto_protect(tenant_id or "default")
    export = prepare_oracle_export(analysis, security)

    return JSONResponse({
        "message": "ok",
        "template": str(template),
        "oracle_export": export,
    })


@router.get("/ui", response_class=HTMLResponse)
def ui():
    """Upload form for plan analysis."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ICM PlanLytics - Compensation Plan Analysis</title>
<style>
:root {
  --bg-dark: #0f1117; --bg-card: #1a1d27; --border: #2a2d3a;
  --text-primary: #e4e4e7; --text-secondary: #a1a1aa; --text-muted: #71717a;
  --accent-cyan: #06b6d4; --accent-blue: #3b82f6;
  --accent-emerald: #10b981; --accent-amber: #f59e0b; --accent-rose: #f43f5e;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'DM Sans', -apple-system, sans-serif; background: var(--bg-dark); color: var(--text-primary); }
a { color: var(--accent-cyan); text-decoration: none; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.container { max-width: 720px; margin: 0 auto; padding: 40px 24px 60px; }
.page-header { display: flex; align-items: center; gap: 16px; margin-bottom: 32px; opacity: 0; animation: fadeUp 0.6s ease forwards; }
.page-header h1 { font-size: 24px; font-weight: 700; }
.page-header h1 .micro { color: var(--accent-cyan); }
.page-header .sub { font-size: 11px; letter-spacing: 2px; color: var(--accent-emerald); text-transform: uppercase; margin-top: 2px; }
.form-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 32px; opacity: 0; animation: fadeUp 0.6s ease 0.2s forwards; }
.dropzone { border: 2px dashed var(--border); border-radius: 12px; padding: 40px 24px; text-align: center; cursor: pointer; transition: all 0.3s; margin-bottom: 24px; position: relative; }
.dropzone:hover { border-color: var(--accent-cyan); background: rgba(6,182,212,0.04); }
.dropzone .dz-label { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
.dropzone .dz-sub { font-size: 13px; color: var(--text-muted); }
.dropzone .dz-formats { display: flex; gap: 8px; justify-content: center; margin-top: 12px; }
.dropzone .fmt { font-size: 11px; padding: 2px 10px; border-radius: 4px; background: rgba(6,182,212,0.08); color: var(--accent-cyan); }
.dropzone input[type="file"] { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
.file-name { font-size: 12px; color: var(--accent-emerald); margin-top: 8px; display: none; }
.field { margin-bottom: 20px; }
.field label { display: block; font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px; }
.field select, .field input[type="text"] { width: 100%; padding: 10px 14px; background: var(--bg-dark); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-size: 14px; outline: none; }
.field select:focus, .field input[type="text"]:focus { border-color: var(--accent-cyan); }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.submit-btn { width: 100%; padding: 14px; background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue)); border: none; border-radius: 10px; color: #fff; font-size: 15px; font-weight: 700; cursor: pointer; transition: all 0.2s; margin-top: 8px; }
.submit-btn:hover { opacity: 0.9; transform: translateY(-1px); box-shadow: 0 4px 20px rgba(6,182,212,0.3); }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.result-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-top: 24px; }
.result-card h3 { font-size: 16px; font-weight: 700; color: var(--accent-emerald); margin-bottom: 16px; }
.result-card .dl-link { display: block; padding: 8px 12px; background: rgba(16,185,129,0.06); border: 1px solid rgba(16,185,129,0.15); border-radius: 8px; margin-bottom: 8px; font-size: 14px; }
.pii-warning { background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.2); border-radius: 8px; padding: 12px 16px; margin-top: 12px; font-size: 13px; color: var(--accent-amber); }
.error-msg { background: rgba(244,63,94,0.06); border: 1px solid rgba(244,63,94,0.2); border-radius: 8px; padding: 12px 16px; margin-top: 12px; font-size: 13px; color: var(--accent-rose); }
.analyzing { text-align: center; padding: 24px; color: var(--text-secondary); }
.spinner { display: inline-block; width: 24px; height: 24px; border: 3px solid var(--border); border-top-color: var(--accent-cyan); border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 12px; }
@keyframes spin { to { transform: rotate(360deg); } }
.pii-badge { display: inline-block; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); color: var(--accent-emerald); font-size: 11px; padding: 2px 8px; border-radius: 4px; margin-left: 8px; }
</style>
</head>
<body>
<div class="container">
  <div class="page-header">
    <div>
      <h1><span class="micro">ICM</span> PlanLytics</h1>
      <div class="sub">Compensation Plan Analysis <span class="pii-badge">PII Protected</span></div>
    </div>
  </div>
  <div class="form-card">
    <form id="f" enctype="multipart/form-data">
      <div class="dropzone" id="dropzone">
        <div class="dz-label">Drop your plan document here</div>
        <div class="dz-sub">or click to browse</div>
        <div class="dz-formats">
          <span class="fmt">.docx</span><span class="fmt">.pdf</span><span class="fmt">.txt</span>
        </div>
        <input type="file" name="file" id="fileInput" accept=".docx,.pdf,.txt" required />
        <div class="file-name" id="fileName"></div>
      </div>
      <div class="field">
        <label>Analysis Template</label>
        <select name="template">
          <option value="master">Master</option>
          <option value="automation_framework">Automation Framework</option>
          <option value="side_by_side">Side-by-Side</option>
          <option value="risk_assessment">Risk Assessment</option>
          <option value="oracle_mapping">Oracle Mapping</option>
          <option value="quick_analysis">Quick Analysis</option>
        </select>
      </div>
      <div class="field-row">
        <div class="field"><label>Tenant ID</label><input type="text" name="tenant_id" placeholder="optional" /></div>
        <div class="field"><label>Org ID</label><input type="text" name="org_id" placeholder="optional" /></div>
      </div>
      <button type="submit" class="submit-btn" id="submitBtn">Analyze Plan</button>
    </form>
    <div id="result"></div>
  </div>
</div>
<script>
const fi = document.getElementById('fileInput');
const fn = document.getElementById('fileName');
fi.addEventListener('change', () => { if (fi.files.length) { fn.textContent = fi.files[0].name; fn.style.display = 'block'; } });
document.getElementById('f').onsubmit = async (e) => {
  e.preventDefault();
  const btn = document.getElementById('submitBtn');
  const res = document.getElementById('result');
  btn.disabled = true; btn.textContent = 'Analyzing...';
  res.innerHTML = '<div class="analyzing"><div class="spinner"></div><div>Processing through PII scrubbing and AI analysis...</div></div>';
  try {
    const fd = new FormData(e.target);
    const r = await fetch('/plan/analyze', {method: 'POST', body: fd});
    const j = await r.json();
    if (!r.ok) { res.innerHTML = '<div class="error-msg">' + (j.detail || 'Analysis failed') + '</div>'; btn.disabled = false; btn.textContent = 'Analyze Plan'; return; }
    let html = '<div class="result-card"><h3>Analysis Complete</h3>';
    if (j.excel_url) html += '<a href="' + j.excel_url + '" class="dl-link">Download Excel Report</a>';
    if (j.html_url) html += '<a href="' + j.html_url + '" class="dl-link">View HTML Summary</a>';
    if (j.analysis_json_url) html += '<a href="' + j.analysis_json_url + '" class="dl-link">View JSON Data</a>';
    html += '</div>';
    if (j.security && j.security.pii_scrubbed) { html += '<div class="pii-warning">PII was detected and scrubbed before analysis: ' + (j.security.pii_summary || 'sensitive data removed') + '</div>'; }
    res.innerHTML = html;
  } catch(err) { res.innerHTML = '<div class="error-msg">Error: ' + err + '</div>'; }
  btn.disabled = false; btn.textContent = 'Analyze Plan';
};
</script>
</body>
</html>"""
