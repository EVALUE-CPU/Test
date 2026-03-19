import streamlit as st
import pandas as pd
import os

# ─────────────────────────────────────────────
# 設定
# ─────────────────────────────────────────────
DATA_DIR = "DATA"

PRIZES = [
    {"score": 10000, "name": "EVALUE 萬元點數",            "emoji": "🏆"},
    {"score": 5000,  "name": "2026 3天免費充電方案",        "emoji": "⚡"},
    {"score": 2500,  "name": "EVALUE 500點",               "emoji": "🎁"},
    {"score": 2000,  "name": "2026 1天免費充電方案",        "emoji": "🔌"},
    {"score": 1500,  "name": "DC 快充 50% 回饋卷 x3",      "emoji": "🎫"},
    {"score": 1000,  "name": "EVALUE 500點",               "emoji": "🎁"},
    {"score": 750,   "name": "DC 快充 50% 回饋卷 x1",      "emoji": "🎫"},
    {"score": 500,   "name": "DC 快充 25% 回饋卷 x3",      "emoji": "🎟️"},
    {"score": 300,   "name": "EVALUE 50點",                "emoji": "⭐"},
]

MAX_SCORE = PRIZES[0]["score"]  # 10000

# ─────────────────────────────────────────────
# 讀取資料
# ─────────────────────────────────────────────
@st.cache_data
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
            # 保留全部欄位，只重命名 phone 和 score 欄
            dfs[name] = df.rename(columns={phone_col: "Phone", score_col: "Score"})
        else:
            dfs[name] = pd.DataFrame(columns=["Phone", "Score"])
    return dfs


@st.cache_data
def compute_total(dfs):
    # 用 pandas merge 取代逐筆迴圈，速度快數十倍
    merged = None
    for i, (name, df) in enumerate(dfs.items()):
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

/* ══════════════════════════════════════
   GAME UI — Dark Flat Design
   Primary: #003366  Accent: #f28500
══════════════════════════════════════ */
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

/* ══ GLOBAL ══ */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
    background: var(--bg) !important;
    color: var(--text);
}
.stApp {
    background: var(--bg) !important;
    /* Game grid background */
    background-image:
        linear-gradient(rgba(0,51,102,.18) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,51,102,.18) 1px, transparent 1px) !important;
    background-size: 40px 40px !important;
}

/* ══ TOP / BOTTOM TICKER BARS ══ */
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

/* ══ LEFT / RIGHT BRICK COLUMNS ══
   Uses repeating SVG bricks + wood door panels
   Pure CSS, fixed position, pointer-events:none
══════════════════════════════════════════════ */

/* shared column base */
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

/* Brick repeating pattern via inline SVG data URI */
.game-col-left::before,
.game-col-right::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='72' height='40'%3E%3Crect width='72' height='40' fill='%23162030'/%3E%3Crect x='1' y='1' width='34' height='18' rx='1' fill='%231a2d42' stroke='%230a1520' stroke-width='1.5'/%3E%3Crect x='37' y='1' width='34' height='18' rx='1' fill='%231e3250' stroke='%230a1520' stroke-width='1.5'/%3E%3Crect x='1' y='21' width='22' height='18' rx='1' fill='%231e3250' stroke='%230a1520' stroke-width='1.5'/%3E%3Crect x='25' y='21' width='24' height='18' rx='1' fill='%231a2d42' stroke='%230a1520' stroke-width='1.5'/%3E%3Crect x='51' y='21' width='20' height='18' rx='1' fill='%231e3250' stroke='%230a1520' stroke-width='1.5'/%3E%3C/svg%3E");
    background-size: 72px 40px;
    background-repeat: repeat-y;
    opacity: 1;
}

/* Accent stripe (glowing edge toward content) */
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

@keyframes glowpulse {
    from { opacity: .5; }
    to   { opacity: 1; }
}

