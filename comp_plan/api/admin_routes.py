"""Admin dashboard - standalone UI with stub API endpoints."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/dashboard")
def get_dashboard():
    """Stub dashboard stats."""
    return {
        "total_users": 0,
        "users_today": 0,
        "total_analyses": 0,
        "analyses_today": 0,
        "active_sessions_today": 0,
        "expired_sessions_today": 0,
        "avg_session_minutes": 0.0,
        "unread_visitors": 0,
    }


@router.get("/visitors")
def get_visitors(limit: int = 50, offset: int = 0):
    return []


@router.post("/visitors/mark-read")
def mark_visitors_read():
    return {"status": "ok"}


@router.get("/analyses")
def get_analyses(limit: int = 50, offset: int = 0):
    return []


@router.get("/analyses/{log_id}/debug")
def get_analysis_debug(log_id: str):
    return {"id": log_id, "message": "No debug data available in standalone mode"}


@router.get("/users")
def get_users(limit: int = 50, offset: int = 0):
    return []


@router.get("/sessions")
def get_sessions(limit: int = 50, offset: int = 0):
    return []


@router.get("/ui", response_class=HTMLResponse)
def admin_dashboard_ui():
    """Branded admin dashboard."""
    from comp_plan.api.landing import BRAND_CSS, SVG_MICROPLAN

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ICM PlanLytics - Admin Dashboard</title>
<style>
{BRAND_CSS}

.container {{
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px 28px 60px;
}}

.dash-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
  opacity: 0;
  animation: fadeUp 0.5s ease forwards;
}}
.dash-header-left {{
  display: flex;
  align-items: center;
  gap: 14px;
}}
.dash-header svg {{ width: 40px; height: 40px; }}
.dash-title {{
  font-family: 'Sora', sans-serif;
  font-size: 22px;
  font-weight: 700;
}}
.dash-title .icm {{ color: var(--accent-emerald); }}
.dash-title .plan  {{ color: var(--text-primary); }}
.dash-subtitle {{
  font-size: 12px;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
  margin-top: 2px;
}}
.dash-actions {{
  display: flex; gap: 10px; align-items: center;
}}
.refresh-btn, .home-btn {{
  padding: 8px 16px;
  border-radius: 8px;
  font-family: 'Sora', sans-serif;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid var(--border);
  transition: all 0.2s;
  text-decoration: none;
}}
.refresh-btn {{
  background: var(--bg-card);
  color: var(--accent-cyan);
}}
.refresh-btn:hover {{ background: var(--bg-card-hover); }}
.home-btn {{
  background: transparent;
  color: var(--text-secondary);
  border-color: var(--border);
}}
.home-btn:hover {{ background: var(--bg-card); color: var(--accent-cyan); }}

.stats-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
  opacity: 0;
  animation: fadeUp 0.5s ease 0.1s forwards;
}}
.stat-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px 22px;
  transition: all 0.2s;
}}
.stat-card:hover {{
  background: var(--bg-card-hover);
  border-color: rgba(59,130,246,0.2);
}}
.stat-label {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.8px;
  text-transform: uppercase;
  margin-bottom: 8px;
}}
.stat-value {{
  font-family: 'Sora', sans-serif;
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1;
}}
.stat-card.cyan .stat-value  {{ color: var(--accent-cyan); }}
.stat-card.blue .stat-value  {{ color: var(--accent-blue); }}
.stat-card.emerald .stat-value {{ color: var(--accent-emerald); }}
.stat-card.amber .stat-value {{ color: var(--accent-amber); }}
.stat-card.rose .stat-value  {{ color: var(--accent-rose); }}
.stat-sub {{
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}}

.nav-tabs {{
  display: flex;
  gap: 0;
  margin-bottom: 0;
  opacity: 0;
  animation: fadeUp 0.5s ease 0.15s forwards;
}}
.nav-tab {{
  padding: 12px 24px;
  font-family: 'Sora', sans-serif;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  background: transparent;
  border: 1px solid var(--border);
  border-bottom: none;
  border-radius: 10px 10px 0 0;
  cursor: pointer;
  transition: all 0.2s;
}}
.nav-tab:hover {{ color: var(--text-secondary); }}
.nav-tab.active {{
  color: var(--accent-cyan);
  background: var(--bg-card);
  border-color: var(--border);
}}

.content-panel {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 0 12px 12px 12px;
  padding: 24px;
  min-height: 400px;
  opacity: 0;
  animation: fadeUp 0.5s ease 0.2s forwards;
}}
.tab-pane {{ display: none; }}
.tab-pane.active {{ display: block; }}

.data-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}}
.data-table thead th {{
  text-align: left;
  padding: 10px 12px;
  font-family: 'Sora', sans-serif;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}}
.data-table tbody td {{
  padding: 10px 12px;
  border-bottom: 1px solid rgba(30,41,59,0.5);
  color: var(--text-secondary);
  vertical-align: top;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}}
.data-table tbody tr:hover td {{
  background: var(--bg-card-hover);
}}

.empty-state {{
  text-align: center;
  padding: 50px 20px;
  color: var(--text-muted);
}}
.empty-state .icon {{ font-size: 40px; margin-bottom: 12px; }}
.empty-state p {{ font-size: 14px; }}

@media (max-width: 768px) {{
  .container {{ padding: 16px; }}
  .stats-grid {{ grid-template-columns: repeat(2, 1fr); gap: 10px; }}
  .stat-value {{ font-size: 22px; }}
  .nav-tabs {{ overflow-x: auto; flex-wrap: nowrap; }}
  .nav-tab {{ padding: 10px 14px; font-size: 12px; white-space: nowrap; }}
  .dash-header {{ flex-direction: column; gap: 12px; }}
}}
</style>
</head>
<body>
<div class="page">
<div class="container">

  <div class="dash-header">
    <div class="dash-header-left">
      {SVG_MICROPLAN.replace('viewBox="0 0 72 72"', 'viewBox="0 0 72 72" width="40" height="40"')}
      <div>
        <div class="dash-title">
          <span class="icm">ICM</span> <span class="plan">PlanLytics</span>
          &nbsp;Admin
        </div>
        <div class="dash-subtitle">System monitoring &amp; analytics</div>
      </div>
    </div>
    <div class="dash-actions">
      <button class="refresh-btn" onclick="loadAll()">&#8635; Refresh</button>
      <a href="/" class="home-btn">&larr; Home</a>
    </div>
  </div>

  <div class="stats-grid" id="statsGrid">
    <div class="stat-card cyan">
      <div class="stat-label">Total Users</div>
      <div class="stat-value" id="st-total-users">--</div>
      <div class="stat-sub" id="st-users-today">-- new today</div>
    </div>
    <div class="stat-card blue">
      <div class="stat-label">Total Analyses</div>
      <div class="stat-value" id="st-total-analyses">--</div>
      <div class="stat-sub" id="st-analyses-today">-- today</div>
    </div>
    <div class="stat-card emerald">
      <div class="stat-label">Active Sessions</div>
      <div class="stat-value" id="st-active-sessions">--</div>
      <div class="stat-sub" id="st-expired-sessions">-- expired</div>
    </div>
    <div class="stat-card amber">
      <div class="stat-label">Avg Session</div>
      <div class="stat-value" id="st-avg-session">--</div>
      <div class="stat-sub">minutes</div>
    </div>
    <div class="stat-card rose">
      <div class="stat-label">Unread Visitors</div>
      <div class="stat-value" id="st-unread">--</div>
      <div class="stat-sub">pending review</div>
    </div>
  </div>

  <div class="nav-tabs">
    <div class="nav-tab active" onclick="switchTab('visitors')">Visitors</div>
    <div class="nav-tab" onclick="switchTab('analyses')">Analyses</div>
    <div class="nav-tab" onclick="switchTab('users')">Users</div>
    <div class="nav-tab" onclick="switchTab('sessions')">Sessions</div>
  </div>

  <div class="content-panel">
    <div id="pane-visitors" class="tab-pane active">
      <div class="empty-state"><div class="icon">&#128065;</div><p>No visitor logs yet</p></div>
    </div>
    <div id="pane-analyses" class="tab-pane">
      <div class="empty-state"><div class="icon">&#128202;</div><p>No analysis logs yet</p></div>
    </div>
    <div id="pane-users" class="tab-pane">
      <div class="empty-state"><div class="icon">&#128100;</div><p>No users yet</p></div>
    </div>
    <div id="pane-sessions" class="tab-pane">
      <div class="empty-state"><div class="icon">&#9202;</div><p>No session data yet</p></div>
    </div>
  </div>

</div>
</div>

<script>
  function switchTab(name) {{
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    const pane = document.getElementById('pane-' + name);
    if (pane) pane.classList.add('active');
    const tabs = document.querySelectorAll('.nav-tab');
    const map = {{ visitors: 0, analyses: 1, users: 2, sessions: 3 }};
    if (map[name] !== undefined) tabs[map[name]].classList.add('active');
  }}

  async function loadAll() {{
    try {{
      const r = await fetch('/admin/dashboard');
      const d = await r.json();
      document.getElementById('st-total-users').textContent = d.total_users;
      document.getElementById('st-users-today').textContent = d.users_today + ' new today';
      document.getElementById('st-total-analyses').textContent = d.total_analyses;
      document.getElementById('st-analyses-today').textContent = d.analyses_today + ' today';
      document.getElementById('st-active-sessions').textContent = d.active_sessions_today;
      document.getElementById('st-expired-sessions').textContent = d.expired_sessions_today + ' expired';
      document.getElementById('st-avg-session').textContent = d.avg_session_minutes;
      document.getElementById('st-unread').textContent = d.unread_visitors;
    }} catch(e) {{ console.error('Stats load error:', e); }}
  }}

  loadAll();
</script>
</body>
</html>"""
