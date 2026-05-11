#!/usr/bin/env python3
"""
File Renamer — Web GUI
Opens automatically in your browser. No extra libraries needed.
Run: python3 file_renamer.py
"""

import json
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

# ─────────────────────────────────────────────
#  Rename Logic
# ─────────────────────────────────────────────

def build_new_name(original: Path, fmt_type: str, options: dict, index: int) -> str:
    stem = original.stem
    ext  = original.suffix

    if fmt_type == "datetime":
        date_fmt  = options.get("date_fmt", "%Y-%m-%d")
        position  = options.get("position", "prefix")
        separator = options.get("separator", "_")
        try:
            timestamp = datetime.now().strftime(date_fmt)
        except Exception:
            timestamp = datetime.now().strftime("%Y-%m-%d")
        new_stem = f"{timestamp}{separator}{stem}" if position == "prefix" else f"{stem}{separator}{timestamp}"

    elif fmt_type == "sequential":
        padding   = int(options.get("padding", 3))
        start     = int(options.get("start", 1))
        position  = options.get("position", "prefix")
        separator = options.get("separator", "_")
        number    = str(index + start).zfill(padding)
        new_stem  = f"{number}{separator}{stem}" if position == "prefix" else f"{stem}{separator}{number}"

    elif fmt_type == "custom":
        pattern = options.get("pattern", "{name}")
        ts      = datetime.now()
        number  = str(index + int(options.get("start", 1))).zfill(int(options.get("padding", 3)))
        new_stem = (
            pattern
            .replace("{name}",  stem)
            .replace("{date}",  ts.strftime("%Y-%m-%d"))
            .replace("{time}",  ts.strftime("%H-%M-%S"))
            .replace("{num}",   number)
            .replace("{UPPER}", stem.upper())
            .replace("{lower}", stem.lower())
        )
    else:
        new_stem = stem

    return new_stem + ext