/* ══ WOOD DOOR PANELS — mid-column decorations ══ */
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
/* small stars above/below door */
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
/* icon badges on brick column */
.col-badge {
    position: fixed;
    width: 36px; height: 36px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    z-index: 102;
    pointer-events: none;
    background: #1e2d40;
    border: 2px solid #f28500;
    box-shadow: 0 0 8px rgba(242,133,0,.35);
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 700px;
    position: relative;
}
#MainMenu, footer, header { visibility: hidden; }
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

/* ══ HERO — Game Header Panel ══ */
.hero {
    background: var(--primary);
    border: 2px solid var(--accent);
    border-radius: var(--radius-lg);
    padding: 2rem 1.5rem 1.6rem;
    text-align: center;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    /* pixelated corner notch effect */
    clip-path: polygon(0 10px,10px 0,calc(100% - 10px) 0,100% 10px,100% calc(100% - 10px),calc(100% - 10px) 100%,10px 100%,0 calc(100% - 10px));
}
/* animated scan line */
.hero::before {
    content:'';
    position:absolute;
    top:-100%; left:0; right:0;
    height:40%;
    background: linear-gradient(to bottom, transparent, rgba(242,133,0,.06), transparent);
    animation: scan 3s linear infinite;
}
/* corner stars */
.hero::after {
    content:'★ ★ ★ ★ ★';
    position:absolute;
    bottom:8px; left:0; right:0;
    text-align:center;
    font-size:.6rem;
    letter-spacing:.8em;
    color:rgba(242,133,0,.4);
}
@keyframes scan {
    0%   { top: -100%; }
    100% { top:  200%; }
}
.hero-badge {
    display: inline-block;
    background: var(--accent);
    color: #fff;
    font-size: .7rem;
    font-weight: 800;
    letter-spacing: .15em;
    padding: .25rem 1rem;
    border-radius: 3px;
    margin-bottom: .9rem;
    text-transform: uppercase;
    /* pixel underline */
    border-bottom: 3px solid rgba(0,0,0,.3);
}
.hero-title {
    font-size: 2rem;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.2;
    margin-bottom: .4rem;
    text-shadow: 0 2px 0 rgba(0,0,0,.4);
}
.hero-title span { color: var(--accent); }
.hero-sub {
    font-size: .82rem;
    color: rgba(255,255,255,.55);
    letter-spacing: .05em;
}

/* ══ INPUT — Game Console Style ══ */
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

/* ══ BUTTON — Pixel Game Button ══ */
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

/* ══ SCORE CARD — XP Panel ══ */
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

/* ══ NOT FOUND ══ */
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

