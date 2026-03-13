"""Auth UI - standalone sign in / register / forgot password page."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.post("/login")
def login(body: dict):
    """Stub login - returns demo token."""
    return {
        "access_token": "demo-token",
        "refresh_token": "demo-refresh",
        "token_type": "bearer",
        "expires_in": 3600,
        "user_id": "demo-user",
        "tenant_id": "demo-tenant",
    }


@router.post("/register")
def register(body: dict):
    """Stub registration."""
    return {"message": "Registration successful! You can now sign in."}


@router.post("/forgot-password")
def forgot_password(body: dict):
    """Stub forgot password."""
    return {"message": "If that email is registered, a password reset link has been sent."}


@router.post("/reset-password")
def reset_password(body: dict):
    """Stub reset password."""
    return {"message": "Password reset successful. You can now sign in with your new password."}


@router.get("/ui", response_class=HTMLResponse)
def auth_ui():
    """Branded auth page with Sign In, Register, and Forgot Password."""
    from comp_plan.api.landing import BRAND_CSS, SVG_MICROPLAN

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ICM PlanLytics - Sign In</title>
<style>
{BRAND_CSS}

.container {{
  max-width: 480px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}}

.page-header {{
  text-align: center;
  margin-bottom: 32px;
  opacity: 0;
  animation: fadeUp 0.6s ease forwards;
}}
.page-header svg {{ width: 56px; height: 56px; margin-bottom: 12px; }}
.page-header .brand {{
  font-family: 'Sora', sans-serif;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
}}
.page-header .brand .icm {{ color: var(--accent-emerald); }}
.page-header .brand .plan {{ color: var(--text-primary); }}
.back-link {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 24px;
  display: block;
  text-align: center;
  opacity: 0;
  animation: fadeUp 0.5s ease 0.1s forwards;
}}
.back-link:hover {{ color: var(--accent-cyan); }}

.tabs {{
  display: flex;
  gap: 0;
  margin-bottom: 0;
  opacity: 0;
  animation: fadeUp 0.6s ease 0.15s forwards;
}}
.tab {{
  flex: 1;
  padding: 14px 0;
  text-align: center;
  font-family: 'Sora', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
  background: transparent;
  border: 1px solid var(--border);
  border-bottom: none;
  border-radius: 12px 12px 0 0;
  cursor: pointer;
  transition: all 0.2s;
}}
.tab:hover {{ color: var(--text-secondary); }}
.tab.active {{
  color: var(--accent-cyan);
  background: var(--bg-card);
  border-color: var(--border);
}}

.form-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 0 0 16px 16px;
  padding: 32px;
  opacity: 0;
  animation: fadeUp 0.6s ease 0.2s forwards;
}}

.field {{
  margin-bottom: 20px;
}}
.field label {{
  display: block;
  font-family: 'Sora', sans-serif;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
  letter-spacing: 0.5px;
}}
.field input {{
  width: 100%;
  padding: 12px 14px;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}}
.field input:focus {{
  border-color: var(--accent-cyan);
}}
.field input::placeholder {{
  color: var(--text-muted);
}}

.submit-btn {{
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
  border: none;
  border-radius: 10px;
  color: #fff;
  font-family: 'Sora', sans-serif;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 8px;
}}
.submit-btn:hover {{
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(6,182,212,0.3);
}}
.submit-btn:disabled {{
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}}

.form-footer {{
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: var(--text-muted);
}}
.form-footer a {{
  color: var(--accent-cyan);
  cursor: pointer;
}}

.msg {{
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 13px;
  display: none;
}}
.msg.error {{
  background: rgba(244,63,94,0.08);
  border: 1px solid rgba(244,63,94,0.2);
  color: var(--accent-rose);
  display: block;
}}
.msg.success {{
  background: rgba(16,185,129,0.08);
  border: 1px solid rgba(16,185,129,0.2);
  color: var(--accent-emerald);
  display: block;
}}

.pw-strength {{
  height: 4px;
  border-radius: 2px;
  margin-top: 8px;
  background: var(--border);
  overflow: hidden;
}}
.pw-strength-bar {{
  height: 100%;
  border-radius: 2px;
  width: 0%;
  transition: width 0.3s, background 0.3s;
}}

.panel {{ display: none; }}
.panel.active {{ display: block; }}
</style>
</head>
<body>
<div class="page">
<div class="container">

  <a href="/" class="back-link">&larr; Back to Dashboard</a>

  <div class="page-header">
    {SVG_MICROPLAN.replace('viewBox="0 0 72 72"', 'viewBox="0 0 72 72" width="56" height="56"')}
    <div class="brand">
      <span class="icm">ICM</span> <span class="plan">PlanLytics</span>
    </div>
  </div>

  <div id="globalMsg" class="msg"></div>

  <div class="tabs">
    <div class="tab active" onclick="showTab('signin')">Sign In</div>
    <div class="tab" onclick="showTab('register')">Register</div>
    <div class="tab" onclick="showTab('forgot')">Forgot Password</div>
  </div>

  <div class="form-card">

    <div id="panel-signin" class="panel active">
      <form id="signinForm" onsubmit="return handleSignin(event)">
        <div class="field">
          <label>Email</label>
          <input type="email" id="si-email" placeholder="you@company.com" required />
        </div>
        <div class="field">
          <label>Password</label>
          <input type="password" id="si-password" placeholder="Your password" required />
        </div>
        <div id="si-msg" class="msg"></div>
        <button type="submit" class="submit-btn" id="si-btn">Sign In</button>
        <div class="form-footer">
          <a onclick="showTab('forgot')">Forgot your password?</a>
          &nbsp;&middot;&nbsp;
          <a onclick="showTab('register')">Create an account</a>
        </div>
      </form>
    </div>

    <div id="panel-register" class="panel">
      <form id="registerForm" onsubmit="return handleRegister(event)">
        <div class="field">
          <label>Full Name</label>
          <input type="text" id="reg-name" placeholder="Jane Smith" required />
        </div>
        <div class="field">
          <label>Email</label>
          <input type="email" id="reg-email" placeholder="you@company.com" required />
        </div>
        <div class="field">
          <label>Company</label>
          <input type="text" id="reg-company" placeholder="Acme Corp" required />
        </div>
        <div class="field">
          <label>Password</label>
          <input type="password" id="reg-password" placeholder="Min 8 characters" required minlength="8" oninput="updatePwStrength(this.value)" />
          <div class="pw-strength"><div class="pw-strength-bar" id="pw-bar"></div></div>
        </div>
        <div class="field">
          <label>Confirm Password</label>
          <input type="password" id="reg-confirm" placeholder="Repeat password" required />
        </div>
        <div id="reg-msg" class="msg"></div>
        <button type="submit" class="submit-btn" id="reg-btn">Create Account</button>
        <div class="form-footer">
          Already have an account? <a onclick="showTab('signin')">Sign In</a>
        </div>
      </form>
    </div>

    <div id="panel-forgot" class="panel">
      <form id="forgotForm" onsubmit="return handleForgot(event)">
        <p style="color:var(--text-secondary);font-size:14px;margin-bottom:20px;">
          Enter your email and we'll send you a link to reset your password.
        </p>
        <div class="field">
          <label>Email</label>
          <input type="email" id="fg-email" placeholder="you@company.com" required />
        </div>
        <div id="fg-msg" class="msg"></div>
        <button type="submit" class="submit-btn" id="fg-btn">Send Reset Link</button>
        <div class="form-footer">
          <a onclick="showTab('signin')">Back to Sign In</a>
        </div>
      </form>
    </div>

  </div>
</div>
</div>

<script>
  function showTab(name) {{
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    const panel = document.getElementById('panel-' + name);
    if (panel) panel.classList.add('active');
    const tabs = document.querySelectorAll('.tab');
    const tabMap = {{'signin': 0, 'register': 1, 'forgot': 2}};
    if (tabMap[name] !== undefined) tabs[tabMap[name]].classList.add('active');
    document.querySelectorAll('.msg').forEach(m => {{ m.className = 'msg'; m.textContent = ''; }});
  }}

  function showMsg(id, text, type) {{
    const el = document.getElementById(id);
    el.className = 'msg ' + type;
    el.textContent = text;
  }}

  function updatePwStrength(pw) {{
    const bar = document.getElementById('pw-bar');
    let score = 0;
    if (pw.length >= 8) score++;
    if (pw.length >= 12) score++;
    if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
    if (/[0-9]/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;
    const pct = Math.min(score * 20, 100);
    const colors = ['#f43f5e', '#f59e0b', '#f59e0b', '#10b981', '#10b981'];
    bar.style.width = pct + '%';
    bar.style.background = colors[Math.min(score, 4)];
  }}

  async function handleSignin(e) {{
    e.preventDefault();
    const btn = document.getElementById('si-btn');
    btn.disabled = true; btn.textContent = 'Signing in...';
    try {{
      const r = await fetch('/auth/login', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
          email: document.getElementById('si-email').value,
          password: document.getElementById('si-password').value
        }})
      }});
      const j = await r.json();
      if (!r.ok) {{
        showMsg('si-msg', j.detail || 'Login failed', 'error');
        btn.disabled = false; btn.textContent = 'Sign In';
        return false;
      }}
      localStorage.setItem('mp_access_token', j.access_token);
      showMsg('si-msg', 'Signed in successfully! Redirecting...', 'success');
      setTimeout(() => window.location.href = '/plan/ui', 800);
    }} catch(err) {{
      showMsg('si-msg', 'Network error: ' + err, 'error');
      btn.disabled = false; btn.textContent = 'Sign In';
    }}
    return false;
  }}

  async function handleRegister(e) {{
    e.preventDefault();
    const pw = document.getElementById('reg-password').value;
    const confirm = document.getElementById('reg-confirm').value;
    if (pw !== confirm) {{
      showMsg('reg-msg', 'Passwords do not match', 'error');
      return false;
    }}
    const btn = document.getElementById('reg-btn');
    btn.disabled = true; btn.textContent = 'Creating account...';
    try {{
      const r = await fetch('/auth/register', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
          email: document.getElementById('reg-email').value,
          password: pw,
          full_name: document.getElementById('reg-name').value,
          company: document.getElementById('reg-company').value
        }})
      }});
      const j = await r.json();
      if (!r.ok) {{
        showMsg('reg-msg', j.detail || 'Registration failed', 'error');
        btn.disabled = false; btn.textContent = 'Create Account';
        return false;
      }}
      showMsg('reg-msg', j.message || 'Account created! You can now sign in.', 'success');
      btn.textContent = 'Account Created';
    }} catch(err) {{
      showMsg('reg-msg', 'Network error: ' + err, 'error');
      btn.disabled = false; btn.textContent = 'Create Account';
    }}
    return false;
  }}

  async function handleForgot(e) {{
    e.preventDefault();
    const btn = document.getElementById('fg-btn');
    btn.disabled = true; btn.textContent = 'Sending...';
    try {{
      const r = await fetch('/auth/forgot-password', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{ email: document.getElementById('fg-email').value }})
      }});
      const j = await r.json();
      showMsg('fg-msg', j.message || 'Check your email for the reset link.', 'success');
      btn.textContent = 'Check your email';
    }} catch(err) {{
      showMsg('fg-msg', 'Network error: ' + err, 'error');
      btn.disabled = false; btn.textContent = 'Send Reset Link';
    }}
    return false;
  }}
</script>
</body>
</html>"""
