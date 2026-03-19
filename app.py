import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="EVALUE 5歲生日快樂活動",
    page_icon="🎂",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── 獎項門檻設定 ──────────────────────────────────────────
REWARDS = [
    {"score": 10000, "label": "EVALUE 萬元點數",          "icon": "👑"},
    {"score": 5000,  "label": "2026 3天免費充電方案",      "icon": "⚡"},
    {"score": 2500,  "label": "EVALUE 500點",             "icon": "🎁"},
    {"score": 2000,  "label": "2026 1天免費充電方案",      "icon": "🔋"},
    {"score": 1500,  "label": "DC 快充 50% 回饋卷 x 3",   "icon": "⚡"},
    {"score": 1000,  "label": "EVALUE 500點",             "icon": "🎁"},
    {"score": 750,   "label": "DC 快充 50% 回饋卷 x 1",   "icon": "⚡"},
    {"score": 500,   "label": "DC 快充 25% 回饋卷 x 3",   "icon": "🌟"},
    {"score": 300,   "label": "EVALUE 50點",              "icon": "🎀"},
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@st.cache_data
def load_all_data():
    def load(fname):
        path = os.path.join(DATA_DIR, fname)
        if os.path.exists(path):
            return pd.read_csv(path, dtype={"Phone": str})
        return pd.DataFrame()

    degree  = load("Degree.csv")
    car     = load("Car.csv")
    station = load("Station.csv")
    count   = load("Count.csv")
    save    = load("Save.csv")
    special = load("Special.csv")
    return degree, car, station, count, save, special

def compute_total_score(phone: str, degree, car, station, count, save, special) -> int:
    total = 0
    for df, col in [
        (degree,  "TotalScore"),
        (car,     "CarTotalScore"),
        (station, "StationScore"),
        (count,   "CountScore"),
        (save,    "SaveScore"),
        (special, "SpecialScore"),
    ]:
        if df.empty or "Phone" not in df.columns:
            continue
        row = df[df["Phone"] == phone]
        if not row.empty:
            total += int(row[col].values[0])
    return total

def get_special_marks(phone: str, special) -> list[str]:
    """取得該手機的特殊活動標記清單"""
    if special.empty or "Phone" not in special.columns:
        return []
    rows = special[special["Phone"] == phone]
    if rows.empty:
        return []
    return rows["Mark"].tolist()

def count_winners(degree, car, station, count, save, special) -> dict[int, int]:
    """回傳每個門檻有多少人達標"""
    all_phones = set()
    for df in [degree, car, station, count, save, special]:
        if not df.empty and "Phone" in df.columns:
            all_phones.update(df["Phone"].tolist())

    scores = {}
    for ph in all_phones:
        scores[ph] = compute_total_score(ph, degree, car, station, count, save, special)

    winners = {}
    for r in REWARDS:
        winners[r["score"]] = sum(1 for s in scores.values() if s >= r["score"])
    return winners

# ── CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Noto+Sans+TC:wght@400;700&display=swap');

:root {
    --evalue-green:  #00ff88;
    --evalue-teal:   #00e5cc;
    --evalue-dark:   #0a0f1e;
    --evalue-card:   #111827;
    --evalue-border: #1e293b;
    --evalue-glow:   0 0 20px rgba(0,255,136,0.4);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--evalue-dark) !important;
    color: #e2e8f0 !important;
}

[data-testid="stHeader"] { background: transparent !important; }

.main-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.6rem, 5vw, 2.8rem);
    font-weight: 900;
    text-align: center;
    background: linear-gradient(135deg, var(--evalue-green), var(--evalue-teal), #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.08em;
    margin-bottom: 0.2rem;
    text-shadow: none;
    filter: drop-shadow(0 0 12px rgba(0,255,136,0.5));
}
.sub-title {
    font-family: 'Noto Sans TC', sans-serif;
    text-align: center;
    color: #94a3b8;
    font-size: 1rem;
    margin-bottom: 2rem;
    letter-spacing: 0.15em;
}
.birthday-row {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    font-size: 1.6rem;
    margin-bottom: 2.5rem;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-6px); }
}