/* ══ SECTION LABEL — Quest Label ══ */
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
</style>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────
# 溫度計 HTML（全用 inline style，避免 Streamlit 壓縮 HTML 導致 class 失效）
# ─────────────────────────────────────────────
def render_thermometer(user_score, prize_counts):
    capped = min(user_score, MAX_SCORE)
    pct = capped / MAX_SCORE * 100
    tube_h = len(PRIZES) * 50

    # Flat Design palette
    ROW_BASE = (
        "display:flex;align-items:center;gap:8px;"
        "border-radius:8px;padding:7px 10px;"
        "margin-bottom:4px;border:1px solid #2a3f58;"
        "background:#1e2d40;"
    )
    ROW_UNLOCKED = (
        "display:flex;align-items:center;gap:8px;"
        "border-radius:8px;padding:7px 10px;"
        "margin-bottom:4px;border:1px solid #f28500;"
        "background:#2a1f0d;"
    )
    DOT_BASE     = "width:9px;height:9px;border-radius:50%;background:#2a3f58;flex-shrink:0;"
    DOT_UNLOCKED = "width:9px;height:9px;border-radius:50%;background:#f28500;box-shadow:0 0 5px #f28500;flex-shrink:0;"
    SCORE_BASE     = "font-family:monospace;font-size:.7rem;color:#506880;min-width:48px;"
    SCORE_UNLOCKED = "font-family:monospace;font-size:.7rem;color:#f28500;min-width:48px;font-weight:700;"
    NAME_BASE      = "font-size:.8rem;font-weight:600;color:#506880;flex:1;"
    NAME_UNLOCKED  = "font-size:.8rem;font-weight:700;color:#e8f0f8;flex:1;"
    COUNT_BASE     = "font-family:monospace;font-size:.67rem;color:#2a3f58;white-space:nowrap;"
    COUNT_UNLOCKED = "font-family:monospace;font-size:.67rem;color:#f28500;white-space:nowrap;"

    prize_rows_html = ""
    for p in PRIZES:
        unlocked = user_score >= p["score"]
        count = prize_counts.get(p["score"], 0)
        if unlocked:
            row_s, dot_s, score_s, name_s, count_s, lock_icon = (
                ROW_UNLOCKED, DOT_UNLOCKED, SCORE_UNLOCKED,
                NAME_UNLOCKED, COUNT_UNLOCKED, "🔓"
            )
        else:
            row_s, dot_s, score_s, name_s, count_s, lock_icon = (
                ROW_BASE, DOT_BASE, SCORE_BASE,
                NAME_BASE, COUNT_BASE, "🔒"
            )
        prize_rows_html += (
            f'<div style="{row_s}">' +
            f'<div style="{dot_s}"></div>' +
            f'<span style="{score_s}">{p["score"]:,}</span>' +
            f'<span style="font-size:1rem;">{p["emoji"]}</span>' +
            f'<span style="{name_s}">{p["name"]}</span>' +
            f'<span style="{count_s}">{count} 人達標</span>' +
            f'<span style="font-size:.75rem;">{lock_icon}</span>' +
            '</div>'
        )

    html = (
        '<div style="display:flex;gap:14px;align-items:flex-start;margin:8px 0;">' +
        # tube column
        '<div style="flex:0 0 38px;display:flex;flex-direction:column;align-items:center;">' +
            f'<div style="width:18px;background:#0f1923;border-radius:9px 9px 0 0;' +
            f'border:2px solid #2a3f58;position:relative;overflow:hidden;height:{tube_h}px;">' +
                f'<div style="position:absolute;bottom:0;left:0;right:0;height:{pct:.1f}%;' +
                f'background:linear-gradient(to top,#f28500,#ffb347);box-shadow:0 0 8px #f28500;"></div>' +
            '</div>' +
            '<div style="width:30px;height:30px;' +
            'background:#f28500;border-radius:50%;' +
            'border:3px solid #2a3f58;margin-top:-2px;flex-shrink:0;' +
            'box-shadow:0 0 10px rgba(242,133,0,.5);"></div>' +
        '</div>' +
        # prize list
        f'<div style="flex:1;">{prize_rows_html}</div>' +
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

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

    # ── 左右磚牆 + 木門裝飾 ──
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

    # 英雄區
    st.markdown("""
<div class="hero">
    <div class="hero-badge">🎂 5th ANNIVERSARY</div>
    <div class="hero-title">EVALUE <span>5歲</span>生日快樂活動</div>
    <div class="hero-sub">輸入手機號碼，立即查詢您的活動積分</div>
</div>
""", unsafe_allow_html=True)

    # 載入資料（cache_data 確保只計算一次）
    try:
        dfs = load_data()
        total_df = compute_total(dfs)
        prize_counts = get_prize_counts(total_df)
        # 預建 phone→score 字典，查詢時 O(1)
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
        phone = st.text_input("", placeholder="例：0912345678", label_visibility="collapsed")
        search = st.button("🔍 查詢積分")

    st.markdown("<hr>", unsafe_allow_html=True)

    if search and phone:
        phone = phone.strip()

        if phone not in total_index:
            st.markdown(f"""
<div class="not-found">
    ⚠️ 找不到手機號碼 <b>{phone}</b> 的資料<br>
    <small>請確認號碼是否正確，或尚未參與活動</small>
</div>
""", unsafe_allow_html=True)
        else:
            user_score = int(total_index[phone])

            # 總分卡片
            st.markdown(f"""
<div class="score-card">
    <div class="score-phone">📱 {phone}</div>
    <div class="score-number">{user_score:,}</div>
    <div class="score-unit">活動總積分</div>
</div>
""", unsafe_allow_html=True)

            # ── 分項積分詳細卡片 ──
            st.markdown('<div class="section-label">📊 分項積分明細</div>', unsafe_allow_html=True)

            def make_card(score, title, emoji, rules_html, progress_html, accent="#f28500"):
                bar_w = min(int(score / 1500 * 100), 100)
                return (
                    # Game card: dark surface + accent border-left
                    f'<div style="background:#1e2d40;border:1px solid #2a3f58;' +
                    f'border-left:3px solid {accent};border-radius:10px;' +
                    f'padding:13px 15px;margin-bottom:8px;">' +
                        # header
                        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">' +
                            f'<div style="display:flex;align-items:center;gap:8px;">' +
                                f'<div style="background:#253547;border-radius:7px;width:30px;height:30px;' +
                                f'display:flex;align-items:center;justify-content:center;font-size:1rem;' +
                                f'border:1px solid #2a3f58;">{emoji}</div>' +
                                f'<span style="font-weight:800;font-size:.9rem;color:#e8f0f8;">{title}</span>' +
                            '</div>' +
                            # score badge
                            f'<div style="background:#0f1923;border:1px solid {accent}44;' +
                            f'border-radius:6px;padding:2px 10px;display:flex;align-items:baseline;gap:3px;">' +
                                f'<span style="font-family:monospace;font-size:.95rem;font-weight:700;color:{accent};">+{score:,}</span>' +
                                f'<span style="font-size:.65rem;color:#506880;">分</span>' +
                            '</div>' +
                        '</div>' +
                        # XP bar
                        '<div style="background:#0f1923;border-radius:3px;height:4px;margin-bottom:9px;">' +
                            f'<div style="background:linear-gradient(90deg,{accent},{accent}99);' +
                            f'border-radius:3px;height:4px;width:{bar_w}%;"></div>' +
                        '</div>' +
                        # rules
                        f'<div style="font-size:.72rem;color:#506880;line-height:1.8;margin-bottom:7px;' +
                        f'padding-bottom:7px;border-bottom:1px solid #253547;">{rules_html}</div>' +
                        # progress
                        f'<div style="font-size:.8rem;color:#8aaac8;">{progress_html}</div>' +
                    '</div>'
                )

            cards_html = ""

            # 🔋 充電度數
            deg_row = dfs["Degree"][dfs["Degree"]["Phone"] == phone]
            dc = float(deg_row["TotalDC"].iloc[0]) if not deg_row.empty and "TotalDC" in deg_row.columns else 0.0
            ac = float(deg_row["TotalAC"].iloc[0]) if not deg_row.empty and "TotalAC" in deg_row.columns else 0.0
            deg_score = int(score_index["Degree"].get(phone, 0))
            cards_html += make_card(
                deg_score, "充電度數", "🔋",
                "DC 充電：每 1 度 = 1 分 ／ AC 充電：每 10 度 = 1 分",
                f"DC <b style='color:#f28500;'>{dc:,.2f} 度</b>　／　AC <b style='color:#f28500;'>{ac:,.2f} 度</b>"
            )

            # 🚗 車輛綁定
            car_row = dfs["Car"][dfs["Car"]["Phone"] == phone]
            car_bound = False
            if not car_row.empty and "CarCount" in car_row.columns:
                car_bound = str(car_row["CarCount"].iloc[0]).strip().lower() == "true"
            car_score = int(score_index["Car"].get(phone, 0))
            bound_tag = (
                '<span style="background:#0d2e1f;color:#00c9a7;border:1px solid #00c9a744;' +
                'border-radius:5px;padding:2px 10px;font-weight:700;">✅ 已完成綁定</span>'
                if car_bound else
                '<span style="background:#2e1a0d;color:#f28500;border:1px solid #f2850044;' +
                'border-radius:5px;padding:2px 10px;font-weight:700;">⚠️ 尚未綁定</span>'
            )
            cards_html += make_card(
                car_score, "車輛綁定", "🚗",
                "完成「隨插即充」功能綁定，立即獲得 100 分",
                f"綁定狀態：{bound_tag}"
            )

            # 📍 拜訪站點
            sta_row = dfs["Station"][dfs["Station"]["Phone"] == phone]
            special_cnt = int(sta_row["SpecialStationCount"].iloc[0]) if not sta_row.empty and "SpecialStationCount" in sta_row.columns else 0
            normal_cnt  = int(sta_row["NormalStationCount"].iloc[0])  if not sta_row.empty and "NormalStationCount" in sta_row.columns else 0
            sta_score = int(score_index["Station"].get(phone, 0))
            cards_html += make_card(
                sta_score, "拜訪站點", "📍",
                "一般站點：每站 10 分 ／ 精選站點：每站 30 分（基本 10 + 額外 20）",
                f"精選站點 <b style='color:#f28500;'>{special_cnt} 站</b>　／　一般站點 <b style='color:#00c9a7;'>{normal_cnt} 站</b>　共 <b style='color:#e8f0f8;font-size:.9rem;'>{special_cnt+normal_cnt} 站</b>",
                accent="#ffd700"
            )

            # 🔢 充電次數
            cnt_row = dfs["Count"][dfs["Count"]["Phone"] == phone]
            charge_cnt = int(cnt_row["PhoneCount"].iloc[0]) if not cnt_row.empty and "PhoneCount" in cnt_row.columns else 0
            cnt_score = int(score_index["Count"].get(phone, 0))
            next_milestone = ((charge_cnt // 20) + 1) * 20
            cnt_left = next_milestone - charge_cnt
            cards_html += make_card(
                cnt_score, "充電次數", "🔢",
                "每累積 20 次充電 = 50 分",
                f"目前充電 <b style='color:#00c9a7;'>{charge_cnt} 次</b>　距下一里程碑還差 <b style='color:#f28500;'>{cnt_left} 次</b>（第 {next_milestone} 次）"
            )

            # 💰 儲值金額
            sav_row = dfs["Save"][dfs["Save"]["Phone"] == phone]
            total_amt = int(sav_row["TotalAmount"].iloc[0]) if not sav_row.empty and "TotalAmount" in sav_row.columns else 0
            sav_score = int(score_index["Save"].get(phone, 0))
            cards_html += make_card(
                sav_score, "儲值金額", "💰",
                "每儲值 1,000 元 = 10 分",
                f"累積儲值 <b style='color:#f28500;'>NT$ {total_amt:,}</b>"
            )

            # 🌟 特殊活動
            sp_score = int(score_index.get("Special", {}).get(phone, 0))
            if sp_score > 0:
                sp_row = dfs["Special"][dfs["Special"]["Phone"] == phone]
                mark = sp_row["Mark"].iloc[0] if not sp_row.empty and "Mark" in sp_row.columns else "特殊活動"
                cards_html += make_card(
                    sp_score, "特殊活動", "🌟",
                    "參與特殊活動獲得額外積分",
                    f"活動名稱：<b style='color:#f28500;'>{mark}</b>",
                    accent="#f28500"
                )

            st.markdown(cards_html, unsafe_allow_html=True)

            # 溫度計 + 獎品
            st.markdown("#### 🌡️ 積分進度 & 獎品解鎖")
            render_thermometer(user_score, prize_counts)

    elif search and not phone:
        st.warning("請輸入手機號碼")


if __name__ == "__main__":
    main()
