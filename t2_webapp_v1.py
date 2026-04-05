#!/usr/bin/env python3
"""
t2_webapp_v1.py — T2 Tri-Core Web Dashboard (Pure Python, Zero Dependencies)
==============================================================
A self-contained web app using only Python standard library.
No pip install needed — runs out of the box.

Features:
- Auto-scan T1 output directories for latest JSON
- Live Markdown preview with syntax highlighting
- One-click PDF/HTML export
- Multi-Asset preview table
- Dark OTengine4 theme

Run:
    python3 t2_webapp_v1.py
    Then open: http://localhost:8501

Author: T2 Tri-Core v2.1 / OTengine4
Date: 2026-04-05
"""

import json, os, re, subprocess, threading
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

PORT = 8501
T2_DIR = Path(__file__).parent.resolve()
INTEGRATOR = T2_DIR / "t2_integrator.py"
OUTPUT_DIR = T2_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

T1_DIRS = [
    T2_DIR.parent / "t1-tricore/output/",
    T2_DIR.parent / "t1-tricore/output/radar/",
    T2_DIR.parent / "t1/outputs/",
    T2_DIR.parent / "T1/output/",
]

def find_latest_t1_json():
    candidates = []
    for d in T1_DIRS:
        if not d.exists(): continue
        for f in d.glob("*.json"):
            try:
                content = json.loads(f.read_text(encoding="utf-8"))
                if any(k in content for k in ['threat_summary', 'battle_card', 'risk_score', 'asset_analysis']):
                    candidates.append((str(f), f.stat().st_mtime))
            except: continue
    if not candidates: return None
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]

def md_to_html(md):
    html = md.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    html = re.sub(r'```[\w]*\n(.*?)\n```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`([^`]+)`', r'<code class="inline">\1</code>', html)
    for i in range(6, 0, -1):
        html = re.sub(rf'^{"#"*i} (.+)$', lambda m: f'<h{i}>{m.group(1)}</h{i}>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    def table_row(m):
        cells = ''.join(f'<td>{c.strip()}</td>' for c in m.group(1).split('|') if c.strip())
        return f'<tr>{cells}</tr>'
    html = re.sub(r'\|(.+)\|', table_row, html)
    html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    html = re.sub(r'^---$', '<hr>', html, flags=re.MULTILINE)
    return html

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): print(f"[T2-WebApp] {fmt % args}")
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        if self.path == "/" or self.path == "/index":
            self.serve_page()
        elif self.path.startswith("/static/"):
            self.serve_static()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == "/api/generate":
            self.handle_generate()
        else:
            self.send_error(404)
    
    def serve_page(self):
        latest = find_latest_t1_json()
        welcome = f"""# 🛡️ OTengine4 T2 Dashboard

## พร้อมใช้งาน

**T1 Intel:** {'✅ พบไฟล์ล่าสุด — ' + Path(latest).name if latest else '⚠️ ไม่พบ T1 JSON'}

กด **⚡ Generate Autonomous Policy** เพื่อเริ่มต้น

---
*Policy Tier: Base ฿95K → Enterprise ฿395K*
"""
        html = self.render_page(md_to_html(welcome), latest)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def render_page(self, content_html, latest_t1=None):
        return f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OTengine4 T2 Dashboard</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', sans-serif; background: #0a0e1a; color: #e2e8f0; min-height: 100vh; }}