/* score card */
.score-card {
    background: linear-gradient(135deg, #0f172a, #1e1b4b);
    border: 1px solid var(--evalue-green);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    box-shadow: var(--evalue-glow), inset 0 0 40px rgba(0,255,136,0.03);
    margin: 1.5rem 0;
}
.score-number {
    font-family: 'Orbitron', monospace;
    font-size: clamp(3rem, 10vw, 5rem);
    font-weight: 900;
    background: linear-gradient(90deg, var(--evalue-green), var(--evalue-teal));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    filter: drop-shadow(0 0 16px rgba(0,255,136,0.7));
}
.score-label {
    font-family: 'Noto Sans TC', sans-serif;
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 0.4rem;
    letter-spacing: 0.2em;
}

/* thermometer + rewards */
.thermo-section {
    display: flex;
    gap: 1.5rem;
    margin-top: 1.5rem;
    align-items: flex-start;
}
.thermo-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 48px;
    flex-shrink: 0;
}
.thermo-outer {
    position: relative;
    width: 24px;
    border-radius: 12px;
    background: #1e293b;
    border: 2px solid #334155;
    overflow: hidden;
}
.thermo-fill {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    border-radius: 12px;
    background: linear-gradient(to top, #00ff88, #00e5cc, #7c3aed);
    transition: height 1s cubic-bezier(.4,0,.2,1);
    box-shadow: 0 0 12px rgba(0,255,136,0.6);
}
.thermo-bulb {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #00ff88, #00a86b);
    border: 2px solid #334155;
    box-shadow: 0 0 14px rgba(0,255,136,0.8);
    margin-top: -2px;
    flex-shrink: 0;
}

/* reward list */
.rewards-list {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.reward-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 1rem;
    border-radius: 10px;
    border: 1px solid #1e293b;
    background: #111827;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.reward-item.unlocked {
    border-color: var(--evalue-green);
    background: linear-gradient(90deg, rgba(0,255,136,0.08), rgba(0,229,204,0.05));
    box-shadow: 0 0 10px rgba(0,255,136,0.2);
}
.reward-item.unlocked::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(to bottom, var(--evalue-green), var(--evalue-teal));
}
.reward-icon { font-size: 1.2rem; width: 1.5rem; text-align: center; }
.reward-score {
    font-family: 'Orbitron', monospace;
    font-size: 0.75rem;
    color: #64748b;
    min-width: 44px;
}
.reward-item.unlocked .reward-score { color: var(--evalue-green); }
.reward-label {
    font-family: 'Noto Sans TC', sans-serif;
    font-size: 0.85rem;
    color: #94a3b8;
    flex: 1;
}
.reward-item.unlocked .reward-label { color: #e2e8f0; font-weight: 700; }
.reward-lock { font-size: 0.9rem; opacity: 0.3; }
.reward-item.unlocked .reward-lock { opacity: 0; }
.winner-badge {
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    padding: 2px 7px;
    border-radius: 20px;
    background: rgba(0,255,136,0.15);
    color: var(--evalue-green);
    border: 1px solid rgba(0,255,136,0.3);
    white-space: nowrap;
}
.winner-badge.locked {
    background: rgba(255,255,255,0.05);
    color: #475569;
    border-color: #334155;
}

/* special activity badge */
.special-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
    margin-top: 0.75rem;
}
.special-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    background: linear-gradient(135deg, rgba(251,191,36,0.15), rgba(245,158,11,0.1));
    border: 1px solid rgba(251,191,36,0.5);
    color: #fbbf24;
    font-family: 'Noto Sans TC', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    box-shadow: 0 0 10px rgba(251,191,36,0.2);
}

