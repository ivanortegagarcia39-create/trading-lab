#!/usr/bin/env python3
"""
web-dashboard.py — Dashboard web del sistema TradingLab.

Uso:
    python scripts/web-dashboard.py
    python scripts/web-dashboard.py --port 8766

Puerto por defecto: 8766
"""

import argparse
import base64
import glob
import json
import os
import re
import struct
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT    = Path(__file__).parent.parent
RESULTS = ROOT / "results"
SQX_DIR = Path(r"D:\user\projects\Builder\databanks\Results")

# ── Decodificador SQStats (formato binario SQX) ────────────────────────────

def _parse_sqstats(data: bytes) -> dict:
    s = {}
    trades_set = False
    i = 0
    while i < len(data) - 5:
        t = data[i]
        if t == 0x03:
            fid = data[i + 1]
            val = struct.unpack(">f", data[i + 2:i + 6])[0]
            if ("F", fid) not in s:
                s[("F", fid)] = val
            i += 6
        elif t == 0x01:
            fid = data[i + 1]
            val = struct.unpack(">I", data[i + 2:i + 6])[0]
            if fid == 0x01 and not trades_set:
                s["trades"] = val
                trades_set = True
            i += 6
        else:
            i += 1
    return s


def _read_sqx_files() -> list[dict]:
    strategies = []
    if not SQX_DIR.exists():
        return strategies
    for f in sorted(SQX_DIR.glob("*.sqx")):
        try:
            with zipfile.ZipFile(f) as z:
                rx = next(n for n in z.namelist() if n.endswith("Results.xml"))
                xml = z.read(rx).decode(errors="ignore")
            m = re.search(
                r"<RobustnessOriginalResults>.*?<SQStats[^>]*>(.*?)</SQStats>",
                xml, re.DOTALL,
            )
            if not m:
                continue
            data = base64.b64decode(m.group(1).strip())
            s = _parse_sqstats(data)
            pf     = round(s.get(("F", 0x2E), 0.0), 2)
            dd     = round(s.get(("F", 0x5B), 0.0), 2)
            trades = s.get("trades", 0)
            wr     = round(s.get(("F", 0x34), 0.0), 1)
            netp   = round(s.get(("F", 0x31), 0.0), 0)
            strategies.append({
                "name":   f.stem,
                "pf":     pf,
                "dd":     dd,
                "trades": trades,
                "wr":     wr,
                "netp":   int(netp),
            })
        except Exception:
            pass
    return strategies


# ── Recolectores de datos ──────────────────────────────────────────────────

def _read_json(path: Path) -> dict | list:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _build_info() -> dict:
    lock = _read_json(RESULTS / "pipeline.lock")
    if not lock:
        return {"build": "—", "activo": "—", "spread": "—", "status": "—", "elapsed": "—"}
    elapsed = "—"
    started = lock.get("started", "")
    if started:
        try:
            dt = datetime.fromisoformat(started)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            delta = datetime.now(timezone.utc) - dt
            h, r = divmod(int(delta.total_seconds()), 3600)
            m = r // 60
            elapsed = f"{h}h {m}m"
        except Exception:
            pass
    return {
        "build":   lock.get("build", "—"),
        "activo":  lock.get("activo", "—"),
        "spread":  lock.get("spread_real", "—"),
        "status":  lock.get("status", "—"),
        "elapsed": elapsed,
    }


def _queue_info() -> list[dict]:
    queue = _read_json(RESULTS / "build-queue.json")
    if not isinstance(queue, list):
        return []
    items = []
    for item in queue[:6]:
        items.append({
            "activo": item.get("activo", "—"),
            "score":  item.get("score", "—"),
            "estado": item.get("estado", "—"),
            "build":  item.get("build", "—"),
        })
    return items


def _services_status() -> dict:
    services = {}

    # API TradingLab
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:8765/health", timeout=3) as r:
            services["api"] = "OK" if r.status == 200 else f"HTTP {r.status}"
    except Exception as e:
        services["api"] = f"DOWN"

    # N8N
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:5678", timeout=3) as r:
            services["n8n"] = "OK"
    except Exception:
        services["n8n"] = "DOWN"

    # StrategyQuantX
    try:
        r = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq StrategyQuantX.exe"],
            capture_output=True, text=True, timeout=5,
        )
        services["sq"] = "corriendo" if "StrategyQuantX.exe" in r.stdout else "parado"
    except Exception:
        services["sq"] = "—"

    return services


