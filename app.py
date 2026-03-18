import streamlit as st
import os
import pandas as pd
import json

st.set_page_config(
    page_title="EVALUE 5歲生日快樂活動",
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


# ── 獎品門檻（高→低），只設分數，winners 由程式從 CSV 計算 ──
PRIZE_THRESHOLDS = [10000, 5000, 2500, 2000, 1500, 1000, 750, 500, 300]


@st.cache_data
def load_data():
    """
    讀取五個 CSV，以 Phone 為 key outer join，
    將所有含 'score' 的欄位加總為 TotalScore，
    並計算每個獎品門檻的達標人數。
    回傳 all_data dict 與 winner_counts dict。
    """
    base = os.path.dirname(__file__)

    degree  = pd.read_csv(os.path.join(base, "Degree.csv"))
    count   = pd.read_csv(os.path.join(base, "Count.csv"))
    car     = pd.read_csv(os.path.join(base, "Car.csv"))
    save    = pd.read_csv(os.path.join(base, "Save.csv"))
    station = pd.read_csv(os.path.join(base, "Station.csv"))

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

    # 計算每個門檻達標人數（TotalScore >= threshold）
    winner_counts = {
        pts: int((df["TotalScore"] >= pts).sum())
        for pts in PRIZE_THRESHOLDS
    }

    # all_data：phone -> {rank, score}，供前端查詢
    all_data = {
        row["Phone"]: {"rank": int(row["rank"]), "score": int(row["TotalScore"])}
        for _, row in df.iterrows()
    }

    return all_data, winner_counts


# ── 執行 ────────────────────────────────────────────
all_data, winner_counts = load_data()

html_path = os.path.join(os.path.dirname(__file__), "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

html_content = html_content.replace(
    "ALL_DATA_PLACEHOLDER",
    json.dumps(all_data, ensure_ascii=False)
)
html_content = html_content.replace(
    "WINNER_COUNTS_PLACEHOLDER",
    json.dumps(winner_counts, ensure_ascii=False)   # e.g. {"300":374,"500":91,...}
)

st.components.v1.html(html_content, height=1800, scrolling=True)
