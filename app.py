import base64
import json
import os
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# ─────────────────────────────────────────────
# 工具函式
# ─────────────────────────────────────────────
def img_to_base64(path):
    """將圖片轉為 base64 data URI，找不到時回傳空字串"""
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        ext = path.rsplit(".", 1)[-1].lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
        return f"data:{mime};base64,{data}"
    return ""

# ─────────────────────────────────────────────
# 設定
# ─────────────────────────────────────────────
DATA_DIR = "DATA"

PRIZES = [
    {"score": 5000,  "name": "EVALUE 5000元點數",                          "emoji": "⚡"},
    {"score": 2500,  "name": "2026 2天免費充電方案",                        "emoji": "🎁"},
    {"score": 2000,  "name": "EVALUE 500點",                               "emoji": "🔌"},
    {"score": 1500,  "name": "2026 1天免費充電方案 (隨插即充)",              "emoji": "🎫"},
    {"score": 1000,  "name": "DC 快充 50% 回饋卷 x 3  (7/1-8/31 最高消費)","emoji": "🎁"},
    {"score": 750,   "name": "EVALUE 500點",                               "emoji": "🎫"},
    {"score": 500,   "name": "DC 快充 50% 回饋卷 x 2  (7/1-8/31 最高消費)","emoji": "🎟️"},
    {"score": 300,   "name": "EVALUE 100點",                               "emoji": "⭐"},
]

MAX_SCORE = PRIZES[0]["score"]  # 5000

# ─────────────────────────────────────────────
# 讀取資料
# ─────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_data():
    files = {
        "Degree":  ("Phone", "TotalScore"),
        "Car":     ("Phone", "CarTotalScore"),
        "Station": ("Phone", "StationScore"),
        "Count":   ("Phone", "CountScore"),
        "Save":    ("Phone", "SaveScore"),
        "Special": ("Phone", "SpecialScore"),
    }
    dfs = {}
    for name, (phone_col, score_col) in files.items():
        path = os.path.join(DATA_DIR, f"{name}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path, dtype={phone_col: str})
            df[phone_col] = df[phone_col].str.strip()
            dfs[name] = df.rename(columns={phone_col: "Phone", score_col: "Score"})
        else:
            dfs[name] = pd.DataFrame(columns=["Phone", "Score"])
    return dfs


@st.cache_data(ttl=600)
def compute_total(dfs):
    merged = None
    for name, df in dfs.items():
        renamed = df.rename(columns={"Score": f"Score_{name}"})
        if merged is None:
            merged = renamed
        else:
            merged = merged.merge(renamed, on="Phone", how="outer")
    score_cols = [c for c in merged.columns if c.startswith("Score_")]
    merged["Total"] = merged[score_cols].fillna(0).sum(axis=1).astype(int)
    return merged[["Phone", "Total"]]


def get_prize_counts(total_df):
    counts = {}
    for p in PRIZES:
        counts[p["score"]] = int((total_df["Total"] >= p["score"]).sum())
    return counts


# ─────────────────────────────────────────────
# 樣式
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;900&family=Space+Mono:wght@400;700&display=swap');

:root {
    --primary:    #003366;
    --primary2:   #004a99;
    --accent:     #f28500;
    --accent2:    #ffb347;
    --teal:       #00c9a7;
    --pink:       #e94f8b;
    --bg:         #0f1923;
    --bg2:        #162030;
    --bg3:        #1e2d40;
    --surface:    #1e2d40;
    --surface2:   #253547;
    --border:     #2a3f58;
    --text:       #e8f0f8;
    --text-mid:   #8aaac8;
    --text-lt:    #506880;
    --success:    #00c9a7;
    --radius:     10px;
    --radius-lg:  14px;
}

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
    background: var(--bg) !important;
    color: var(--text);
}
.stApp {
    background: var(--bg) !important;
    background-image:
        linear-gradient(rgba(0,51,102,.18) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,51,102,.18) 1px, transparent 1px) !important;
    background-size: 40px 40px !important;
}

.stApp::before {
    content: '⚡  ★  🎮  ⚡  ★  🎯  ⚡  ★  🎮  ⚡  ★  🎯  ⚡  ★  🎮  ⚡';
    position: fixed;
    top: 0; left: 0; right: 0;
    padding: 6px 0;
    text-align: center;
    font-size: .65rem;
    letter-spacing: .5em;
    color: rgba(242,133,0,.25);
    background: rgba(15,25,35,.9);
    border-bottom: 1px solid rgba(242,133,0,.15);
    z-index: 999;
    pointer-events: none;
}
.stApp::after {
    content: '⚡  ★  🎮  ⚡  ★  🎯  ⚡  ★  🎮  ⚡  ★  🎯  ⚡  ★  🎮  ⚡';
    position: fixed;
    bottom: 0; left: 0; right: 0;
    padding: 6px 0;
    text-align: center;
    font-size: .65rem;
    letter-spacing: .5em;
    color: rgba(242,133,0,.25);
    background: rgba(15,25,35,.9);
    border-top: 1px solid rgba(242,133,0,.15);
    z-index: 999;
    pointer-events: none;
}

@media (min-width: 900px) {
.game-col-left, .game-col-right {
    position: fixed;
    top: 0; bottom: 0;
    width: 72px;
    z-index: 100;
    pointer-events: none;
    overflow: hidden;
}
.game-col-left  { left: 0; }
.game-col-right { right: 0; }

.game-col-left::before,
.game-col-right::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='72' height='40'%3E%3Crect width='72' height='40' fill='%23162030'/%3E%3Crect x='1' y='1' width='34' height='18' rx='1' fill='%231a2d42' stroke='%230a1520' stroke-width='1.5'/%3E%3Crect x='37' y='1' width='34' height='18' rx='1' fill='%231e3250' stroke='%230a1520' stroke-width='1.5'/%3E%3Crect x='1' y='21' width='22' height='18' rx='1' fill='%231e3250' stroke='%230a1520' stroke-width='1.5'/%3E%3Crect x='25' y='21' width='24' height='18' rx='1' fill='%231a2d42' stroke='%230a1520' stroke-width='1.5'/%3E%3Crect x='51' y='21' width='20' height='18' rx='1' fill='%231e3250' stroke='%230a1520' stroke-width='1.5'/%3E%3C/svg%3E");
    background-size: 72px 40px;
    background-repeat: repeat-y;
}