# ─────────────────────────────────────────────
#  HTML UI
# ─────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>✦ File Renamer</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');
  :root{
    --bg:#0d0f1a; --surface:#151827; --card:#1c2035; --border:#272b45;
    --accent:#7c6dfa; --accent2:#fa6d8f; --success:#3ddc84; --warn:#f7a030;
    --danger:#f74040; --text:#dde0f5; --muted:#636690;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--text);font-family:'Space Grotesk',sans-serif;min-height:100vh;padding:24px 28px;}
  h1{font-size:1.7rem;font-weight:700;color:var(--accent);letter-spacing:-0.5px}
  h1 span{color:var(--muted);font-size:.95rem;font-weight:400;margin-left:10px}
  .grid{display:grid;grid-template-columns:340px 1fr;gap:18px;margin-top:20px}
  .card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px}
  .card+.card{margin-top:14px}
  .card-title{font-size:.8rem;font-weight:700;letter-spacing:.08em;color:var(--accent);text-transform:uppercase;margin-bottom:14px}
  label{font-size:.85rem;color:var(--muted);display:block;margin-bottom:4px}
  input[type=text],input[type=number]{
    width:100%;background:var(--surface);border:1px solid var(--border);border-radius:7px;
    color:var(--text);font-family:'JetBrains Mono',monospace;font-size:.85rem;
    padding:8px 10px;outline:none;transition:border .2s
  }
  input:focus{border-color:var(--accent)}
  .row{display:flex;gap:10px;align-items:center;margin-bottom:10px}
  .row label{min-width:100px;margin:0;white-space:nowrap}
  .row input{flex:1}
  .radio-group{display:flex;gap:14px;flex-wrap:wrap}
  .radio-group label{display:flex;align-items:center;gap:6px;cursor:pointer;color:var(--text);font-size:.9rem;margin:0}
  .mode-btn{
    display:flex;align-items:center;gap:8px;padding:10px 14px;border-radius:9px;
    background:var(--surface);border:1px solid var(--border);cursor:pointer;
    font-family:inherit;font-size:.9rem;color:var(--text);transition:all .18s;width:100%;margin-bottom:8px
  }
  .mode-btn.active{border-color:var(--accent);background:#1e1a3a;color:var(--accent)}
  .mode-btn:hover{border-color:var(--muted)}
  .btn{padding:9px 18px;border-radius:8px;border:none;cursor:pointer;font-family:inherit;font-size:.88rem;font-weight:600;transition:opacity .15s}
  .btn:hover{opacity:.85}
  .btn-muted{background:var(--border);color:var(--text)}
  .btn-success{background:var(--success);color:#0d1a11}
  .btn-danger{background:var(--danger);color:#fff;padding:6px 12px;font-size:.8rem}
  .btn-row{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}
  #drop-zone{
    border:2px dashed var(--border);border-radius:10px;padding:22px;text-align:center;
    color:var(--muted);font-size:.9rem;cursor:pointer;transition:border .2s;margin-bottom:10px
  }
  #drop-zone.drag{border-color:var(--accent);background:#1a1a35}
  #drop-zone:hover{border-color:var(--muted)}
  #file-input{display:none}
  #file-list{max-height:160px;overflow-y:auto;font-family:'JetBrains Mono',monospace;font-size:.8rem}
  .file-item{display:flex;justify-content:space-between;align-items:center;padding:5px 8px;border-radius:6px;border-bottom:1px solid var(--border)}
  .file-item:hover{background:var(--surface)}
  .file-name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:240px}
  .file-remove{color:var(--danger);cursor:pointer;font-size:1rem;padding:0 4px;flex-shrink:0}
  #count{font-size:.8rem;color:var(--muted);margin-top:6px}
  .preview-header{display:grid;grid-template-columns:1fr 24px 1fr;gap:8px;font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;padding:0 10px;margin-bottom:6px}
  #preview-list{max-height:400px;overflow-y:auto}
  .preview-row{display:grid;grid-template-columns:1fr 24px 1fr;gap:8px;align-items:center;padding:7px 10px;border-radius:7px;font-family:'JetBrains Mono',monospace;font-size:.8rem}
  .preview-row:nth-child(odd){background:var(--surface)}
  .preview-arrow{color:var(--accent);text-align:center}
  .preview-new{color:var(--success);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .preview-err{color:var(--danger)}
  .preview-orig{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  #status{margin-top:12px;font-size:.85rem;color:var(--muted);min-height:20px}
  .tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.75rem;font-family:'JetBrains Mono',monospace;background:var(--surface);color:var(--accent2);border:1px solid var(--border);margin:2px;cursor:pointer}
  .tag:hover{border-color:var(--accent2)}
  .legend{margin-top:10px;display:flex;flex-wrap:wrap;gap:4px}
  .hint{font-size:.78rem;color:var(--muted);margin-top:4px}
  .section-sep{height:1px;background:var(--border);margin:14px 0}
  .folder-row{margin-bottom:12px}
  .folder-row label{color:var(--muted);font-size:.82rem;margin-bottom:4px}
  .folder-row input{width:100%;background:var(--surface);border:1px solid var(--border);border-radius:7px;color:var(--text);font-family:'JetBrains Mono',monospace;font-size:.82rem;padding:7px 10px;outline:none;}
  .folder-row input:focus{border-color:var(--accent)}
</style>
</head>
<body>

<h1>✦ File Renamer <span>batch · smart · flexible</span></h1>

<div class="grid">

<!-- LEFT PANEL -->
<div>
  <div class="card">
    <div class="card-title">① Select Files</div>
    <div class="folder-row">
      <label>Folder path (where your files live)</label>
      <input type="text" id="folder-path" placeholder="/Users/you/Documents/photos" oninput="refreshPreview()"/>
    </div>
    <div id="drop-zone" onclick="document.getElementById('file-input').click()">
      Click to pick files — or drag &amp; drop
    </div>
    <input type="file" id="file-input" multiple onchange="addFiles(this.files)"/>
    <div class="btn-row">
      <button class="btn btn-danger" onclick="clearFiles()">✕ Clear All</button>
    </div>
    <div id="file-list"></div>
    <div id="count">No files selected</div>
  </div>

  <div class="card" style="margin-top:14px">
    <div class="card-title">② Choose Format</div>
    <button class="mode-btn active" id="btn-datetime"   onclick="setMode('datetime')">📅  Date / Time</button>
    <button class="mode-btn"        id="btn-sequential" onclick="setMode('sequential')">🔢  Sequential Number</button>
    <button class="mode-btn"        id="btn-custom"     onclick="setMode('custom')">✏️  Custom Pattern</button>
  </div>

  <div class="card" style="margin-top:14px">
    <div class="card-title" id="options-title">Date / Time Options</div>
    <div id="options-body"></div>
  </div>
</div>

<!-- RIGHT PANEL -->
<div class="card" style="display:flex;flex-direction:column">
  <div class="card-title">③ Preview &amp; Rename</div>
  <div class="preview-header"><span>ORIGINAL</span><span></span><span>RENAMED</span></div>
  <div id="preview-list"></div>
  <div id="status">Add files and configure options to see a preview.</div>
  <div style="margin-top:auto;padding-top:16px;display:flex;gap:10px;flex-wrap:wrap">
    <button class="btn btn-muted"    onclick="refreshPreview()">🔍 Refresh Preview</button>
    <button class="btn btn-success"  onclick="doRename()">▶ Rename Files</button>
  </div>
</div>

</div>

<script>
let files = [];
let mode  = 'datetime';

// ── File Handling ──────────────────
function addFiles(fileList){
  for(const f of fileList){
    if(!files.find(x=>x.name===f.name)) files.push({name:f.name});
  }
  renderFileList(); refreshPreview();
}
function removeFile(i){ files.splice(i,1); renderFileList(); refreshPreview(); }
function clearFiles(){ files=[]; renderFileList(); refreshPreview(); }
function renderFileList(){
  document.getElementById('file-list').innerHTML = files.map((f,i)=>`
    <div class="file-item">
      <span class="file-name" title="${f.name}">${f.name}</span>
      <span class="file-remove" onclick="removeFile(${i})">✕</span>
    </div>`).join('');
  document.getElementById('count').textContent =
    files.length ? `${files.length} file${files.length!==1?'s':''} selected` : 'No files selected';
}

// ── Drop Zone ──────────────────────
const dz=document.getElementById('drop-zone');
dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('drag')});
dz.addEventListener('dragleave',()=>dz.classList.remove('drag'));
dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('drag');addFiles(e.dataTransfer.files);});

