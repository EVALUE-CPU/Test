import streamlit as st
import os
import pandas as pd
import json

st.set_page_config(
    page_title="Charging Points Event",
    page_icon="zap",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """讀取五個 CSV，合併計算每人總積分，回傳 all_data dict 與 leaderboard list"""
    base = os.path.dirname(__file__)

    degree  = pd.read_csv(os.path.join(base, "Degree.csv"))
    count   = pd.read_csv(os.path.join(base, "Count.csv"))
    car     = pd.read_csv(os.path.join(base, "Car.csv"))
    save    = pd.read_csv(os.path.join(base, "Save.csv"))
    station = pd.read_csv(os.path.join(base, "Station.csv"))

    # 找出各檔包含 "score" (不分大小寫) 的欄位
    def score_col(df):
        return next(c for c in df.columns if "score" in c.lower())

    df = degree[["Phone", score_col(degree)]].rename(columns={score_col(degree): "s_degree"})
    df = df.merge(count  [["Phone", score_col(count)  ]].rename(columns={score_col(count):   "s_count"}),   on="Phone", how="outer")
    df = df.merge(car    [["Phone", score_col(car)    ]].rename(columns={score_col(car):     "s_car"}),     on="Phone", how="outer")
    df = df.merge(save   [["Phone", score_col(save)   ]].rename(columns={score_col(save):    "s_save"}),    on="Phone", how="outer")
    df = df.merge(station[["Phone", score_col(station)]].rename(columns={score_col(station): "s_station"}), on="Phone", how="outer")

    df = df.fillna(0)
    df["TotalScore"] = (
        df["s_degree"] + df["s_count"] + df["s_car"] + df["s_save"] + df["s_station"]
    ).astype(int)

    df = df.sort_values("TotalScore", ascending=False).reset_index(drop=True)
    df["rank"]  = df.index + 1
    df["Phone"] = df["Phone"].astype(str).str.zfill(10)

    # all_data：phone -> {rank, score}，供查詢用
    all_data = {
        row["Phone"]: {"rank": int(row["rank"]), "score": int(row["TotalScore"])}
        for _, row in df.iterrows()
    }

    # leaderboard：前 50 名，附 emoji
    EMOJIS = ["🦁","🐯","🦊","🐼","🦄","🐉","🦋","🌟","🔥","⚡",
              "🎯","🏆","💎","🚀","🌈","🦅","🎸","🌙","⭐","🎪"]
    leaderboard = [
        {
            "rank":  int(row["rank"]),
            "phone": row["Phone"],
            "score": int(row["TotalScore"]),
            "emoji": EMOJIS[i % len(EMOJIS)],
        }
        for i, (_, row) in enumerate(df.head(50).iterrows())
    ]

    return all_data, leaderboard


# ── 讀取並注入資料 ──────────────────────────────────────────────
all_data, leaderboard = load_data()

html_path = os.path.join(os.path.dirname(__file__), "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# 將真實資料注入 HTML 的佔位符
html_content = html_content.replace(
    "ALL_DATA_PLACEHOLDER",
    json.dumps(all_data, ensure_ascii=False)
)
html_content = html_content.replace(
    "LEADERBOARD_PLACEHOLDER",
    json.dumps(leaderboard, ensure_ascii=False)
)

st.components.v1.html(html_content, height=1800, scrolling=True)