.game-col-left::after,
.game-col-right::after {
    content: '';
    position: absolute;
    top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(
        to bottom,
        transparent 0%,
        rgba(242,133,0,.5) 15%,
        rgba(242,133,0,.8) 30%,
        rgba(242,133,0,.5) 50%,
        rgba(242,133,0,.8) 70%,
        rgba(242,133,0,.5) 85%,
        transparent 100%
    );
    animation: glowpulse 2.5s ease-in-out infinite alternate;
}
.game-col-left::after  { right: 0; }
.game-col-right::after { left: 0; }

.game-door-left, .game-door-right {
    position: fixed;
    top: 50%;
    transform: translateY(-50%);
    width: 60px;
    z-index: 101;
    pointer-events: none;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
}
.game-door-left  { left: 6px; }
.game-door-right { right: 6px; }
}

@media (max-width: 899px) {
    .game-col-left, .game-col-right,
    .game-door-left, .game-door-right { display: none !important; }
    .stApp::before, .stApp::after {
        font-size: .5rem !important;
        letter-spacing: .25em !important;
        padding: 4px 0 !important;
    }
    .block-container {
        padding-left: .75rem !important;
        padding-right: .75rem !important;
    }
}

@keyframes glowpulse {
    from { opacity: .5; }
    to   { opacity: 1; }
}

.door-cap {
    width: 52px; height: 12px;
    background: linear-gradient(180deg, #c97a1a, #7a4a0a);
    border-radius: 4px 4px 0 0;
    border: 1.5px solid #5a3508;
    border-bottom: none;
}
.door-body {
    width: 52px;
    background: linear-gradient(180deg, #a0600e 0%, #7a4808 40%, #5c3806 100%);
    border: 1.5px solid #3a2504;
    border-top: none;
    border-bottom: none;
    padding: 8px 6px;
    display: flex;
    flex-direction: column;
    gap: 5px;
    align-items: center;
}
.door-plank {
    width: 38px; height: 10px;
    background: linear-gradient(180deg, #c8820e, #8a5208);
    border-radius: 2px;
    border: 1px solid #4a2e04;
    box-shadow: inset 0 1px 0 rgba(255,200,80,.2);
}
.door-knob {
    width: 10px; height: 10px;
    background: radial-gradient(circle at 35% 35%, #ffd700, #b8860b);
    border-radius: 50%;
    border: 1px solid #8b6914;
    margin: 2px auto;
}
.door-base {
    width: 52px; height: 10px;
    background: linear-gradient(180deg, #7a4808, #3a2202);
    border-radius: 0 0 4px 4px;
    border: 1.5px solid #3a2504;
    border-top: none;
}
.door-star {
    font-size: 1rem;
    color: #f28500;
    opacity: .7;
    margin: 4px 0;
    animation: starpulse 2s ease-in-out infinite alternate;
}
@keyframes starpulse {
    from { opacity: .4; transform: scale(1); }
    to   { opacity: .9; transform: scale(1.15); }
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 700px;
    position: relative;
}
#MainMenu, footer, header { visibility: hidden; }
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

.stTextInput > div > div > input {
    background: var(--bg2) !important;
    border: 2px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--accent2) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 1rem !important;
    padding: .65rem 1rem !important;
    text-align: center;
    letter-spacing: .2em;
    box-shadow: inset 0 2px 6px rgba(0,0,0,.3) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--text-lt) !important; }
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(242,133,0,.2), inset 0 2px 6px rgba(0,0,0,.3) !important;
}

.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    font-weight: 900 !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    letter-spacing: .08em !important;
    text-transform: uppercase;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: .7rem 2rem !important;
    width: 100%;
    border-bottom: 4px solid #b36200 !important;
    transition: transform .1s, border-bottom .1s;
}
.stButton > button:hover {
    background: #ffb347 !important;
    transform: translateY(-2px);
}
.stButton > button:active {
    transform: translateY(2px) !important;
    border-bottom: 1px solid #b36200 !important;
}

.score-card {
    background: var(--primary);
    border: 2px solid var(--accent);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    text-align: center;
    margin: .8rem 0;
    position: relative;
    overflow: hidden;
    clip-path: polygon(0 8px,8px 0,calc(100% - 8px) 0,100% 8px,100% calc(100% - 8px),calc(100% - 8px) 100%,8px 100%,0 calc(100% - 8px));
}
.score-card::before {
    content:'XP';
    position:absolute;
    top:10px; left:14px;
    font-size:.6rem;
    font-weight:700;
    letter-spacing:.15em;
    color:rgba(242,133,0,.4);
    font-family:'Space Mono',monospace;
}
.score-phone {
    font-size: .75rem;
    color: rgba(255,255,255,.45);
    letter-spacing: .12em;
    margin-bottom: .2rem;
    font-family: 'Space Mono', monospace;
}
.score-number {
    font-family: 'Space Mono', monospace;
    font-size: 3.6rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
    text-shadow: 0 0 20px rgba(242,133,0,.4);
}
.score-unit {
    font-size: .75rem;
    color: rgba(255,255,255,.5);
    margin-top: .3rem;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.not-found {
    background: var(--surface);
    border: 2px dashed var(--border);
    border-radius: var(--radius-lg);
    padding: 2rem;
    text-align: center;
    color: var(--text-mid);
    font-size: .9rem;
    margin: 1rem 0;
}

.section-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: .68rem;
    font-weight: 800;
    color: var(--accent);
    letter-spacing: .18em;
    text-transform: uppercase;
    margin: 1.4rem 0 .6rem;
}
.section-label::before,
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border));
}
.section-label::before {
    background: linear-gradient(90deg, var(--border), transparent);
}