// ── Mode Switching ─────────────────
const OPTIONS = {
  datetime:`
    <div class="row"><label>Date Format</label><input type="text" id="dt_fmt" value="%Y-%m-%d" oninput="refreshPreview()"/></div>
    <div class="hint">%Y=2026 &nbsp;%m=05 &nbsp;%d=11 &nbsp;%b=May &nbsp;%H%M=1430</div>
    <div class="section-sep"></div>
    <div class="row"><label>Separator</label><input type="text" id="dt_sep" value="_" style="max-width:70px" oninput="refreshPreview()"/></div>
    <div class="row"><label>Position</label>
      <div class="radio-group">
        <label><input type="radio" name="dt_pos" value="prefix" checked onchange="refreshPreview()"/> Prefix</label>
        <label><input type="radio" name="dt_pos" value="suffix"        onchange="refreshPreview()"/> Suffix</label>
      </div>
    </div>`,
  sequential:`
    <div class="row"><label>Start Number</label><input type="number" id="sq_start" value="1" min="0" oninput="refreshPreview()"/></div>
    <div class="row"><label>Pad Width</label><input type="number" id="sq_pad" value="3" min="1" max="10" oninput="refreshPreview()"/></div>
    <div class="hint">Pad 3 → 001, 002, 003 …</div>
    <div class="section-sep"></div>
    <div class="row"><label>Separator</label><input type="text" id="sq_sep" value="_" style="max-width:70px" oninput="refreshPreview()"/></div>
    <div class="row"><label>Position</label>
      <div class="radio-group">
        <label><input type="radio" name="sq_pos" value="prefix" checked onchange="refreshPreview()"/> Prefix</label>
        <label><input type="radio" name="sq_pos" value="suffix"        onchange="refreshPreview()"/> Suffix</label>
      </div>
    </div>`,
  custom:`
    <div class="row"><label>Pattern</label><input type="text" id="cu_pat" value="{date}_{name}" oninput="refreshPreview()"/></div>
    <div class="legend">
      <span class="tag" onclick="insertTag('{name}')">{name}</span>
      <span class="tag" onclick="insertTag('{date}')">{date}</span>
      <span class="tag" onclick="insertTag('{time}')">{time}</span>
      <span class="tag" onclick="insertTag('{num}')">{num}</span>
      <span class="tag" onclick="insertTag('{UPPER}')">{UPPER}</span>
      <span class="tag" onclick="insertTag('{lower}')">{lower}</span>
    </div>
    <div class="hint" style="margin-top:6px">Click a tag to insert it into the pattern</div>
    <div class="section-sep"></div>
    <div class="row"><label>Start #</label><input type="number" id="cu_start" value="1" min="0" oninput="refreshPreview()"/></div>
    <div class="row"><label>Pad Width</label><input type="number" id="cu_pad" value="3" min="1" oninput="refreshPreview()"/></div>`
};
const TITLES={datetime:'Date / Time Options',sequential:'Sequential Options',custom:'Custom Pattern'};

