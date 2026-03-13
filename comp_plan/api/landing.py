"""Landing page - branded MicroPlan AI homepage with route cards."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

# ---------------------------------------------------------------------------
# Shared CSS used across all pages
# ---------------------------------------------------------------------------
BRAND_CSS = """
:root {
  --bg-dark: #0a0b0f;
  --bg-card: #12141c;
  --bg-card-hover: #181b26;
  --accent-blue: #3b82f6;
  --accent-cyan: #06b6d4;
  --accent-emerald: #10b981;
  --accent-amber: #f59e0b;
  --accent-violet: #8b5cf6;
  --accent-rose: #f43f5e;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #475569;
  --border: #1e293b;
}

@font-face {
  font-family: 'Sora';
  font-style: normal;
  font-weight: 300 800;
  font-display: swap;
  src: local('Sora');
}
@font-face {
  font-family: 'DM Sans';
  font-style: normal;
  font-weight: 400 700;
  font-display: swap;
  src: local('DM Sans');
}
@font-face {
  font-family: 'JetBrains Mono';
  font-style: normal;
  font-weight: 400 600;
  font-display: swap;
  src: local('JetBrains Mono');
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: var(--bg-dark);
  color: var(--text-primary);
  font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
}

body::before {
  content: '';
  position: fixed;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 1;
}

.page { position: relative; z-index: 2; }