/* ── 注意事項區塊 ── */
.notice-section {
    margin-top: 2.5rem;
    border-top: 1px solid var(--border);
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
.notice-title {
    font-size: .72rem;
    font-weight: 900;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.notice-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}
.notice-block {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin-bottom: .75rem;
}
.notice-block p {
    font-size: .78rem;
    color: var(--text-mid);
    line-height: 2;
    margin: 0;
}
.notice-block b {
    color: var(--accent2);
    font-weight: 700;
}
.notice-station-list {
    font-size: .76rem;
    color: var(--text-mid);
    line-height: 2;
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin-bottom: .75rem;
}
.notice-station-list b {
    color: var(--teal);
    display: block;
    margin-bottom: .5rem;
    font-size: .72rem;
    letter-spacing: .12em;
    text-transform: uppercase;
}
.station-tag {
    display: inline-block;
    background: #0d2233;
    border: 1px solid #2a3f58;
    border-radius: 5px;
    padding: 2px 9px;
    margin: 2px 3px;
    font-size: .72rem;
    color: var(--teal);
    line-height: 1.8;
}
.notice-footer {
    font-size: .7rem;
    color: var(--text-lt);
    text-align: center;
    padding: .75rem 0 .5rem;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 溫度計（用 components.html 讓 JS 正常執行）
# ─────────────────────────────────────────────
def render_thermometer(user_score, prize_counts):
    capped = min(user_score, MAX_SCORE)
    pct = capped / MAX_SCORE * 100

    IMAGE_FILES = ["a1.jpg","a2.jpg","a3.jpg","a4.jpg","a5.jpg","a6.jpg","a7.jpg","a8.jpg"]
    img_data_list  = [img_to_base64(f) for f in IMAGE_FILES]
    js_img_array   = json.dumps(img_data_list)
    js_name_array  = json.dumps([p["name"] for p in PRIZES])
    js_score_array = json.dumps([f'{p["score"]:,}' for p in PRIZES])

    ROW_BASE = (
        "display:flex;align-items:center;gap:8px;"
        "border-radius:8px;padding:7px 10px;"
        "margin-bottom:4px;border:1px solid #2a3f58;"
        "background:#1e2d40;cursor:pointer;transition:opacity .15s;"
    )
    ROW_UNLOCKED = (
        "display:flex;align-items:center;gap:8px;"
        "border-radius:8px;padding:7px 10px;"
        "margin-bottom:4px;border:1px solid #f28500;"
        "background:#2a1f0d;cursor:pointer;transition:opacity .15s;"
    )
    DOT_BASE       = "width:9px;height:9px;border-radius:50%;background:#2a3f58;flex-shrink:0;"
    DOT_UNLOCKED   = "width:9px;height:9px;border-radius:50%;background:#f28500;box-shadow:0 0 5px #f28500;flex-shrink:0;"
    SCORE_BASE     = "font-family:monospace;font-size:.7rem;color:#506880;min-width:48px;"
    SCORE_UNLOCKED = "font-family:monospace;font-size:.7rem;color:#f28500;min-width:48px;font-weight:700;"
    NAME_BASE      = "font-size:.8rem;font-weight:600;color:#506880;flex:1;"
    NAME_UNLOCKED  = "font-size:.8rem;font-weight:700;color:#e8f0f8;flex:1;"

    prize_rows_html = ""
    for idx, p in enumerate(PRIZES):
        unlocked = user_score >= p["score"]
        row_s    = ROW_UNLOCKED if unlocked else ROW_BASE
        dot_s    = DOT_UNLOCKED if unlocked else DOT_BASE
        score_s  = SCORE_UNLOCKED if unlocked else SCORE_BASE
        name_s   = NAME_UNLOCKED if unlocked else NAME_BASE
        lock_icon= "🔓" if unlocked else "🔒"

        prize_rows_html += (
            f'<div style="{row_s}" onclick="showPrize({idx})" '
            f'onmouseover="this.style.opacity=\'0.75\'" '
            f'onmouseout="this.style.opacity=\'1\'">' +
            f'<div style="{dot_s}"></div>' +
            f'<span style="{score_s}">{p["score"]:,}</span>' +
            f'<span style="font-size:1rem;">{p["emoji"]}</span>' +
            f'<span style="{name_s}">{p["name"]}</span>' +
            f'<span style="font-size:.75rem;">{lock_icon}</span>' +
            f'<span style="font-size:.65rem;color:#8aaac8;margin-left:2px;">👁</span>' +
            '</div>'
        )

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ margin:0; padding:0; background:transparent;
         font-family:'Nunito',sans-serif; overflow-x:hidden; }}

  #overlay {{
    display:none;
    position:fixed;
    inset:0;
    background:rgba(0,0,0,.88);
    align-items:center;
    justify-content:center;
    z-index:9999;
  }}
  #overlay.open {{ display:flex; }}

  #modal-box {{
    background:#1e2d40;
    border:2px solid #f28500;
    border-radius:14px;
    padding:20px;
    max-width:400px;
    width:90%;
    position:relative;
    text-align:center;
    box-shadow:0 0 40px rgba(242,133,0,.4);
  }}
  #closeBtn {{
    position:absolute;top:10px;right:14px;
    font-size:1.4rem;cursor:pointer;
    color:#f28500;font-weight:900;line-height:1;
  }}
  #modalScore {{
    display:inline-block;background:#f28500;color:#fff;
    font-family:monospace;font-size:.75rem;font-weight:700;
    padding:3px 14px;border-radius:4px;margin-bottom:10px;
    letter-spacing:.1em;
  }}
  #modalName {{
    font-size:1rem;font-weight:800;color:#e8f0f8;
    margin-bottom:14px;line-height:1.4;
  }}
  #modalImg {{
    width:100%;border-radius:10px;
    border:1px solid #2a3f58;
    object-fit:contain;max-height:300px;
  }}
  .hint {{ margin-top:10px;font-size:.7rem;color:#506880; }}
</style>
</head>
<body>

<div id="overlay" onclick="closeModal()">
  <div id="modal-box" onclick="event.stopPropagation()">
    <div id="closeBtn" onclick="closeModal()">✕</div>
    <div id="modalScore"></div>
    <div id="modalName"></div>
    <img id="modalImg" src="" alt="獎品圖片"/>
    <div class="hint">點擊圖片外部或按 Esc 關閉</div>
  </div>
</div>

<div style="display:flex;gap:14px;align-items:stretch;margin:8px 0;">
  <div style="flex:0 0 38px;display:flex;flex-direction:column;align-items:center;">
    <div style="width:18px;background:#0f1923;border-radius:9px 9px 0 0;
        border:2px solid #2a3f58;position:relative;overflow:hidden;flex:1;">
      <div style="position:absolute;bottom:0;left:0;right:0;height:{pct:.1f}%;
          background:linear-gradient(to top,#f28500,#ffb347);
          box-shadow:0 0 8px #f28500;"></div>
    </div>
    <div style="width:30px;height:30px;background:#f28500;border-radius:50%;
        border:3px solid #2a3f58;margin-top:-2px;flex-shrink:0;
        box-shadow:0 0 10px rgba(242,133,0,.5);"></div>
  </div>
  <div style="flex:1;">
    {prize_rows_html}
  </div>
</div>

<script>
var _imgs   = {js_img_array};
var _names  = {js_name_array};
var _scores = {js_score_array};

function showPrize(i) {{
  document.getElementById("modalImg").src         = _imgs[i];
  document.getElementById("modalName").innerText  = _names[i];
  document.getElementById("modalScore").innerText = _scores[i] + " 分獎項";
  document.getElementById("overlay").classList.add("open");
}}
function closeModal() {{
  document.getElementById("overlay").classList.remove("open");
}}
document.addEventListener("keydown", function(e) {{
  if (e.key === "Escape") closeModal();
}});

function reportHeight() {{
  var h = document.body.scrollHeight;
  window.parent.postMessage({{type:"streamlit:setFrameHeight", height: h}}, "*");
}}
window.addEventListener("load", function() {{
  reportHeight();
  setTimeout(reportHeight, 150);
  setTimeout(reportHeight, 500);
  setTimeout(reportHeight, 1000);
}});
</script>

</body>
</html>"""

    estimated_height = len(PRIZES) * 62 + 200
    components.html(html, height=estimated_height, scrolling=True)


# ─────────────────────────────────────────────
# 全部 6 張卡片放進同一個 iframe，間距完全一致
# ─────────────────────────────────────────────
def render_all_cards(
    deg_score, dc, ac,
    car_score, car_bound,
    sta_score, special_cnt, normal_cnt, special_names, normal_names,
    cnt_score, charge_cnt,
    sav_score, total_amt,
    sp_score, sp_mark
):
    next_ms  = ((charge_cnt // 20) + 1) * 20
    cnt_left = next_ms - charge_cnt

    def parse_names(raw):
        if not raw or str(raw).strip() in ("", "nan", "None"):
            return []
        return [n.strip() for n in str(raw).split(",") if n.strip()]

    special_list = parse_names(special_names)
    normal_list  = parse_names(normal_names)
    js_special   = json.dumps(special_list)
    js_normal    = json.dumps(normal_list)

    def card_header_html(emoji, title, score, accent):
        return (
            f'<div class="cheader">'
            f'<div class="ctitle">'
            f'<div class="ibox">{emoji}</div>'
            f'<span class="ttext">{title}</span>'
            f'</div>'
            f'<div class="sbadge" style="border-color:{accent}44;">'
            f'<span class="snum" style="color:{accent};">+{score:,}</span>'
            f'<span class="sunit">分</span>'
            f'</div>'
            f'</div>'
        )

    if car_bound:
        bound_html = ('<span style="background:#0d2e1f;color:#00c9a7;border:1px solid #00c9a744;'
                      'border-radius:5px;padding:2px 10px;font-weight:700;">✅ 已完成綁定</span>')
    else:
        bound_html = ('<span style="background:#2e1a0d;color:#f28500;border:1px solid #f2850044;'
                      'border-radius:5px;padding:2px 10px;font-weight:700;">⚠️ 尚未綁定</span>')

    sp_card_html = ""
    if sp_score > 0:
        sp_card_html = (
            '<div class="card" style="border-left-color:#f28500;">' +
            card_header_html("🌟", "特殊任務", sp_score, "#f28500") +
            '<div class="summary">達成特殊任務可獲得額外積分，敬請期待</div>' +
            f'<div class="ptext">活動名稱：<b style="color:#f28500;">{sp_mark}</b></div>' +
            '</div>'
        )

    card_count = 5 + (1 if sp_score > 0 else 0)
    base_h = 135 * card_count + 60
    list_extra = (len(special_list) + len(normal_list)) * 36 + 120
    estimated_h = base_h + list_extra

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;900&family=Space+Mono:wght@400;700&display=swap');
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Nunito',sans-serif;background:transparent;overflow-x:hidden;}}

.card{{
  background:#1e2d40;
  border:1px solid #2a3f58;
  border-left:3px solid #f28500;
  border-radius:10px;
  padding:13px 15px;
  margin-bottom:8px;
}}
.cheader{{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;}}
.ctitle{{display:flex;align-items:center;gap:8px;}}
.ibox{{background:#253547;border-radius:7px;width:30px;height:30px;
       display:flex;align-items:center;justify-content:center;
       font-size:1rem;border:1px solid #2a3f58;flex-shrink:0;}}
.ttext{{font-weight:800;font-size:.9rem;color:#e8f0f8;}}
.sbadge{{background:#0f1923;border:1px solid;border-radius:6px;
         padding:2px 10px;display:flex;align-items:baseline;gap:3px;}}
.snum{{font-family:monospace;font-size:.95rem;font-weight:700;}}
.sunit{{font-size:.65rem;color:#506880;}}
.summary{{font-size:.72rem;color:#506880;line-height:1.8;
          margin-bottom:7px;padding-bottom:7px;border-bottom:1px solid #253547;}}
.ptext{{font-size:.8rem;color:#8aaac8;}}
.prow{{display:flex;align-items:center;justify-content:space-between;gap:8px;}}

.vbtn{{
  background:transparent;border:1px solid #ffd70066;border-radius:6px;
  color:#ffd700;font-size:.72rem;font-weight:700;
  font-family:'Nunito',sans-serif;padding:3px 10px;
  cursor:pointer;transition:background .15s;white-space:nowrap;flex-shrink:0;
}}
.vbtn:hover{{background:#ffd70022;color:#fff;}}
#sta-panel{{display:none;margin-top:10px;border-top:1px solid #2a3f58;padding-top:10px;}}
#sta-panel.open{{display:block;}}
.llabel{{font-size:.65rem;font-weight:800;letter-spacing:.15em;
         text-transform:uppercase;margin-bottom:6px;margin-top:8px;}}
.slist{{list-style:none;display:flex;flex-wrap:wrap;gap:5px;margin-bottom:4px;}}
.stag{{display:inline-flex;align-items:center;gap:4px;border-radius:6px;
       padding:3px 9px;font-size:.76rem;font-weight:700;line-height:1.4;}}
.stag.sp{{background:#2a1f0d;border:1px solid #ffd70088;color:#ffd700;}}
.stag.nm{{background:#0d2e20;border:1px solid #00c9a788;color:#00c9a7;}}
.enote{{font-size:.75rem;color:#506880;font-style:italic;}}
</style>
</head>
<body>

<!-- 🔋 充電度數 -->
<div class="card" style="border-left-color:#f28500;">
  {card_header_html("🔋", "充電度數", deg_score, "#f28500")}
  <div class="summary">
  DC 充電：每 1 度 = 1 分 ／ AC 充電：每 10 度 = 1 分<br>
  (有開立發票，且發票金額不為零始認列)
  </div>
  <div class="ptext">
    DC <b style="color:#f28500;">{dc:,.2f} 度</b>　／　AC <b style="color:#f28500;">{ac:,.2f} 度</b>
  </div>
</div>

<!-- 🚗 車輛綁定 -->
<div class="card" style="border-left-color:#f28500;">
  {card_header_html("🚗", "車輛綁定", car_score, "#f28500")}
  <div class="summary">完成「隨插即充」功能綁定，立即獲得 100 分 <br>
  ※每帳號限得一次
  </div>
  <div class="ptext">綁定狀態：{bound_html}</div>
</div>

<!-- 📍 拜訪站點 -->
<div class="card" style="border-left-color:#ffd700;">
  {card_header_html("📍", "拜訪站點", sta_score, "#ffd700")}
  <div class="summary">
  一般站點：每站 10 分 ／ 精選站點：每站 30 分（基本 10 + 額外 20）<br>
  ※每一站點僅計算一次，重複拜訪不重複計分
  (有開立發票，且發票金額不為零始認列)
  </div>
  <div class="prow">
    <div class="ptext">
      精選站點 <b style="color:#ffd700;">{special_cnt} 站</b>
      　／　一般站點 <b style="color:#00c9a7;">{normal_cnt} 站</b>
      　共 <b style="color:#e8f0f8;font-size:.9rem;">{special_cnt+normal_cnt} 站</b>
    </div>
    <button class="vbtn" id="toggleBtn" onclick="toggleList()">📋 查看站點</button>
  </div>
  <div id="sta-panel">
    <div><div class="llabel" style="color:#ffd700;">⭐ 精選站點</div>
         <ul class="slist" id="sp-list"></ul></div>
    <div><div class="llabel" style="color:#00c9a7;">📍 一般站點</div>
         <ul class="slist" id="nm-list"></ul></div>
  </div>
</div>

<!-- 🔢 充電次數 -->
<div class="card" style="border-left-color:#f28500;">
  {card_header_html("🔢", "充電次數", cnt_score, "#f28500")}
  <div class="summary">
  每累積 20 次充電 = 50 分<br>
  (有開立發票，且發票金額不為零、單次度數>10度始認列一次)
  </div>
  <div class="ptext">
    目前充電 <b style="color:#00c9a7;">{charge_cnt} 次</b>
    　距下一里程碑還差 <b style="color:#f28500;">{cnt_left} 次</b>（第 {next_ms} 次）
  </div>
</div>

<!-- 💰 儲值金額 -->
<div class="card" style="border-left-color:#f28500;">
  {card_header_html("💰", "儲值金額", sav_score, "#f28500")}
  <div class="summary">每儲值 1,000 元 = 10 分</div>
  <div class="ptext">累積儲值 <b style="color:#f28500;">NT$ {total_amt:,}</b></div>
</div>

{sp_card_html}

<script>
var spNames = {js_special};
var nmNames = {js_normal};
var open    = false;

function buildList(names, el, cls) {{
  el.innerHTML = "";
  if (!names.length) {{ el.innerHTML='<li class="enote">（無紀錄）</li>'; return; }}
  names.forEach(function(n) {{
    var li = document.createElement("li");
    li.innerHTML = '<span class="stag ' + cls + '">' +
      (cls==="sp"?"⭐":"📍") + " " + n + "</span>";
    el.appendChild(li);
  }});
}}
buildList(spNames, document.getElementById("sp-list"), "sp");
buildList(nmNames, document.getElementById("nm-list"), "nm");

function toggleList() {{
  open = !open;
  document.getElementById("sta-panel").classList.toggle("open", open);
  document.getElementById("toggleBtn").textContent = open ? "▲ 收起" : "📋 查看站點";
  reportH();
}}

function reportH() {{
  var h = document.body.scrollHeight;
  window.parent.postMessage(
    {{type:"streamlit:setFrameHeight", height: h + 10}}, "*"
  );
}}

window.addEventListener("load", function() {{
  reportH();
  setTimeout(reportH, 150);
  setTimeout(reportH, 500);
  setTimeout(reportH, 1000);
}});
</script>
</body>
</html>"""

    components.html(html, height=estimated_h, scrolling=True)


# ─────────────────────────────────────────────
# 活動說明區塊（顯示在注意事項之前）
# ─────────────────────────────────────────────
def render_activity():
    st.markdown("""
<div style="
    margin-top: 2.5rem;
    border-top: 1px solid var(--border);
    padding-top: 1.5rem;
">

  <!-- 標題列 -->
  <div style="
    font-size:.72rem; font-weight:900; letter-spacing:.18em;
    text-transform:uppercase; color:var(--accent); margin-bottom:1rem;
    display:flex; align-items:center; gap:8px;
  ">📢 活動說明
    <span style="flex:1;height:1px;background:var(--border);display:inline-block;"></span>
  </div>

  <!-- 主標語卡片 -->
  <div style="
    background:var(--primary); border:2px solid var(--accent);
    border-radius:var(--radius-lg); padding:1.2rem 1.4rem;
    text-align:center; margin-bottom:.9rem;
    clip-path:polygon(0 6px,6px 0,calc(100% - 6px) 0,100% 6px,100% calc(100% - 6px),calc(100% - 6px) 100%,6px 100%,0 calc(100% - 6px));
  ">
    <div style="font-size:1.05rem;font-weight:900;color:var(--accent2);line-height:1.7;">
      🎂 EVALUE 5歲生日慶
    </div>
    <div style="font-size:.85rem;color:var(--text-mid);margin-top:.3rem;line-height:1.9;">
      完成指定任務，累積積分，達到對應門檻即可獲得獎勵<br>
      <span style="font-size:.76rem;color:var(--text-lt);">
        （含：免費充電、EVALUE 點數、DC 快充 50% 點數回饋…等好禮）
      </span>
    </div>
    <div style="margin-top:.9rem;">
      <span style="
        background:var(--accent); color:#fff; font-weight:800;
        font-size:.78rem; border-radius:6px; padding:5px 18px;
        letter-spacing:.06em;
      ">⚡ 活動期間：04/02 ～ 06/22</span>
    </div>
  </div>

  <!-- 主線任務 -->
  <div style="
    background:var(--bg2); border:1px solid var(--border);
    border-left:3px solid var(--accent);
    border-radius:var(--radius); padding:1rem 1.2rem; margin-bottom:.75rem;
  ">
    <div style="
      font-size:.7rem; font-weight:900; letter-spacing:.15em;
      text-transform:uppercase; color:var(--accent); margin-bottom:.75rem;
      display:flex; align-items:center; gap:8px;
    ">📍 主線任務
      <span style="color:var(--text-lt);font-size:.65rem;font-weight:600;
                   letter-spacing:.04em;text-transform:none;">（可持續參加）</span>
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:.82rem;">
      <tr>
        <td style="padding:5px 0;color:var(--text-mid);">🔋 每 DC 充電 1 度</td>
        <td style="text-align:right;color:var(--accent);font-weight:800;
                   font-family:'Space Mono',monospace;white-space:nowrap;">= 1 分</td>
      </tr>
      <tr>
        <td style="padding:5px 0;color:var(--text-mid);">🔌 每 AC 充電 10 度</td>
        <td style="text-align:right;color:var(--accent);font-weight:800;
                   font-family:'Space Mono',monospace;white-space:nowrap;">= 1 分</td>
      </tr>
      <tr>
        <td style="padding:5px 0;color:var(--text-mid);">💳 每儲值 $1,000</td>
        <td style="text-align:right;color:var(--accent);font-weight:800;
                   font-family:'Space Mono',monospace;white-space:nowrap;">= 10 分</td>
      </tr>
      <tr>
        <td style="padding:5px 0;color:var(--text-mid);">📍 每到一個站點充電</td>
        <td style="text-align:right;color:var(--accent);font-weight:800;
                   font-family:'Space Mono',monospace;white-space:nowrap;">= 10 分</td>
      </tr>
      <tr>
        <td style="padding:5px 0;color:var(--text-mid);">⭐ 每探索一個精選站點（額外加分20分）</td>
        <td style="text-align:right;color:#ffd700;font-weight:800;
                   font-family:'Space Mono',monospace;white-space:nowrap;">= 30 分</td>
      </tr>
      <tr>
        <td style="padding:5px 0;color:var(--text-mid);">🔢 每充電次數累積達 20 次</td>
        <td style="text-align:right;color:var(--accent);font-weight:800;
                   font-family:'Space Mono',monospace;white-space:nowrap;">= 50 分</td>
      </tr>
    </table>
  </div>

  <!-- 支線任務 -->
  <div style="
    background:var(--bg2); border:1px solid var(--border);
    border-left:3px solid var(--teal);
    border-radius:var(--radius); padding:1rem 1.2rem; margin-bottom:.75rem;
  ">
    <div style="
      font-size:.7rem; font-weight:900; letter-spacing:.15em;
      text-transform:uppercase; color:var(--teal); margin-bottom:.75rem;
      display:flex; align-items:center; gap:8px;
    ">📍 支線任務
      <span style="color:var(--text-lt);font-size:.65rem;font-weight:600;
                   letter-spacing:.04em;text-transform:none;">（每人限一次）</span>
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:.82rem;">
      <tr>
        <td style="padding:5px 0;color:var(--text-mid);">👍 官方 FB 追蹤</td>
        <td style="text-align:right;color:var(--teal);font-weight:800;
                   font-family:'Space Mono',monospace;white-space:nowrap;">= 25 分</td>
      </tr>
      <tr>
        <td style="padding:5px 0;color:var(--text-mid);">📸 官方 IG 追蹤</td>
        <td style="text-align:right;color:var(--teal);font-weight:800;
                   font-family:'Space Mono',monospace;white-space:nowrap;">= 25 分</td>
      </tr>
      <tr>
        <td style="padding:5px 0;color:var(--text-mid);">▶️ 官方 YouTube 追蹤</td>
        <td style="text-align:right;color:var(--teal);font-weight:800;
                   font-family:'Space Mono',monospace;white-space:nowrap;">= 25 分</td>
      </tr>
      <tr>
        <td style="padding:5px 0;color:var(--text-mid);">💬 官方 Line@ 追蹤</td>
        <td style="text-align:right;color:var(--teal);font-weight:800;
                   font-family:'Space Mono',monospace;white-space:nowrap;">= 25 分</td>
      </tr>
      <tr>
        <td style="padding:5px 0;color:var(--text-mid);">🪪 完成 EVALUE 名片牆</td>
        <td style="text-align:right;color:var(--teal);font-weight:800;
                   font-family:'Space Mono',monospace;white-space:nowrap;">= 99 分</td>
      </tr>
      <tr>
        <td style="padding:5px 0;color:var(--text-mid);">🚗 綁定並使用隨插即充充電</td>
        <td style="text-align:right;color:var(--teal);font-weight:800;
                   font-family:'Space Mono',monospace;white-space:nowrap;">= 100 分</td>
      </tr>
    </table>
  </div>

  <!-- 獎項內容 -->
  <div style="
    background:var(--bg2); border:1px solid var(--border);
    border-left:3px solid var(--pink);
    border-radius:var(--radius); padding:1rem 1.2rem; margin-bottom:.75rem;
  ">
    <div style="
      font-size:.7rem; font-weight:900; letter-spacing:.15em;
      text-transform:uppercase; color:var(--pink); margin-bottom:.75rem;
    ">🎁 獎項內容</div>
    <table style="width:100%;border-collapse:collapse;font-size:.82rem;">
      <tr>
        <td style="padding:5px 0;">
          <span style="font-family:'Space Mono',monospace;color:var(--accent);font-weight:800;
                       display:inline-block;min-width:58px;">5000分</span>
          <span style="color:var(--text-mid);">⚡ EVALUE 5,000 點數</span>
        </td>
      </tr>
      <tr>
        <td style="padding:5px 0;">
          <span style="font-family:'Space Mono',monospace;color:var(--accent);font-weight:800;
                       display:inline-block;min-width:58px;">2500分</span>
          <span style="color:var(--text-mid);">🎁 隨插即充 二日免費充電</span>
        </td>
      </tr>
      <tr>
        <td style="padding:5px 0;">
          <span style="font-family:'Space Mono',monospace;color:var(--accent);font-weight:800;
                       display:inline-block;min-width:58px;">2000分</span>
          <span style="color:var(--text-mid);">🔌 EVALUE 500 點數</span>
        </td>
      </tr>
      <tr>
        <td style="padding:5px 0;">
          <span style="font-family:'Space Mono',monospace;color:var(--accent);font-weight:800;
                       display:inline-block;min-width:58px;">1500分</span>
          <span style="color:var(--text-mid);">🎫 隨插即充 一日免費充電</span>
        </td>
      </tr>
      <tr>
        <td style="padding:5px 0;">
          <span style="font-family:'Space Mono',monospace;color:var(--accent);font-weight:800;
                       display:inline-block;min-width:58px;">1000分</span>
          <span style="color:var(--text-mid);">🎟️ DC 快充 50% 點數回饋 3 筆</span>
        </td>
      </tr>
      <tr>
        <td style="padding:5px 0;">
          <span style="font-family:'Space Mono',monospace;color:var(--accent);font-weight:800;
                       display:inline-block;min-width:58px;">750分</span>
          <span style="color:var(--text-mid);">⭐ EVALUE 500 點數</span>
        </td>
      </tr>
      <tr>
        <td style="padding:5px 0;">
          <span style="font-family:'Space Mono',monospace;color:var(--accent);font-weight:800;
                       display:inline-block;min-width:58px;">500分</span>
          <span style="color:var(--text-mid);">🎟️ DC 快充 50% 點數回饋 2 筆</span>
        </td>
      </tr>
      <tr>
        <td style="padding:5px 0;">
          <span style="font-family:'Space Mono',monospace;color:var(--accent);font-weight:800;
                       display:inline-block;min-width:58px;">300分</span>
          <span style="color:var(--text-mid);">💎 EVALUE 100 點數</span>
        </td>
      </tr>
    </table>
  </div>

  <!-- 累積領獎說明 -->
  <div style="
    background:#0a1e14; border:1px solid #00c9a755;
    border-radius:var(--radius); padding:.9rem 1.2rem;
  ">
    <div style="font-size:.8rem;color:var(--teal);font-weight:800;margin-bottom:.5rem;">
      🔔 獎項累積說明
    </div>
    <div style="font-size:.78rem;color:var(--text-mid);line-height:2;">
      達成積分門檻時，可<b style="color:var(--accent2);">累積領取</b>該門檻以下所有獎項。<br>
      分數愈高拿得愈多，不是只能選一份，而是<b style="color:var(--accent2);">「一路往上拿」</b>！
    </div>
    <div style="
      margin-top:.65rem; padding:.6rem .9rem;
      background:#0d1a10; border-radius:7px;
      font-size:.75rem; color:var(--text-lt); line-height:2;
      border:1px solid #00c9a722;
    ">
      📌 <b style="color:#e8f0f8;">範例：</b><br>
      500 分 → 300分＋500分 獎品<br>
      1,000 分 → 300＋500＋750＋1,000 分 獎品<br>
      5,000 分 → 全部八個獎項 🎉
    </div>
  </div>

</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 注意事項區塊
# ─────────────────────────────────────────────
def render_notice():
    stations = [
        "宜蘭元健大和宜科觀光工廠","宜蘭壯圍共乘停車場","宜蘭南門站停車場","宜蘭科學園區",
        "苗栗銅鑼科學園區","高鐵桃園停車場","嘟嘟房高鐵雲林站","台中上城里停車場",
        "台東航空站","台南南瀛綠都心停車場","宜蘭安永心食館","屏東幸福公園停車場",
        "高雄展覽館","新北澳底公園地下停車場","燦坤_高雄五甲店","燦坤_高雄新岡山店",
        "燦坤_彰化中正店","辰淵_高雄七老爺停車場","辰淵_高雄國軒停車場","辰淵空大停車場",
        "桃園興仁親子公園停車場","國立臺灣歷史博物館遊客停車場",
        "歐特儀_台中中央公園北側停車場","歐特儀_台中中央公園地下停車場",
        "歐特儀股份有限公司社頂公園停車場","歐特儀股份有限公司旗津海岸停車場",
        "聯合醫院_台北松德院區","新北延吉立體停車場","台東南昌街停車場","台東柳州街停車場",
        "成睿_青溪停車場","成睿_建國停車場","成睿_龍安一停車場","基隆樂利停車場",
        "新北水柳腳立體停車場","新北華翠橋下平面停車場","臺東森林公園",
        "台中米平方廣場(二期)","花蓮立閣人文旅店","屏東墾丁瑪雅之家",
        "桃園名人堂花園大飯店","桃園龍潭渴望研究園","高雄MLD台鋁生活商場",
        "新北建昇淡水行政中心","新竹老爺酒店","新竹統一馬武督渡假會議中心",
        "墾丁Hotel dua","新北林口公車轉運站平面停車場","嘉義翁聚德觀光工廠","嘉義吳鳳公園",
    ]
    station_tags = "".join(f'<span class="station-tag">{s}</span>' for s in stations)

    st.markdown(f"""
<div class="notice-section">

  <div class="notice-title">📋 注意事項</div>
  <div class="notice-block">
    <p>
      🪪 <b>前往 EVALUE 名片牆任務</b><br>
      點擊下方連結，完成名片牆登記即可獲得積分！<br>
      <a href="https://forms.office.com/r/S2n0ikM2sy"
         target="_blank"
         style="color:#f28500;font-weight:700;word-break:break-all;
                text-decoration:underline;text-underline-offset:3px;">
        🔗 https://forms.office.com/r/S2n0ikM2sy
      </a>
    </p>
  </div>
  <div class="notice-block">
    <p>
      會員於活動期間完成各種任務（與充電、累積次數、站點有關的任務，充電發票金額不可為零），就能累積積分，達到指定積分即可解鎖回饋，<b>得到該積分門檻以下所有好禮</b>。<br>
      舉例：積分 <b>500 分</b>可得到「DC快充50%回饋券 ×2 ＋ EVALUE 100點」；積分 <b>1,000 分</b>可得到「DC快充50%回饋券 ×3 ＋ EVALUE 500點 ＋ DC快充50%回饋券 ×2 ＋ EVALUE 100點」；積分 <b>5,000 分</b>可得到全部八個獎項。
    </p>
  </div>
  <div class="notice-block">
    <p>
      🔋 <b>DC/AC 充電度數任務</b>：適用所有 EVALUE DC 快充站、AC 充電站。<br>
      📍 <b>探索站點任務</b>：每到一個不同站點充電 <b>10 分</b>（每站僅計一次）；每到一個不同精選站點充電額外加 <b>20 分</b>（每站僅計一次），首次到訪精選站點最高可獲得 <b>30 分</b>。<br>
      🔢 <b>充電次數累積任務</b>：每筆充電須達 <b>10 度（含）以上</b>始計入累積次數，每累積 20 次得 50 分，舉例：累積20次得50分，累積40次得100分，以此類推。<br>
      🚗 <b>隨插即充任務</b>：需綁定並使用隨插即充充電，每帳號限加分一次，得 100 分。<br>
      ⚠️ 以上各任務的<b>充電發票金額不可為零</b>，如為零則該筆充電紀錄不計入積分。未符合資格者恕不另行通知。
    </p>
  </div>

  <div class="notice-station-list">
    <b>⭐ 精選站點名單</b>
    {station_tags}
  </div>

  <div class="notice-block">
    <p>
      <b>積分排除對象</b>：發票金額為零、具免費充電優惠方案身分之用戶。本活動限 EVALUE APP 會員參與，並以 EVALUE 會員帳號之符合資格交易為準。<br>
      回饋之點數將於活動結束後一週內回饋至您的 EVALUE APP 會員帳戶，實際回饋時間依本公司作業規定為準。<b>贈點使用期限至 2027/03/31</b>。詳細點數使用規定請參見 APP 會員中心 &gt; 點數 &gt; 右上角 (i)。
    </p>
  </div>

  <div class="notice-block">
    <p>
      🎟️ <b>DC快充 50% 點數回饋券</b>：回饋計算期間為 <b>2026/07/01 ～ 08/31</b> 的充電紀錄，擇最高單筆消費，回饋充電費（發票金額不可為零）50% 點數至會員帳戶，將於 <b>2026/09/07 入帳</b>。<br>
      🎫 <b>隨插即充一日／二日免費充電方案</b>：限得獎本人一台車輛（隨插即充）使用，EVALUE 將主動聯繫得主安排，<b>使用期限至 2026/12/31</b>。選擇日之 00:00–23:59 充電行為將於日後以無期限點數匯入帳號。<br>
      所有獎品<b>不得更換、折現或轉讓他人</b>。隨插即充適用條件與支援車款以 EVALUE 公告為準；若車輛不支援，請依中獎通知上的聯絡方式洽詢。
    </p>
  </div>

  <div class="notice-footer">
    詳細活動辦法以華城電能公告為準，本公司保留活動之解釋、修改、調整、終止等相關權利。
  </div>

</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 主程式
# ─────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="EVALUE 5歲生日快樂活動",
        page_icon="⚡",
        layout="centered",
    )
    inject_css()

    # 左右磚牆 + 木門
    st.markdown("""
<div class="game-col-left"></div>
<div class="game-col-right"></div>

<div class="game-door-left">
  <div class="door-star">★</div>
  <div class="door-cap"></div>
  <div class="door-body">
    <div class="door-plank"></div>
    <div class="door-plank"></div>
    <div class="door-knob"></div>
    <div class="door-plank"></div>
    <div class="door-plank"></div>
  </div>
  <div class="door-base"></div>
  <div class="door-star">⚡</div>
</div>

<div class="game-door-right">
  <div class="door-star">★</div>
  <div class="door-cap"></div>
  <div class="door-body">
    <div class="door-plank"></div>
    <div class="door-plank"></div>
    <div class="door-knob"></div>
    <div class="door-plank"></div>
    <div class="door-plank"></div>
  </div>
  <div class="door-base"></div>
  <div class="door-star">⚡</div>
</div>
""", unsafe_allow_html=True)

    # 英雄區圖片
    st.image("p1.jpg", use_container_width=True)

    # 載入資料
    try:
        dfs = load_data()
        total_df = compute_total(dfs)
        prize_counts = get_prize_counts(total_df)
        score_index = {
            name: df.set_index("Phone")["Score"].to_dict()
            for name, df in dfs.items()
        }
        total_index = total_df.set_index("Phone")["Total"].to_dict()
    except Exception as e:
        st.error(f"❌ 資料載入失敗：{e}")
        return

    # 查詢輸入
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        phone = st.text_input("", placeholder="請輸入手機門號", label_visibility="collapsed")
        search = st.button("🔍 查詢積分")

    st.markdown("<hr>", unsafe_allow_html=True)

    if search and phone:
        phone = phone.strip()

        user_score = int(total_index.get(phone, 0))

        st.markdown(f"""
<div class="score-card">
    <div class="score-phone">📱 {phone}</div>
    <div class="score-number">{user_score:,}</div>
    <div class="score-unit">活動總積分(最後更新時間：2026/05/05 00:00)</div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div class="section-label">📊 分項積分明細</div>', unsafe_allow_html=True)

        deg_row   = dfs["Degree"][dfs["Degree"]["Phone"] == phone]
        dc        = float(deg_row["TotalDC"].iloc[0])   if not deg_row.empty and "TotalDC"   in deg_row.columns else 0.0
        ac        = float(deg_row["TotalAC"].iloc[0])   if not deg_row.empty and "TotalAC"   in deg_row.columns else 0.0
        deg_score = int(score_index["Degree"].get(phone, 0))

        car_row   = dfs["Car"][dfs["Car"]["Phone"] == phone]
        car_bound = (not car_row.empty and "CarCount" in car_row.columns and
                     str(car_row["CarCount"].iloc[0]).strip().lower() == "true")
        car_score = int(score_index["Car"].get(phone, 0))

        sta_row       = dfs["Station"][dfs["Station"]["Phone"] == phone]
        special_cnt   = int(sta_row["SpecialStationCount"].iloc[0])  if not sta_row.empty and "SpecialStationCount"  in sta_row.columns else 0
        normal_cnt    = int(sta_row["NormalStationCount"].iloc[0])   if not sta_row.empty and "NormalStationCount"   in sta_row.columns else 0
        special_names = sta_row["SpecialStationNames"].iloc[0]       if not sta_row.empty and "SpecialStationNames"  in sta_row.columns else ""
        normal_names  = sta_row["NormalStationNames"].iloc[0]        if not sta_row.empty and "NormalStationNames"   in sta_row.columns else ""
        sta_score     = int(score_index["Station"].get(phone, 0))

        cnt_row    = dfs["Count"][dfs["Count"]["Phone"] == phone]
        charge_cnt = int(cnt_row["PhoneCount"].iloc[0]) if not cnt_row.empty and "PhoneCount" in cnt_row.columns else 0
        cnt_score  = int(score_index["Count"].get(phone, 0))

        sav_row   = dfs["Save"][dfs["Save"]["Phone"] == phone]
        total_amt = int(sav_row["TotalAmount"].iloc[0]) if not sav_row.empty and "TotalAmount" in sav_row.columns else 0
        sav_score = int(score_index["Save"].get(phone, 0))

        sp_score = int(score_index.get("Special", {}).get(phone, 0))
        sp_mark  = ""
        if sp_score > 0:
            sp_row  = dfs["Special"][dfs["Special"]["Phone"] == phone]
            sp_mark = sp_row["Mark"].iloc[0] if not sp_row.empty and "Mark" in sp_row.columns else "特殊活動"

        render_all_cards(
            deg_score, dc, ac,
            car_score, car_bound,
            sta_score, special_cnt, normal_cnt, special_names, normal_names,
            cnt_score, charge_cnt,
            sav_score, total_amt,
            sp_score, sp_mark
        )

        st.markdown("#### 🌡️ 積分進度 & 獎品解鎖")
        render_thermometer(user_score, prize_counts)

    elif search and not phone:
        st.warning("請輸入手機號碼")

    # ── 活動說明（注意事項之前）──
    render_activity()

    # ── 注意事項（永遠顯示在頁面底部） ──
    render_notice()


if __name__ == "__main__":
    main()
