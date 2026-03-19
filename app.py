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
   CSS VARIABLES — Flat Design × Game
══════════════════════════════════════ */
:root {
    --primary:      #003366;
    --primary-mid:  #004080;
    --primary-lt:   #e8f0f8;
    --accent:       #f28500;
    --accent-lt:    #fff3e0;
    --bg:           #f0f4f8;
    --surface:      #ffffff;
    --surface2:     #f7fafc;
    --border:       #dbe4ee;
    --text:         #1a2a3a;
    --text-mid:     #4a6080;
    --text-lt:      #8a9bb0;
    --success:      #00a86b;
    --warn:         #e05c00;
    --radius:       12px;
    --radius-lg:    16px;
}

/* ══ 全域 ══ */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
    background: var(--bg) !important;
    color: var(--text);
}
.stApp { background: var(--bg) !important; }
.block-container {
    padding-top: .5rem !important;
    max-width: 700px;
}
#MainMenu, footer, header { visibility: hidden; }
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

/* ══ HERO ══ */
.hero {
    background: var(--primary);
    border-radius: var(--radius-lg);
    padding: 2.2rem 1.5rem 1.8rem;
    text-align: center;
    margin-bottom: 1.2rem;
}
.hero-badge {
    display: inline-block;
    background: var(--accent);
    color: #fff;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .1em;
    padding: .2rem .9rem;
    border-radius: 20px;
    margin-bottom: .9rem;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.2;
    margin-bottom: .4rem;
}
.hero-title span { color: var(--accent); }
.hero-sub {
    font-size: .85rem;
    color: rgba(255,255,255,.65);
    letter-spacing: .05em;
}

/* ══ INPUT ══ */
.stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 2px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 1rem !important;
    padding: .65rem 1rem !important;
    text-align: center;
    letter-spacing: .12em;
    box-shadow: none !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(0,51,102,.12) !important;
}

/* ══ BUTTON ══ */
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    font-weight: 800 !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: .65rem 2rem !important;
    width: 100%;
    letter-spacing: .04em;
    transition: background .15s, transform .1s;
}
.stButton > button:hover {
    background: #d97700 !important;
    transform: translateY(-1px);
}
.stButton > button:active { transform: translateY(0); }