/* input styling */
.stTextInput input {
    background: #111827 !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    font-family: 'Noto Sans TC', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.7rem 1rem !important;
}
.stTextInput input:focus {
    border-color: var(--evalue-green) !important;
    box-shadow: 0 0 0 2px rgba(0,255,136,0.2) !important;
}
.stButton button {
    background: linear-gradient(135deg, var(--evalue-green), var(--evalue-teal)) !important;
    color: #0a0f1e !important;
    font-family: 'Orbitron', monospace !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2rem !important;
    letter-spacing: 0.1em !important;
    transition: all 0.2s !important;
}
.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(0,255,136,0.4) !important;
}
.not-found {
    text-align: center;
    color: #ef4444;
    font-family: 'Noto Sans TC', sans-serif;
    padding: 1rem;
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── 標題 ─────────────────────────────────────────────────
st.markdown('<div class="main-title">EVALUE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">⚡ 5歲生日快樂活動 ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="birthday-row">🎂🎉🎁🎊🎈</div>', unsafe_allow_html=True)

# ── 載入資料 ──────────────────────────────────────────────
degree, car, station, count, save, special = load_all_data()
winners_map = count_winners(degree, car, station, count, save, special)

# ── 查詢框 ────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    phone_input = st.text_input("", placeholder="請輸入您的手機號碼", label_visibility="collapsed")
with col2:
    query_btn = st.button("查詢積分", use_container_width=True)

MAX_SCORE = REWARDS[0]["score"]  # 10000

if query_btn and phone_input:
    phone = phone_input.strip()
    total = compute_total_score(phone, degree, car, station, count, save, special)

    # 確認號碼存在
    found = False
    for df in [degree, car, station, count, save, special]:
        if not df.empty and "Phone" in df.columns and phone in df["Phone"].values:
            found = True
            break

    if not found:
        st.markdown('<div class="not-found">❌ 查無此手機號碼，請確認後再試</div>', unsafe_allow_html=True)
    else:
        # ── 特殊活動標章 ──────────────────────────────────
        marks = get_special_marks(phone, special)
        special_html = ""
        if marks:
            badges = "".join(f'<span class="special-badge">⭐ {m}</span>' for m in marks)
            special_html = f'<div class="special-row">{badges}</div>'

        # ── 積分卡 ────────────────────────────────────────
        st.markdown(f"""
        <div class="score-card">
            <div class="score-number">{total:,}</div>
            <div class="score-label">累積積分 TOTAL SCORE</div>
            {special_html}
        </div>
        """, unsafe_allow_html=True)

        # ── 溫度計 + 獎項 ──────────────────────────────────
        pct = min(total / MAX_SCORE * 100, 100)
        thermo_h = 420  # px

        rewards_html = ""
        for r in REWARDS:
            unlocked = total >= r["score"]
            cls = "unlocked" if unlocked else ""
            lock_icon = "✅" if unlocked else "🔒"
            w = winners_map.get(r["score"], 0)
            badge_cls = "" if unlocked else "locked"
            rewards_html += f"""
            <div class="reward-item {cls}">
                <span class="reward-icon">{r['icon']}</span>
                <span class="reward-score">{r['score']:,}</span>
                <span class="reward-label">{r['label']}</span>
                <span class="winner-badge {badge_cls}">{w} 人達標</span>
                <span class="reward-lock">{lock_icon}</span>
            </div>"""

        fill_h = int(thermo_h * pct / 100)

        st.markdown(f"""
        <div class="thermo-section">
            <div class="thermo-wrap">
                <div class="thermo-outer" style="height:{thermo_h}px;">
                    <div class="thermo-fill" style="height:{fill_h}px;"></div>
                </div>
                <div class="thermo-bulb"></div>
            </div>
            <div class="rewards-list">
                {rewards_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

elif query_btn and not phone_input:
    st.warning("請輸入手機號碼")

# ── footer ────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;color:#334155;font-size:0.75rem;font-family:'Noto Sans TC',sans-serif;letter-spacing:0.1em;">
© 2026 EVALUE · 5th Anniversary Event
</div>
""", unsafe_allow_html=True)