.topbar {{ background: linear-gradient(135deg, #0f1629, #1a2744); border-bottom: 1px solid #1e3a5f;
           padding: 0 32px; height: 64px; display: flex; align-items: center;
           justify-content: space-between; position: sticky; top: 0; z-index: 100; }}
.topbar .brand {{ display: flex; align-items: center; gap: 12px; }}
.topbar .logo {{ font-size: 24px; }}
.topbar .name {{ font-size: 18px; font-weight: 700; color: #60a5fa; }}
.topbar .sub {{ font-size: 11px; color: #64748b; }}
.topbar .badge {{ background: #1e3a5f; border: 1px solid #3b82f6; color: #60a5fa;
                   padding: 6px 16px; border-radius: 20px; font-size: 12px; font-family: monospace; }}
.main {{ display: flex; min-height: calc(100vh - 64px); }}
.sidebar {{ width: 300px; background: #111827; border-right: 1px solid #1f2937; padding: 24px; flex-shrink: 0; overflow-y: auto; }}
.sidebar h3 {{ color: #60a5fa; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin: 20px 0 10px; }}
.sidebar h3:first-child {{ margin-top: 0; }}
.form-group {{ margin-bottom: 14px; }}
.form-group label {{ display: block; color: #94a3b8; font-size: 12px; margin-bottom: 6px; }}
.form-group input, .form-group select {{ width: 100%; background: #1a2744; border: 1px solid #2a3f5f; color: #e2e8f0; padding: 10px 12px; border-radius: 8px; font-size: 14px; }}
.form-group input:focus, .form-group select:focus {{ outline: none; border-color: #3b82f6; }}
.checkbox-item {{ display: flex; align-items: center; gap: 8px; margin: 6px 0; cursor: pointer; }}
.checkbox-item input {{ width: 16px; height: 16px; accent-color: #3b82f6; }}
.checkbox-item span {{ color: #cbd5e1; font-size: 13px; }}
.btn {{ display: block; width: 100%; padding: 14px 20px; border-radius: 10px; font-size: 14px;
        font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; margin-top: 16px; }}
.btn-primary {{ background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; }}
.btn-primary:hover {{ background: linear-gradient(135deg, #1e3a8a, #60a5fa); transform: translateY(-1px); }}
.btn:disabled {{ opacity: 0.5; cursor: not-allowed; transform: none; }}
.content {{ flex: 1; padding: 24px; overflow-y: auto; }}
.status-bar {{ display: flex; gap: 12px; margin-bottom: 20px; display: none; }}
.status-card {{ background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 16px 20px; flex: 1; text-align: center; }}
.status-card .label {{ font-size: 11px; color: #64748b; text-transform: uppercase; }}
.status-card .value {{ font-size: 20px; font-weight: 700; color: #60a5fa; margin-top: 4px; }}
.empty-state {{ text-align: center; padding: 100px 40px; color: #64748b; }}
.empty-state .icon {{ font-size: 56px; margin-bottom: 16px; }}
.empty-state h3 {{ color: #94a3b8; font-size: 20px; margin-bottom: 8px; }}
.doc-preview {{ background: #111827; border: 1px solid #1f2937; border-radius: 16px; padding: 28px; display: none; }}
.preview-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #1f2937; }}
.preview-title {{ color: #60a5fa; font-size: 16px; font-weight: 600; }}
.doc-actions {{ display: flex; gap: 8px; }}
.btn-sm {{ padding: 8px 14px; font-size: 12px; border-radius: 8px; border: 1px solid #3b82f6; background: #1e3a5f; color: #60a5fa; cursor: pointer; }}
.btn-sm:hover {{ background: #1e3a8a; }}
.doc-body {{ color: #cbd5e1; font-size: 14px; line-height: 1.8; }}
.doc-body h1 {{ color: #60a5fa; font-size: 22px; border-bottom: 2px solid #1e3a5f; padding-bottom: 12px; margin: 24px 0 16px; }}
.doc-body h2 {{ color: #93c5fd; font-size: 18px; margin: 20px 0 12px; }}
.doc-body h3 {{ color: #a5b4fc; font-size: 15px; margin: 16px 0 8px; }}
.doc-body table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 13px; }}
.doc-body th {{ background: #1e3a5f; color: #60a5fa; padding: 10px 12px; text-align: left; }}
.doc-body td {{ padding: 8px 12px; border-bottom: 1px solid #1f2937; }}
.doc-body tr:hover td {{ background: #1a2332; }}
.doc-body blockquote {{ border-left: 4px solid #3b82f6; padding: 12px 16px; background: #1a1f35; margin: 16px 0; color: #a5b4fc; }}
.doc-body code.inline {{ background: #1e293b; padding: 2px 8px; border-radius: 4px; color: #a5b4fc; }}
.doc-body pre {{ background: #1e293b; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 16px 0; }}
.doc-body pre code {{ color: #a5b4fc; font-size: 12px; }}
.doc-body ul {{ margin: 12px 0; padding-left: 24px; }}
.doc-body li {{ margin: 4px 0; }}
.doc-body hr {{ border: none; border-top: 1px solid #1f2937; margin: 20px 0; }}
.doc-body strong {{ color: #f1f5f9; }}
.loading {{ text-align: center; padding: 80px; display: none; }}
.loading .spinner {{ font-size: 40px; animation: spin 1s linear infinite; }}
@keyframes spin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
.alert {{ padding: 12px 16px; border-radius: 8px; margin: 12px 0; display: none; font-size: 13px; }}
.alert-error {{ background: rgba(239,68,68,0.1); border: 1px solid #ef4444; color: #fca5a5; }}
.alert-success {{ background: rgba(34,197,94,0.1); border: 1px solid #22c55e; color: #86efac; }}
.footer {{ text-align: center; padding: 14px; color: #475569; font-size: 11px; border-top: 1px solid #1f2937; }}
@media (max-width: 768px) {{ .main {{ flex-direction: column; }} .sidebar {{ width: 100%; }} }}
</style>
</head>
<body>
<div class="topbar">
    <div class="brand">
        <span class="logo">🛡️</span>
        <div>
            <div class="name">OTengine4 — T2 Tri-Core v2.1</div>
            <div class="sub">Autonomous Policy Generator | Neural Link</div>
        </div>
    </div>
    <div class="badge" id="syncBadge">Ready</div>
</div>

<div class="main">
    <div class="sidebar">
        <h3>📋 Client Information</h3>
        <div class="form-group">
            <label>Client / ชื่อองค์กร</label>
            <input type="text" id="clientName" placeholder="บริษัท พลังงานสะอาด จำกัด">
        </div>
        <div class="form-group">
            <label>Sector / ภาคส่วน</label>
            <select id="sector">
                <option value="พลังงาน">⚡ พลังงาน / ไฟฟ้า</option>
                <option value="น้ำประปา">💧 น้ำประปา / สุขาภิบาล</option>
                <option value="การผลิต">🏭 การผลิต</option>
                <option value="ขนส่ง">🚢 ขนส่ง / Maritime</option>
                <option value="น้ำมันและก๊าซ">⛽ น้ำมันและก๊าซ</option>
            </select>
        </div>

        <h3>📐 Policy Tier</h3>
        <div class="form-group">
            <select id="tier">
                <option value="B">🟢 Base — ฿95,000</option>
                <option value="S">🟡 Standard — ฿125,000</option>
                <option value="P" selected>🟠 Pro — ฿165,000</option>
                <option value="E">🔴 Enterprise — ฿395,000</option>
            </select>
        </div>

        <h3>📜 Regulations</h3>
        <div class="form-group">
            <div class="checkbox-item"><input type="checkbox" id="regTh" checked><span>พ.ร.บ.ไซเบอร์ ม.58/59 (TH)</span></div>
            <div class="checkbox-item"><input type="checkbox" id="regIec" checked><span>IEC 62443-2-1</span></div>
            <div class="checkbox-item"><input type="checkbox" id="regCip"><span>NERC CIP</span></div>
            <div class="checkbox-item"><input type="checkbox" id="regNis2"><span>NIS2 (EU)</span></div>
        </div>

        <h3>🔍 T1 Source</h3>
        <div class="form-group">
            <label>T1 JSON auto-detected</label>
            <input type="text" value="{Path(latest_t1).name if latest_t1 else 'Auto (none found)'}" readonly
                   style="opacity:0.7;cursor:not-allowed;">
        </div>

        <button class="btn btn-primary" id="genBtn" onclick="generate()">
            ⚡ Generate Autonomous Policy
        </button>

        <div class="loading" id="loading">
            <div class="spinner">⟳</div>
            <div style="margin-top:12px;color:#64748b;">กำลังสร้างนโยบาย...</div>
        </div>

        <div class="alert alert-error" id="errorAlert"></div>
    </div>

    <div class="content">
        <div class="status-bar" id="statusBar">
            <div class="status-card"><div class="label">Threat</div><div class="value" id="sThreat">—</div></div>
            <div class="status-card"><div class="label">Severity</div><div class="value" id="sSeverity">—</div></div>
            <div class="status-card"><div class="label">Tier</div><div class="value" id="sTier">—</div></div>
            <div class="status-card"><div class="label">Assets</div><div class="value" id="sAssets">—</div></div>
        </div>

        <div class="empty-state" id="emptyState">
            <div class="icon">📋</div>
            <h3>ยังไม่มีเอกสาร</h3>
            <p>กรอกข้อมูลด้านซ้าย แล้วกด <strong>Generate Autonomous Policy</strong></p>
        </div>

        <div class="doc-preview" id="docPreview">
            <div class="preview-header">
                <div class="preview-title">🛡️ นโยบายการรักษาความมั่นคงปลอดภัยไซเบอร์</div>
                <div class="doc-actions">
                    <button class="btn-sm" onclick="copyMd()">📋 Copy</button>
                    <button class="btn-sm" onclick="downloadMd()">📄 MD</button>
                    <button class="btn-sm" onclick="downloadHtml()">🌐 HTML</button>
                </div>
            </div>
            <div class="doc-body" id="docBody"></div>
        </div>
    </div>
</div>

<div class="footer">T2 Tri-Core v2.1 | OTengine4 | {datetime.now().strftime('%d/%m/%Y')}</div>

<script>
let currentMd = "";
let currentHtml = "";

async function generate() {{
    const btn = document.getElementById('genBtn');
    const loading = document.getElementById('loading');
    const empty = document.getElementById('emptyState');
    const preview = document.getElementById('docPreview');
    const error = document.getElementById('errorAlert');
    const statusBar = document.getElementById('statusBar');

    btn.disabled = true;
    loading.style.display = 'block';
    empty.style.display = 'none';
    preview.style.display = 'none';
    error.style.display = 'none';

    const client = document.getElementById('clientName').value;
    const sector = document.getElementById('sector').value;

    try {{
        const resp = await fetch('/api/generate', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ client, sector }})
        }});
        const data = await resp.json();

        if (data.success) {{
            currentMd = data.markdown;
            currentHtml = data.html;

            // Update status
            statusBar.style.display = 'flex';
            document.getElementById('sThreat').textContent = data.threat || '—';
            document.getElementById('sSeverity').textContent = data.severity || '—';
            document.getElementById('sTier').textContent = data.tier || '—';
            document.getElementById('sAssets').textContent = data.assetCount || '1';
            document.getElementById('syncBadge').textContent = data.syncId || 'Ready';

            document.getElementById('docBody').innerHTML = data.html;
            preview.style.display = 'block';
        }} else {{
            throw new Error(data.error || 'Generation failed');
        }}
    }} catch (e) {{
        error.textContent = '❌ ' + e.message;
        error.style.display = 'block';
        empty.style.display = 'block';
    }} finally {{
        btn.disabled = false;
        loading.style.display = 'none';
    }}
}}

function copyMd() {{
    navigator.clipboard.writeText(currentMd).then(() => alert('✅ Markdown คัดลอกแล้ว!'));
}}
function downloadMd() {{
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([currentMd], {{type:'text/markdown'}}));
    a.download = 'OT-Policy-Draft.md';
    a.click();
}}
function downloadHtml() {{
    const full = '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>OT Policy</title></head><body>' + currentHtml + '</body></html>';
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([full], {{type:'text/html'}}));
    a.download = 'OT-Policy-Draft.html';
    a.click();
}}
</script>
</body>
</html>"""

    def handle_generate(self):
        try:
            cl = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(cl).decode())
            client = body.get("client", "")
            sector = body.get("sector", "")

            t1_path = find_latest_t1_json()
            cmd = ["python3", str(INTEGRATOR.resolve())]
            if t1_path: cmd += ["--t1-json", t1_path]
            if client: cmd += ["--client", client]
            if sector: cmd += ["--sector", sector]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=str(T2_DIR))

            # Extract markdown output
            md_path = None
            for line in result.stdout.split("\n"):
                if "Markdown:" in line:
                    md_path = line.split("Markdown:")[-1].strip()
                    break

            # Always write output to a predictable path
            output_path = Path("/tmp") / f"t2_webapp_output_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
            if md_path and Path(md_path).exists():
                markdown = Path(md_path).read_text(encoding="utf-8")
            else:
                # Run again with explicit output
                out_cmd = ["python3", str(INTEGRATOR.resolve()),
                          "--client", client, "--sector", sector,
                          "--output", str(output_path)]
                if t1_path: out_cmd += ["--t1-json", t1_path]
                out_run = subprocess.run(out_cmd, capture_output=True, text=True, timeout=120)
                if output_path.exists():
                    markdown = output_path.read_text(encoding="utf-8")
                else:
                    markdown = result.stdout + "\n" + out_run.stdout + "\n" + out_run.stderr

            html_content = md_to_html(markdown)

            sync_id = re.search(r"Sync ID:\s*(SYNC-[^\s]+)", result.stdout)
            threat_m = re.search(r"Threat.*?\|\s*(.+?)\s*\|", result.stdout)
            tier_m = re.search(r"Tier:\s+(.+?)\s+\(", result.stdout)
            asset_m = re.search(r"Assets.*?\|\s*(\d+)", result.stdout)

            self.send_json({
                "success": True,
                "markdown": markdown,
                "html": html_content,
                "syncId": sync_id.group(1) if sync_id else "—",
                "threat": threat_m.group(1).strip() if threat_m else None,
                "severity": None,
                "tier": tier_m.group(1).strip() if tier_m else None,
                "assetCount": asset_m.group(1) if asset_m else "1"
            })
        except subprocess.TimeoutExpired:
            self.send_json({"success": False, "error": "Timeout"}, 500)
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)


def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  🛡️ OTengine4 T2 Dashboard — v2.1 Neural Link            ║
╠══════════════════════════════════════════════════════════════╣
║  URL:  http://localhost:{PORT}                             ║
║  T2:   {str(INTEGRATOR.name)}                              ║
║  Mode: Pure Python — No pip install needed!                ║
╠══════════════════════════════════════════════════════════════╣
║  Press Ctrl+C to stop                                      ║
╚══════════════════════════════════════════════════════════════╝
""")
    server.serve_forever()


if __name__ == "__main__":
    main()