/* ══ SCORE CARD ══ */
.score-card {
    background: var(--primary);
    border-radius: var(--radius-lg);
    padding: 1.6rem 1.5rem;
    text-align: center;
    margin: .8rem 0;
    position: relative;
    overflow: hidden;
}
.score-card::before {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 120px; height: 120px;
    background: rgba(242,133,0,.15);
    border-radius: 50%;
}
.score-card::after {
    content: '';
    position: absolute;
    bottom: -40px; left: -20px;
    width: 100px; height: 100px;
    background: rgba(255,255,255,.04);
    border-radius: 50%;
}
.score-phone {
    font-size: .8rem;
    color: rgba(255,255,255,.55);
    letter-spacing: .1em;
    margin-bottom: .3rem;
}
.score-number {
    font-family: 'Space Mono', monospace;
    font-size: 3.4rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.score-unit {
    font-size: .82rem;
    color: rgba(255,255,255,.6);
    margin-top: .25rem;
    letter-spacing: .08em;
}

/* ══ NOT FOUND ══ */
.not-found {
    background: var(--surface);
    border: 2px dashed var(--border);
    border-radius: var(--radius-lg);
    padding: 2rem;
    text-align: center;
    color: var(--text-lt);
    font-size: .9rem;
    margin: 1rem 0;
}

/* ══ SECTION LABEL ══ */
.section-label {
    font-size: .72rem;
    font-weight: 700;
    color: var(--text-lt);
    letter-spacing: .12em;
    text-transform: uppercase;
    margin: 1.2rem 0 .5rem;
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
        "border-radius:10px;padding:8px 12px;"
        "margin-bottom:5px;border:1px solid #dbe4ee;"
        "background:#ffffff;"
    )
    ROW_UNLOCKED = (
        "display:flex;align-items:center;gap:8px;"
        "border-radius:10px;padding:8px 12px;"
        "margin-bottom:5px;border:1px solid #f28500;"
        "background:#fff8f0;"
    )
    DOT_BASE     = "width:10px;height:10px;border-radius:50%;background:#dbe4ee;flex-shrink:0;"
    DOT_UNLOCKED = "width:10px;height:10px;border-radius:50%;background:#f28500;flex-shrink:0;"
    SCORE_BASE     = "font-family:monospace;font-size:.72rem;color:#8a9bb0;min-width:48px;"
    SCORE_UNLOCKED = "font-family:monospace;font-size:.72rem;color:#b36200;min-width:48px;font-weight:700;"
    NAME_BASE      = "font-size:.82rem;font-weight:600;color:#8a9bb0;flex:1;"
    NAME_UNLOCKED  = "font-size:.82rem;font-weight:700;color:#003366;flex:1;"
    COUNT_BASE     = "font-family:monospace;font-size:.68rem;color:#b0bec5;white-space:nowrap;"
    COUNT_UNLOCKED = "font-family:monospace;font-size:.68rem;color:#f28500;white-space:nowrap;"

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
        '<div style="display:flex;gap:16px;align-items:flex-start;margin:8px 0;">' +
        # tube column
        '<div style="flex:0 0 40px;display:flex;flex-direction:column;align-items:center;">' +
            f'<div style="width:20px;background:#f0f4f8;border-radius:10px 10px 0 0;' +
            f'border:2px solid #dbe4ee;position:relative;overflow:hidden;height:{tube_h}px;">' +
                f'<div style="position:absolute;bottom:0;left:0;right:0;height:{pct:.1f}%;' +
                f'background:linear-gradient(to top,#f28500,#ffb347);"></div>' +
            '</div>' +
            '<div style="width:32px;height:32px;' +
            'background:#f28500;border-radius:50%;' +
            'border:3px solid #dbe4ee;margin-top:-2px;flex-shrink:0;"></div>' +
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
                # Flat Design card: white surface, primary title, accent score
                bar_w = min(int(score / 1500 * 100), 100)  # rough visual bar
                return (
                    '<div style="background:#fff;border:1px solid #dbe4ee;border-radius:12px;' +
                    'padding:14px 16px;margin-bottom:10px;">' +
                        # header row
                        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">' +
                            f'<div style="display:flex;align-items:center;gap:8px;">' +
                                f'<div style="background:#e8f0f8;border-radius:8px;width:32px;height:32px;' +
                                f'display:flex;align-items:center;justify-content:center;font-size:1.1rem;">{emoji}</div>' +
                                f'<span style="font-weight:800;font-size:.92rem;color:#003366;">{title}</span>' +
                            '</div>' +
                            f'<div style="background:#fff3e0;border-radius:8px;padding:3px 10px;">' +
                                f'<span style="font-family:monospace;font-size:1rem;font-weight:700;color:{accent};">+{score:,}</span>' +
                                f'<span style="font-size:.7rem;color:#b36200;"> 分</span>' +
                            '</div>' +
                        '</div>' +
                        # progress bar
                        '<div style="background:#f0f4f8;border-radius:4px;height:5px;margin-bottom:10px;">' +
                            f'<div style="background:{accent};border-radius:4px;height:5px;width:{bar_w}%;transition:width .6s;"></div>' +
                        '</div>' +
                        # rules
                        f'<div style="font-size:.73rem;color:#6a80a0;line-height:1.8;margin-bottom:8px;padding-bottom:8px;border-bottom:1px solid #eef1f5;">{rules_html}</div>' +
                        # progress detail
                        f'<div style="font-size:.8rem;color:#2a4a6a;">{progress_html}</div>' +
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
                f"DC <b style='color:#003366;'>{dc:,.2f} 度</b>　／　AC <b style='color:#003366;'>{ac:,.2f} 度</b>"
            )

            # 🚗 車輛綁定
            car_row = dfs["Car"][dfs["Car"]["Phone"] == phone]
            car_bound = False
            if not car_row.empty and "CarCount" in car_row.columns:
                car_bound = str(car_row["CarCount"].iloc[0]).strip().lower() == "true"
            car_score = int(score_index["Car"].get(phone, 0))
            bound_tag = (
                '<span style="background:#e6f4ed;color:#00a86b;border:1px solid #00a86b44;' +
                'border-radius:6px;padding:2px 10px;font-weight:700;">✅ 已完成綁定</span>'
                if car_bound else
                '<span style="background:#fff0e6;color:#e05c00;border:1px solid #e05c0044;' +
                'border-radius:6px;padding:2px 10px;font-weight:700;">⚠️ 尚未綁定</span>'
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
                f"精選站點 <b style='color:#f28500;'>{special_cnt} 站</b>　／　一般站點 <b style='color:#003366;'>{normal_cnt} 站</b>　共 <b style='color:#1a2a3a;font-size:.9rem;'>{special_cnt+normal_cnt} 站</b>",
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
                f"目前充電 <b style='color:#003366;'>{charge_cnt} 次</b>　距下一里程碑還差 <b style='color:#f28500;'>{cnt_left} 次</b>（第 {next_milestone} 次）"
            )

            # 💰 儲值金額
            sav_row = dfs["Save"][dfs["Save"]["Phone"] == phone]
            total_amt = int(sav_row["TotalAmount"].iloc[0]) if not sav_row.empty and "TotalAmount" in sav_row.columns else 0
            sav_score = int(score_index["Save"].get(phone, 0))
            cards_html += make_card(
                sav_score, "儲值金額", "💰",
                "每儲值 1,000 元 = 10 分",
                f"累積儲值 <b style='color:#003366;'>NT$ {total_amt:,}</b>"
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