function setMode(m){
  mode=m;
  ['datetime','sequential','custom'].forEach(k=>document.getElementById('btn-'+k).classList.toggle('active',k===m));
  document.getElementById('options-title').textContent=TITLES[m];
  document.getElementById('options-body').innerHTML=OPTIONS[m];
  refreshPreview();
}
setMode('datetime');

function insertTag(tag){
  const el=document.getElementById('cu_pat');
  if(!el) return;
  const p=el.selectionStart;
  el.value=el.value.slice(0,p)+tag+el.value.slice(el.selectionEnd);
  el.focus(); el.selectionStart=el.selectionEnd=p+tag.length;
  refreshPreview();
}

// ── Options Getters ────────────────
function getOptions(){
  if(mode==='datetime') return{
    date_fmt:document.getElementById('dt_fmt')?.value||'%Y-%m-%d',
    separator:document.getElementById('dt_sep')?.value||'_',
    position:document.querySelector('input[name=dt_pos]:checked')?.value||'prefix'
  };
  if(mode==='sequential') return{
    start:parseInt(document.getElementById('sq_start')?.value||1),
    padding:parseInt(document.getElementById('sq_pad')?.value||3),
    separator:document.getElementById('sq_sep')?.value||'_',
    position:document.querySelector('input[name=sq_pos]:checked')?.value||'prefix'
  };
  if(mode==='custom') return{
    pattern:document.getElementById('cu_pat')?.value||'{name}',
    start:parseInt(document.getElementById('cu_start')?.value||1),
    padding:parseInt(document.getElementById('cu_pad')?.value||3)
  };
  return{};
}