def _notifications() -> list[dict]:
    items = []
    log_path = RESULTS / "session-log.json"
    if log_path.exists():
        try:
            data = json.loads(log_path.read_text(encoding="utf-8"))
            entries = data if isinstance(data, list) else []
            for entry in reversed(entries[-10:]):
                items.append({
                    "ts":      entry.get("timestamp", entry.get("date", ""))[:16],
                    "type":    entry.get("type", "—"),
                    "device":  entry.get("device", ""),
                    "health":  entry.get("health", ""),
                })
        except Exception:
            pass

    health = _read_json(RESULTS / "system-health.json")
    alerts = []
    if isinstance(health, dict):
        for chk in health.get("checks", []):
            if chk.get("status") in ("FAIL", "WARN"):
                alerts.append({"status": chk["status"], "check": chk.get("check", "").strip(), "detail": chk.get("detail", "")})
    return {"log": items, "alerts": alerts[:8]}


def _collect_all() -> dict:
    return {
        "ts":           datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "build":        _build_info(),
        "queue":        _queue_info(),
        "strategies":   _read_sqx_files(),
        "services":     _services_status(),
        "notifications": _notifications(),
    }


# ── HTML ───────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="theme-color" content="#00bcd4">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="TradingLab">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/icon-192.png">
<title>TradingLab Dashboard</title>
<style>
  :root {
    --bg: #0d0d0d; --card: #161616; --border: #2a2a2a;
    --txt: #e0e0e0; --dim: #888; --green: #4caf50;
    --yellow: #ffc107; --red: #f44336; --blue: #2196f3;
    --accent: #00bcd4;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--txt); font-family: 'Consolas','Courier New',monospace; font-size: 13px; padding: 16px; }
  h1 { color: var(--accent); font-size: 16px; margin-bottom: 4px; }
  .ts { color: var(--dim); font-size: 11px; margin-bottom: 16px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 12px; }
  .card h2 { font-size: 12px; color: var(--accent); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; border-bottom: 1px solid var(--border); padding-bottom: 6px; }
  .row { display: flex; justify-content: space-between; padding: 3px 0; border-bottom: 1px solid #1a1a1a; }
  .row:last-child { border-bottom: none; }
  .label { color: var(--dim); }
  .val { font-weight: bold; }
  .ok { color: var(--green); }
  .warn { color: var(--yellow); }
  .fail { color: var(--red); }
  .info { color: var(--blue); }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  th { color: var(--dim); text-align: right; padding: 4px 6px; font-weight: normal; border-bottom: 1px solid var(--border); }
  th:first-child { text-align: left; }
  td { padding: 3px 6px; text-align: right; border-bottom: 1px solid #1a1a1a; }
  td:first-child { text-align: left; color: var(--dim); max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  tr:hover td { background: #1e1e1e; }
  .pf-good { color: var(--green); }
  .pf-ok   { color: var(--yellow); }
  .pf-bad  { color: var(--red); }
  .badge { display: inline-block; padding: 1px 6px; border-radius: 3px; font-size: 11px; font-weight: bold; }
  .badge-green  { background: #1b3a1b; color: var(--green); }
  .badge-yellow { background: #3a2d00; color: var(--yellow); }
  .badge-red    { background: #3a1010; color: var(--red); }
  .badge-grey   { background: #222; color: var(--dim); }
  .alert-item { padding: 4px 0; color: var(--yellow); font-size: 12px; }
  .alert-item.fail { color: var(--red); }
  .full-width { grid-column: 1 / -1; }
  .spinner { display: inline-block; width: 8px; height: 8px; border: 2px solid var(--dim); border-top-color: var(--accent); border-radius: 50%; animation: spin 1s linear infinite; margin-left: 8px; }
  @keyframes spin { to { transform: rotate(360deg); } }
  #refresh-bar { height: 2px; background: var(--border); margin-bottom: 12px; }
  #refresh-progress { height: 100%; background: var(--accent); transition: width 1s linear; }
  .summary-row { display: flex; gap: 16px; margin-bottom: 12px; }
  .summary-box { background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 10px 16px; flex: 1; text-align: center; }
  .summary-box .big { font-size: 22px; font-weight: bold; color: var(--accent); }
  .summary-box .small { font-size: 11px; color: var(--dim); margin-top: 2px; }
</style>
</head>
<body>
<h1>TRADINGLAB — Dashboard v8.1 <span class="spinner" id="spin" style="display:none"></span></h1>
<div class="ts" id="ts">Cargando...</div>
<div id="refresh-bar"><div id="refresh-progress" style="width:100%"></div></div>

<div id="app">
  <div class="ts" style="margin-top:40px;text-align:center">Cargando datos...</div>
</div>

<script>
const INTERVAL = 60;
let countdown = INTERVAL;
let timer;

function pfClass(pf) {
  if (pf >= 2.0) return 'pf-good';
  if (pf >= 1.3) return 'pf-ok';
  return 'pf-bad';
}

function badge(text) {
  const t = (text || '').toLowerCase();
  if (t === 'ok' || t === 'corriendo' || t === 'running') return `<span class="badge badge-green">${text}</span>`;
  if (t === 'down' || t === 'parado' || t === 'fail') return `<span class="badge badge-red">${text}</span>`;
  if (t === 'warn') return `<span class="badge badge-yellow">${text}</span>`;
  return `<span class="badge badge-grey">${text}</span>`;
}

function statusBadge(s) {
  const t = (s || '').toUpperCase();
  if (t === 'EN_CURSO' || t === 'RUNNING') return `<span class="badge badge-green">${s}</span>`;
  if (t === 'PENDIENTE') return `<span class="badge badge-grey">${s}</span>`;
  return `<span class="badge badge-grey">${s}</span>`;
}

function render(d) {
  const b = d.build;
  const svc = d.services;
  const strats = d.strategies || [];
  const queue = d.queue || [];
  const notif = d.notifications || {};
  const alerts = notif.alerts || [];
  const log = notif.log || [];

  // Summary boxes
  const goodStrats = strats.filter(s => s.pf >= 1.3).length;
  const summaryHTML = `
    <div class="summary-row">
      <div class="summary-box"><div class="big">${b.build !== '—' ? '#' + b.build : '—'}</div><div class="small">Build activo</div></div>
      <div class="summary-box"><div class="big" style="color:${b.status==='running'?'#4caf50':'#888'}">${b.activo}</div><div class="small">${b.elapsed} corriendo</div></div>
      <div class="summary-box"><div class="big">${strats.length}</div><div class="small">Estrategias en Results</div></div>
      <div class="summary-box"><div class="big" style="color:#4caf50">${goodStrats}</div><div class="small">PF ≥ 1.3</div></div>
      <div class="summary-box"><div class="big" style="color:${alerts.length>0?'#ffc107':'#4caf50'}">${alerts.length}</div><div class="small">Alertas activas</div></div>
    </div>`;

  // Build + servicios
  const buildHTML = `
    <div class="card">
      <h2>Build Activo</h2>
      <div class="row"><span class="label">Build</span><span class="val">${b.build}</span></div>
      <div class="row"><span class="label">Activo</span><span class="val">${b.activo}</span></div>
      <div class="row"><span class="label">Spread</span><span class="val">${b.spread} pips</span></div>
      <div class="row"><span class="label">Estado</span><span class="val">${badge(b.status)}</span></div>
      <div class="row"><span class="label">Tiempo corriendo</span><span class="val">${b.elapsed}</span></div>
    </div>`;

  // Cola
  const queueRows = queue.map(q => `
    <div class="row">
      <span class="label">${q.activo}</span>
      <span class="val">${statusBadge(q.estado)} ${q.score !== null && q.score !== '—' ? `<span style="color:var(--dim);font-size:11px">score ${q.score}</span>` : ''}</span>
    </div>`).join('');
  const queueHTML = `
    <div class="card">
      <h2>Cola de Builds</h2>
      ${queueRows || '<div class="row"><span class="label">Cola vacía</span></div>'}
    </div>`;

  // Servicios
  const svcHTML = `
    <div class="card">
      <h2>Servicios</h2>
      <div class="row"><span class="label">API TradingLab :8765</span><span class="val">${badge(svc.api)}</span></div>
      <div class="row"><span class="label">N8N :5678</span><span class="val">${badge(svc.n8n)}</span></div>
      <div class="row"><span class="label">StrategyQuantX</span><span class="val">${badge(svc.sq)}</span></div>
    </div>`;

  // Alertas
  const alertRows = alerts.length
    ? alerts.map(a => `<div class="alert-item ${a.status==='FAIL'?'fail':''}">[${a.status}] ${a.check}${a.detail?' — '+a.detail:''}</div>`).join('')
    : '<div style="color:var(--green);padding:4px 0">Sin alertas activas</div>';
  const alertHTML = `
    <div class="card">
      <h2>Alertas del Sistema</h2>
      ${alertRows}
    </div>`;

  // Estrategias
  const stratRows = strats.map(s => {
    const cls = pfClass(s.pf);
    const ddCls = s.dd > 15 ? 'pf-bad' : s.dd > 10 ? 'pf-ok' : 'pf-good';
    return `<tr>
      <td title="${s.name}">${s.name}</td>
      <td class="${cls}">${s.pf.toFixed(2)}</td>
      <td class="${ddCls}">${s.dd.toFixed(2)}%</td>
      <td>${s.trades}</td>
      <td>${s.wr.toFixed(1)}%</td>
      <td style="color:${s.netp>=0?'#4caf50':'#f44336'}">${s.netp >= 0 ? '+' : ''}${s.netp}</td>
    </tr>`;
  }).join('');
  const stratHTML = `
    <div class="card full-width">
      <h2>Estrategias en Results (${strats.length})</h2>
      <table>
        <thead><tr><th>Nombre</th><th>PF</th><th>DD%</th><th>Trades</th><th>WR%</th><th>NetP</th></tr></thead>
        <tbody>${stratRows || '<tr><td colspan="6" style="text-align:center;color:var(--dim)">Sin estrategias</td></tr>'}</tbody>
      </table>
    </div>`;

  // Notificaciones
  const logRows = log.slice(0, 8).map(e => `
    <div class="row">
      <span class="label" style="font-size:11px">${e.ts}</span>
      <span class="val" style="font-size:11px">[${e.type}] ${e.device} ${e.health ? '— '+e.health : ''}</span>
    </div>`).join('');
  const logHTML = `
    <div class="card full-width">
      <h2>Últimas Notificaciones</h2>
      ${logRows || '<div style="color:var(--dim);padding:4px 0">Sin registros</div>'}
    </div>`;

  document.getElementById('app').innerHTML = `
    ${summaryHTML}
    <div class="grid">
      ${buildHTML}
      ${queueHTML}
      ${svcHTML}
      ${alertHTML}
      ${stratHTML}
      ${logHTML}
    </div>`;

  document.getElementById('ts').textContent = 'Última actualización: ' + d.ts;
}

function startProgress() {
  countdown = INTERVAL;
  const bar = document.getElementById('refresh-progress');
  bar.style.transition = 'none';
  bar.style.width = '100%';
  requestAnimationFrame(() => {
    bar.style.transition = `width ${INTERVAL}s linear`;
    bar.style.width = '0%';
  });
}

async function refresh() {
  document.getElementById('spin').style.display = 'inline-block';
  try {
    const r = await fetch('/api/data');
    const d = await r.json();
    render(d);
    startProgress();
  } catch(e) {
    document.getElementById('ts').textContent = 'Error al cargar datos: ' + e.message;
  } finally {
    document.getElementById('spin').style.display = 'none';
  }
}

refresh();
setInterval(refresh, INTERVAL * 1000);

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(() => {});
}
</script>
</body>
</html>"""


# ── PWA assets ────────────────────────────────────────────────────────────

MANIFEST_JSON = json.dumps({
    "name": "TradingLab",
    "short_name": "TradingLab",
    "description": "Dashboard del sistema TradingLab de trading algorítmico",
    "display": "standalone",
    "orientation": "portrait",
    "theme_color": "#00bcd4",
    "background_color": "#0d0d0d",
    "start_url": "/",
    "scope": "/",
    "icons": [
        {"src": "/icon-192.png", "sizes": "192x192", "type": "image/svg+xml", "purpose": "any maskable"},
    ],
}, ensure_ascii=False, indent=2)

SW_JS = """\
const CACHE = 'tradinglab-v1';
const SHELL = ['/'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.pathname === '/api/data') return;  // siempre en red
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
"""

ICON_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192">
  <rect width="192" height="192" rx="28" fill="#0d0d0d"/>
  <rect x="4" y="4" width="184" height="184" rx="24" fill="none" stroke="#00bcd4" stroke-width="6"/>
  <text x="96" y="128" font-family="Consolas,monospace" font-size="88" font-weight="bold"
        fill="#00bcd4" text-anchor="middle">TL</text>
</svg>"""


# ── Servidor HTTP ──────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silenciar logs de acceso

    def _send(self, code: int, ctype: str, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/data":
            try:
                data = _collect_all()
                body = json.dumps(data, ensure_ascii=False).encode("utf-8")
                self._send(200, "application/json; charset=utf-8", body)
            except Exception as e:
                body = json.dumps({"error": str(e)}).encode("utf-8")
                self._send(500, "application/json", body)
        elif self.path in ("/", "/index.html"):
            self._send(200, "text/html; charset=utf-8", HTML.encode("utf-8"))
        elif self.path == "/manifest.json":
            self._send(200, "application/manifest+json; charset=utf-8", MANIFEST_JSON.encode("utf-8"))
        elif self.path == "/sw.js":
            self._send(200, "application/javascript; charset=utf-8", SW_JS.encode("utf-8"))
        elif self.path == "/icon-192.png":
            self._send(200, "image/svg+xml; charset=utf-8", ICON_SVG.encode("utf-8"))
        else:
            self._send(404, "text/plain", b"Not found")


def main() -> int:
    parser = argparse.ArgumentParser(description="Web Dashboard — TradingLab")
    parser.add_argument("--port", type=int, default=8766, help="Puerto (default: 8766)")
    args = parser.parse_args()

    server = HTTPServer(("0.0.0.0", args.port), Handler)
    print(f"Dashboard iniciado en http://localhost:{args.port}")
    print("Ctrl+C para detener.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard detenido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
