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
            keep = [phone_col, score_col]
            if "Mark" in df.columns:
                keep.append("Mark")
            dfs[name] = df[keep].rename(
                columns={phone_col: "Phone", score_col: "Score"}
            )
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
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Space+Mono:wght@400;700&display=swap');

/* ── 全域 ── */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
    background: #0a0e1a;
    color: #e8f4fd;
}
.stApp { background: #0a0e1a; }

/* ── 標題區 ── */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 50%, #ff6b35 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: .3rem;
}
.hero-sub {
    font-family: 'Space Mono', monospace;
    font-size: .85rem;
    color: #7ec8e3;
    letter-spacing: .12em;
}
.birthday-badge {
    display: inline-block;
    background: linear-gradient(135deg,#7b2ff7,#ff6b35);
    color: white;
    font-weight: 700;
    font-size: .75rem;
    padding: .25rem .75rem;
    border-radius: 20px;
    margin-bottom: 1rem;
    letter-spacing: .08em;
}

/* ── 查詢輸入 ── */
.stTextInput > div > div > input {
    background: #111827 !important;
    border: 2px solid #1e3a5f !important;
    border-radius: 12px !important;
    color: #e8f4fd !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 1.1rem !important;
    padding: .7rem 1rem !important;
    text-align: center;
    letter-spacing: .15em;
}
.stTextInput > div > div > input:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 0 3px rgba(0,212,255,.2) !important;
}
.stButton > button {
    background: linear-gradient(135deg,#00d4ff,#7b2ff7) !important;
    color: white !important;
    font-weight: 700 !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: .6rem 2rem !important;
    width: 100%;
    transition: opacity .2s;
}
.stButton > button:hover { opacity: .88 !important; }

/* ── 總分卡片 ── */
.score-card {
    background: linear-gradient(135deg,#111827,#1a2540);
    border: 1px solid #1e3a5f;
    border-radius: 20px;
    padding: 1.8rem;
    text-align: center;
    margin: 1.2rem 0;
    box-shadow: 0 4px 30px rgba(0,212,255,.1);
}
.score-number {
    font-family: 'Space Mono', monospace;
    font-size: 3.2rem;
    font-weight: 700;
    background: linear-gradient(135deg,#00d4ff,#7b2ff7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.score-label { font-size: .85rem; color: #7ec8e3; letter-spacing: .1em; }

/* ── 溫度計容器 ── */
.thermo-wrap {
    display: flex;
    gap: 1.5rem;
    align-items: flex-start;
    margin: 1rem 0;
}

/* ── 溫度計管 ── */
.thermo-tube {
    flex: 0 0 44px;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.thermo-bg {
    width: 22px;
    background: #1a2540;
    border-radius: 11px 11px 0 0;
    border: 2px solid #1e3a5f;
    position: relative;
    overflow: hidden;
}
.thermo-fill {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    border-radius: 0;
    background: linear-gradient(to top, #ff6b35, #7b2ff7, #00d4ff);
    transition: height .8s ease;
}
.thermo-bulb {
    width: 36px; height: 36px;
    background: radial-gradient(circle at 40% 40%, #ff6b35, #c0392b);
    border-radius: 50%;
    border: 3px solid #1e3a5f;
    margin-top: -2px;
    flex-shrink: 0;
    box-shadow: 0 0 12px rgba(255,107,53,.5);
}

/* ── 獎品列表 ── */
.prize-list { flex: 1; display: flex; flex-direction: column; gap: .5rem; }

.prize-row {
    display: flex;
    align-items: center;
    gap: .6rem;
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: .45rem .75rem;
    transition: all .3s;
}
.prize-row.unlocked {
    background: linear-gradient(90deg,rgba(0,212,255,.08),rgba(123,47,247,.08));
    border-color: #00d4ff;
    box-shadow: 0 0 10px rgba(0,212,255,.15);
}
.prize-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: #1e3a5f;
    flex-shrink: 0;
}
.prize-row.unlocked .prize-dot {
    background: #00d4ff;
    box-shadow: 0 0 6px #00d4ff;
}
.prize-score {
    font-family: 'Space Mono', monospace;
    font-size: .72rem;
    color: #4a7fa8;
    min-width: 44px;
}
.prize-row.unlocked .prize-score { color: #00d4ff; }
.prize-name { font-size: .82rem; font-weight: 700; color: #7ec8e3; flex: 1; }
.prize-row.unlocked .prize-name { color: #e8f4fd; }
.prize-emoji { font-size: 1rem; }
.prize-count {
    font-family: 'Space Mono', monospace;
    font-size: .68rem;
    color: #4a7fa8;
    white-space: nowrap;
}
.prize-row.unlocked .prize-count { color: #7ec8e3; }
.lock-icon { font-size: .75rem; color: #2a4a6a; }
.prize-row.unlocked .lock-icon { display: none; }

/* ── 分項細節 ── */
.detail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(145px,1fr));
    gap: .6rem;
    margin: .8rem 0;
}
.detail-card {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: .7rem .8rem;
    text-align: center;
}
.detail-val {
    font-family: 'Space Mono', monospace;
    font-size: 1.25rem;
    font-weight: 700;
    color: #00d4ff;
}
.detail-lbl { font-size: .72rem; color: #4a7fa8; margin-top: .15rem; }

/* ── 找不到 ── */
.not-found {
    text-align: center;
    padding: 2rem;
    color: #4a7fa8;
    font-family: 'Space Mono', monospace;
    font-size: .9rem;
}

/* ── 分隔線 ── */
hr { border-color: #1e3a5f !important; }

/* 隱藏 Streamlit 預設元素 */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; max-width: 680px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 溫度計 HTML（全用 inline style，避免 Streamlit 壓縮 HTML 導致 class 失效）
# ─────────────────────────────────────────────
def render_thermometer(user_score, prize_counts):
    capped = min(user_score, MAX_SCORE)
    pct = capped / MAX_SCORE * 100

    tube_h = len(PRIZES) * 46

    ROW_BASE = (
        "display:flex;align-items:center;gap:8px;"
        "border-radius:10px;padding:7px 12px;"
        "margin-bottom:6px;border:1px solid #1e3a5f;"
        "background:#111827;"
    )
    ROW_UNLOCKED = (
        "display:flex;align-items:center;gap:8px;"
        "border-radius:10px;padding:7px 12px;"
        "margin-bottom:6px;border:1px solid #00d4ff;"
        "background:linear-gradient(90deg,rgba(0,212,255,.08),rgba(123,47,247,.08));"
        "box-shadow:0 0 10px rgba(0,212,255,.15);"
    )
    DOT_BASE     = "width:10px;height:10px;border-radius:50%;background:#1e3a5f;flex-shrink:0;"
    DOT_UNLOCKED = "width:10px;height:10px;border-radius:50%;background:#00d4ff;box-shadow:0 0 6px #00d4ff;flex-shrink:0;"
    SCORE_BASE     = "font-family:monospace;font-size:.72rem;color:#4a7fa8;min-width:44px;"
    SCORE_UNLOCKED = "font-family:monospace;font-size:.72rem;color:#00d4ff;min-width:44px;"
    NAME_BASE      = "font-size:.82rem;font-weight:700;color:#7ec8e3;flex:1;"
    NAME_UNLOCKED  = "font-size:.82rem;font-weight:700;color:#e8f4fd;flex:1;"
    COUNT_BASE     = "font-family:monospace;font-size:.68rem;color:#4a7fa8;white-space:nowrap;"
    COUNT_UNLOCKED = "font-family:monospace;font-size:.68rem;color:#7ec8e3;white-space:nowrap;"

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
        '<div style="display:flex;gap:20px;align-items:flex-start;margin:12px 0;">' +
        '<div style="flex:0 0 44px;display:flex;flex-direction:column;align-items:center;">' +
        f'<div style="width:22px;background:#1a2540;border-radius:11px 11px 0 0;' +
        f'border:2px solid #1e3a5f;position:relative;overflow:hidden;height:{tube_h}px;">' +
        f'<div style="position:absolute;bottom:0;left:0;right:0;height:{pct:.1f}%;' +
        f'background:linear-gradient(to top,#ff6b35,#7b2ff7,#00d4ff);"></div>' +
        '</div>' +
        '<div style="width:36px;height:36px;' +
        'background:radial-gradient(circle at 40% 40%,#ff6b35,#c0392b);' +
        'border-radius:50%;border:3px solid #1e3a5f;margin-top:-2px;flex-shrink:0;' +
        'box-shadow:0 0 12px rgba(255,107,53,.5);"></div>' +
        '</div>' +
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

    # 英雄區
    st.markdown("""
<div class="hero">
    <div class="birthday-badge">🎂 5th ANNIVERSARY</div>
    <div class="hero-title">EVALUE<br>5歲生日快樂活動</div>
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
    <div class="score-label">📱 {phone}</div>
    <div class="score-number">{user_score:,}</div>
    <div class="score-label">活動總積分</div>
</div>
""", unsafe_allow_html=True)

            # 分項積分（O(1) 字典查詢）
            detail_items = [
                ("⚡ 充電度數", "Degree"),
                ("🚗 車輛綁定", "Car"),
                ("📍 拜訪站點", "Station"),
                ("🔢 充電次數", "Count"),
                ("💰 儲值金額", "Save"),
                ("🌟 特殊活動", "Special"),
            ]

            detail_html = '<div class="detail-grid">'
            for label, name in detail_items:
                val = int(score_index[name].get(phone, 0))
                detail_html += f"""
<div class="detail-card">
    <div class="detail-val">{val:,}</div>
    <div class="detail-lbl">{label}</div>
</div>"""
            detail_html += "</div>"
            st.markdown(detail_html, unsafe_allow_html=True)

            # 特殊活動標記
            special_df = dfs.get("Special", pd.DataFrame())
            if not special_df.empty and phone in score_index.get("Special", {}):
                sp_row = special_df[special_df["Phone"] == phone]
                if not sp_row.empty and "Mark" in sp_row.columns:
                    mark = sp_row["Mark"].iloc[0]
                    sp_score = int(score_index["Special"].get(phone, 0))
                    st.markdown(
                        f'<div style="background:linear-gradient(90deg,rgba(255,215,0,.1),rgba(255,107,53,.1));' +
                        f'border:1px solid rgba(255,215,0,.4);border-radius:12px;padding:10px 16px;' +
                        f'margin:8px 0;display:flex;align-items:center;gap:10px;">' +
                        f'<span style="font-size:1.3rem;">🌟</span>' +
                        f'<div><div style="font-weight:700;color:#ffd700;font-size:.9rem;">{mark}</div>' +
                        f'<div style="font-size:.75rem;color:#a07830;">特殊活動 +{sp_score} 分</div></div>' +
                        f'</div>',
                        unsafe_allow_html=True
                    )

            # 溫度計 + 獎品
            st.markdown("#### 🌡️ 積分進度 & 獎品解鎖")
            render_thermometer(user_score, prize_counts)

    elif search and not phone:
        st.warning("請輸入手機號碼")


if __name__ == "__main__":
    main()