a { color: var(--accent-cyan); text-decoration: none; }
a:hover { text-decoration: underline; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
"""

# ---------------------------------------------------------------------------
# SVG icons
# ---------------------------------------------------------------------------
SVG_MICROPLAN = """<svg viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M36 4L62 20V52L36 68L10 52V20L36 4Z" stroke="#06b6d4" stroke-width="1.5" fill="none" opacity="0.4"/>
  <path d="M36 16L52 26V46L36 56L20 46V26L36 16Z" stroke="#3b82f6" stroke-width="1.5" fill="rgba(59,130,246,0.08)"/>
  <circle cx="36" cy="36" r="8" fill="url(#mpG)" opacity="0.9"/>
  <line x1="36" y1="28" x2="36" y2="16" stroke="#06b6d4" stroke-width="1" opacity="0.6"/>
  <line x1="43" y1="40" x2="52" y2="46" stroke="#06b6d4" stroke-width="1" opacity="0.6"/>
  <line x1="29" y1="40" x2="20" y2="46" stroke="#06b6d4" stroke-width="1" opacity="0.6"/>
  <circle cx="36" cy="14" r="3" fill="#06b6d4"/>
  <circle cx="53" cy="47" r="3" fill="#3b82f6"/>
  <circle cx="19" cy="47" r="3" fill="#10b981"/>
  <text x="36" y="40" text-anchor="middle" font-family="'Sora',sans-serif" font-size="12" font-weight="700" fill="#fff">&#181;</text>
  <defs><radialGradient id="mpG"><stop offset="0%" stop-color="#06b6d4"/><stop offset="100%" stop-color="#3b82f6"/></radialGradient></defs>
</svg>"""

SVG_AIDECKSMAN = """<svg viewBox="0 0 36 36" fill="none"><rect x="4" y="10" width="22" height="16" rx="2" stroke="#f59e0b" stroke-width="1.2" fill="rgba(245,158,11,0.1)"/><circle cx="28" cy="10" r="5" fill="#f59e0b" opacity="0.8"/><path d="M28 7V13M25 10H31" stroke="#fff" stroke-width="1" stroke-linecap="round"/></svg>"""

SVG_ICM = """<svg viewBox="0 0 36 36" fill="none"><circle cx="18" cy="18" r="12" stroke="#10b981" stroke-width="1.2" opacity="0.4"/><polyline points="8,24 14,20 20,22 26,16 30,10" stroke="#10b981" stroke-width="1.5" fill="none" stroke-linecap="round"/><circle cx="30" cy="10" r="3" fill="#10b981"/></svg>"""

SVG_MICROLLM = """<svg viewBox="0 0 36 36" fill="none"><path d="M18 4L30 10V22C30 28 24 32 18 34C12 32 6 28 6 22V10L18 4Z" stroke="#8b5cf6" stroke-width="1.2" fill="rgba(139,92,246,0.1)"/><circle cx="18" cy="18" r="4" fill="#8b5cf6" opacity="0.8"/><text x="18" y="21" text-anchor="middle" font-family="'Sora',sans-serif" font-size="6" font-weight="700" fill="#fff">&#181;</text></svg>"""


# ---------------------------------------------------------------------------
# Route cards
# ---------------------------------------------------------------------------
_ROUTE_CARDS = [
    ("/plan", "Plan Analysis", "Upload compensation plans for AI analysis with Oracle ICM mapping and PII scrubbing.", "var(--accent-emerald)", "/plan/ui",
     '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>'),
    ("/security", "PII Protection", "Scrub PII from text, manage tenant security profiles, and protect sensitive data.", "var(--accent-violet)", "/docs#/Security",
     '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'),
    ("/risk", "Guardrails & Risk", "Risk assessment, org dashboards, escalation workflows, and semantic content scanning.", "var(--accent-amber)", "/docs#/Risk",
     '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'),
    ("/llm", "LLM Operations", "Grounding verification, claim extraction, RAG verify, and conversation management.", "var(--accent-cyan)", "/docs#/LLM",
     '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>'),
    ("/deployment", "Deployment Modes", "Corporate laptop, BYOD cloud portal, and enterprise on-prem configurations.", "var(--accent-blue)", "/docs#/Deployment",
     '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>'),
    ("/o365", "Office 365", "Teams bot integration, Outlook email scanning, Copilot proxy, and Azure AD.", "var(--accent-blue)", "/docs#/Office365",
     '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 7L2 7"/></svg>'),
    ("/deck", "Pitch Decks", "AI-powered branded deck generation with PPTX export via AIDeckSMan bridge.", "var(--accent-amber)", "/docs#/PitchDecks",
     '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8"/><path d="M12 17v4"/><path d="M7 8h5"/><path d="M7 12h10"/></svg>'),
]


def _landing_html() -> str:
    cards_html = ""
    for i, (prefix, title, desc, color, link, icon) in enumerate(_ROUTE_CARDS):
        cards_html += f"""
        <a href="{link}" class="route-card" style="--card-accent: {color}">
          <div class="route-card-icon">{icon}</div>
          <div class="route-card-body">
            <h3>{title}</h3>
            <code>{prefix}</code>
            <p>{desc}</p>
          </div>
        </a>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ICM PlanLytics</title>
<style>
{BRAND_CSS}

.header {{
  text-align: center;
  padding: 60px 40px 20px;
  position: relative;
}}
.header::after {{
  content: '';
  position: absolute;
  top: 0; left: 50%;
  transform: translateX(-50%);
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%);
  pointer-events: none;
}}
.header-label {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: var(--accent-blue);
  margin-bottom: 16px;
  opacity: 0;
  animation: fadeUp 0.6s ease forwards;
}}
.hero-logo {{
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 12px;
  opacity: 0;
  animation: fadeUp 0.6s ease 0.1s forwards;
}}
.hero-logo svg {{ width: 72px; height: 72px; }}
.hero-text .brand {{
  font-family: 'Sora', sans-serif;
  font-size: 42px;
  font-weight: 800;
  letter-spacing: -1px;
  line-height: 1;
}}
.hero-text .brand .icm {{ color: var(--accent-emerald); }}
.hero-text .brand .plan {{ color: var(--text-primary); }}
.hero-text .brand .ai-badge {{
  font-size: 14px;
  font-weight: 600;
  color: var(--bg-dark);
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 8px;
  vertical-align: middle;
  letter-spacing: 1px;
}}
.hero-text .tagline-text {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  letter-spacing: 6px;
  color: var(--text-secondary);
  margin-top: 8px;
  text-transform: uppercase;
}}
.hero-text .tagline-text span:nth-child(1) {{ color: var(--accent-cyan); }}
.hero-text .tagline-text span:nth-child(2) {{ color: var(--accent-blue); }}
.hero-text .tagline-text span:nth-child(3) {{ color: var(--accent-emerald); }}

.header p.subtitle {{
  font-size: 16px;
  color: var(--text-secondary);
  margin-top: 16px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
  opacity: 0;
  animation: fadeUp 0.6s ease 0.2s forwards;
}}

.family-section {{
  max-width: 1100px;
  margin: 32px auto;
  padding: 0 40px;
  opacity: 0;
  animation: fadeUp 0.7s ease 0.3s forwards;
}}
.family-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
}}
.family-card::before {{
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(6,182,212,0.03), rgba(139,92,246,0.03), rgba(16,185,129,0.03));
}}
.family-label {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 20px;
  text-align: center;
  position: relative;
}}
.family-row {{
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 36px;
  flex-wrap: wrap;
  position: relative;
}}
.family-item {{
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0.85;
  transition: opacity 0.3s;
}}
.family-item:hover {{ opacity: 1; }}
.family-item svg {{ width: 32px; height: 32px; }}
.family-item .fi-name {{
  font-family: 'Sora', sans-serif;
  font-size: 15px;
  font-weight: 600;
}}
.family-divider {{
  width: 1px;
  height: 32px;
  background: var(--border);
}}

.routes-section {{
  max-width: 1100px;
  margin: 40px auto;
  padding: 0 40px;
}}
.routes-label {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 20px;
  opacity: 0;
  animation: fadeUp 0.6s ease 0.4s forwards;
}}
.routes-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}}
.route-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  gap: 16px;
  align-items: flex-start;
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0;
  animation: fadeUp 0.5s ease forwards;
}}
.route-card:nth-child(1) {{ animation-delay: 0.45s; }}
.route-card:nth-child(2) {{ animation-delay: 0.5s; }}
.route-card:nth-child(3) {{ animation-delay: 0.55s; }}
.route-card:nth-child(4) {{ animation-delay: 0.6s; }}
.route-card:nth-child(5) {{ animation-delay: 0.65s; }}
.route-card:nth-child(6) {{ animation-delay: 0.7s; }}
.route-card:nth-child(7) {{ animation-delay: 0.75s; }}
.route-card:hover {{
  background: var(--bg-card-hover);
  border-color: var(--card-accent, var(--accent-blue));
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.3);
  text-decoration: none;
}}
.route-card-icon {{
  flex-shrink: 0;
  width: 40px; height: 40px;
  background: rgba(255,255,255,0.04);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.route-card-body h3 {{
  font-family: 'Sora', sans-serif;
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 2px;
}}
.route-card-body code {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--card-accent, var(--accent-cyan));
  background: rgba(6,182,212,0.08);
  padding: 1px 6px;
  border-radius: 4px;
}}
.route-card-body p {{
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-top: 8px;
}}

.actions {{
  max-width: 1100px;
  margin: 40px auto 60px;
  padding: 0 40px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
  opacity: 0;
  animation: fadeUp 0.6s ease 0.8s forwards;
}}
.btn {{
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 500;
  padding: 10px 24px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-primary);
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
}}
.btn:hover {{
  background: var(--bg-card-hover);
  border-color: var(--accent-cyan);
  text-decoration: none;
}}
.btn-primary {{
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
  border-color: transparent;
  color: #fff;
  font-weight: 600;
}}
.btn-primary:hover {{
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(6,182,212,0.3);
}}

.footer {{
  text-align: center;
  padding: 24px 40px;
  font-size: 12px;
  color: var(--text-muted);
  border-top: 1px solid var(--border);
  font-family: 'JetBrains Mono', monospace;
}}

@media (max-width: 768px) {{
  .hero-text .brand {{ font-size: 28px; }}
  .routes-grid {{ grid-template-columns: 1fr; }}
  .family-row {{ gap: 16px; }}
  .family-divider {{ display: none; }}
}}
</style>
</head>
<body>
<div class="page">

  <div class="header">
    <div class="header-label">AI-Powered ICM Analysis</div>
    <div class="hero-logo">
      {SVG_ICM.replace('viewBox="0 0 36 36"', 'viewBox="0 0 36 36" width="72" height="72"')}
      <div class="hero-text">
        <div class="brand">
          <span class="icm">ICM</span> <span class="plan">PlanLytics</span>
        </div>
        <div class="tagline-text">
          <span>Analyze.</span> <span>Map.</span> <span>Protect.</span>
        </div>
      </div>
    </div>
    <p class="subtitle">AI-powered Incentive Compensation Plan Analysis with inherent PII scrubbing, Oracle ICM mapping, and multi-agent AI analysis. Enterprise-grade data security built in.</p>
  </div>

  <div class="family-section">
    <div class="family-card">
      <div class="family-label">The ICM PlanLytics Platform</div>
      <div class="family-row">
        <div class="family-item">
          {SVG_ICM}
          <span class="fi-name" style="color:#10b981">Plan Analysis</span>
        </div>
        <div class="family-divider"></div>
        <div class="family-item">
          {SVG_MICROLLM}
          <span class="fi-name" style="color:#8b5cf6">PII Protection</span>
        </div>
        <div class="family-divider"></div>
        <div class="family-item">
          {SVG_MICROPLAN.replace('viewBox="0 0 72 72"', 'viewBox="0 0 72 72" width="32" height="32"')}
          <span class="fi-name" style="color:#06b6d4">Oracle ICM Mapping</span>
        </div>
        <div class="family-divider"></div>
        <div class="family-item">
          {SVG_AIDECKSMAN}
          <span class="fi-name" style="color:#f59e0b">AI Agents</span>
        </div>
      </div>
    </div>
  </div>

  <div class="routes-section">
    <div class="routes-label">API Route Groups</div>
    <div class="routes-grid">
      {cards_html}
    </div>
  </div>

  <div class="actions">
    <a href="/auth/ui" class="btn btn-primary">Sign In / Register</a>
    <a href="/plan/ui" class="btn">Analyze Plan</a>
    <a href="/admin/ui" class="btn">Admin Dashboard</a>
    <a href="/docs" class="btn">API Docs</a>
    <a href="/plan/healthz" class="btn">Health Check</a>
  </div>

  <div class="footer">ICM PlanLytics v1.0.0 &mdash; AI-Powered Compensation Plan Analysis</div>

</div>
</body>
</html>"""


@router.get("/", response_class=HTMLResponse)
def landing_page():
    return _landing_html()


@router.get("/api/info")
def api_info():
    return {
        "service": "ICM PlanLytics",
        "version": "1.0.0",
        "capabilities": {
            "plan_analysis": "AI-powered Incentive Compensation Plan Analysis",
            "oracle_mapping": "Oracle ICM object mapping and export",
            "pii_protection": "Inherent PII scrubbing at every data transfer",
            "ai_agents": "Multi-agent analysis (document, risk, Oracle)",
        },
        "route_groups": [
            "/plan - Plan Analysis (upload, analyze, export)",
            "/auth - Authentication (sign in, register)",
            "/admin - Admin Dashboard (stats, logs)",
        ],
    }


@router.get("/healthz")
def healthz():
    return {"status": "ok", "service": "icm-planlytics", "version": "1.0.0"}