// ── Preview ────────────────────────
async function refreshPreview(){
  const el=document.getElementById('preview-list');
  const st=document.getElementById('status');
  if(!files.length){el.innerHTML='';st.textContent='No files selected.';st.style.color='var(--muted)';return;}
  const payload={files:files.map(f=>f.name),fmt_type:mode,options:getOptions()};
  try{
    const r=await fetch('/preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const data=await r.json();
    el.innerHTML=data.map(row=>`
      <div class="preview-row">
        <span class="preview-orig" title="${row.original}">${row.original}</span>
        <span class="preview-arrow">→</span>
        <span class="${row.ok?'preview-new':'preview-err'}" title="${row.new}">${row.new}</span>
      </div>`).join('');
    const ok=data.filter(r=>r.ok).length;
    st.textContent=`Preview: ${ok}/${data.length} files ready.`;
    st.style.color='var(--success)';
  }catch(e){st.textContent='Preview error: '+e.message;st.style.color='var(--danger)';}
}

// ── Rename ─────────────────────────
async function doRename(){
  if(!files.length){alert('Please add files first.');return;}
  const folder=document.getElementById('folder-path').value.trim();
  if(!folder){alert('Please enter the folder path where your files are located.');document.getElementById('folder-path').focus();return;}
  if(!confirm(`Rename ${files.length} file(s) in:\n${folder}\n\nThis cannot be undone.`)) return;
  const payload={files:files.map(f=>f.name),fmt_type:mode,options:getOptions(),folder};
  try{
    const r=await fetch('/rename',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const data=await r.json();
    const ok=data.filter(r=>r.ok).length;
    const fail=data.length-ok;
    files=data.filter(r=>r.ok).map(r=>({name:r.new}));
    renderFileList();
    document.getElementById('preview-list').innerHTML=data.map(row=>`
      <div class="preview-row">
        <span class="preview-orig">${row.original}</span>
        <span class="preview-arrow">${row.ok?'✓':'✗'}</span>
        <span class="${row.ok?'preview-new':'preview-err'}">${row.ok?row.new:row.error}</span>
      </div>`).join('');
    const st=document.getElementById('status');
    st.textContent=`Done! ${ok} renamed${fail?', '+fail+' failed':''}.`;
    st.style.color=fail?'var(--warn)':'var(--success)';
    alert(`✓ ${ok} file(s) renamed successfully.${fail?'\n✗ '+fail+' failed.':''}`);
  }catch(e){alert('Error: '+e.message);}
}
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
#  HTTP Server
# ─────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass  # suppress access logs

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = json.loads(self.rfile.read(length))
        result = self._handle_preview(body) if self.path == "/preview" else self._handle_rename(body)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def _handle_preview(self, body):
        out = []
        for i, name in enumerate(body.get("files", [])):
            try:
                new = build_new_name(Path(name), body.get("fmt_type","datetime"), body.get("options",{}), i)
                out.append({"original": name, "new": new, "ok": True})
            except Exception as e:
                out.append({"original": name, "new": str(e), "ok": False})
        return out

    def _handle_rename(self, body):
        out    = []
        base   = Path(body.get("folder", "").strip())
        ftype  = body.get("fmt_type", "datetime")
        opts   = body.get("options", {})
        if not base.exists():
            return [{"original": f, "new": "", "ok": False, "error": "Folder not found"} for f in body.get("files",[])]
        for i, name in enumerate(body.get("files", [])):
            fp = base / name
            try:
                if not fp.exists():
                    raise FileNotFoundError(f"Not found: {name}")
                new_name = build_new_name(fp, ftype, opts, i)
                fp.rename(base / new_name)
                out.append({"original": name, "new": new_name, "ok": True})
            except Exception as e:
                out.append({"original": name, "new": "", "ok": False, "error": str(e)})
        return out


# ─────────────────────────────────────────────
#  Entry Point
# ─────────────────────────────────────────────

PORT = 7474

def open_browser():
    import time; time.sleep(0.7)
    webbrowser.open(f"http://localhost:{PORT}")

if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Handler)
    print(f"\n  ✦ File Renamer is running!")
    print(f"  → Open in browser: http://localhost:{PORT}")
    print(f"  → Press Ctrl+C to stop\n")
    threading.Thread(target=open_browser, daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped. Goodbye!")