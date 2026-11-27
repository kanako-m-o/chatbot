import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="為替換算表アプリ", page_icon="💱", layout="centered")
st.title("💱 日本円 ⇔ 外貨 為替換算表")

# プルダウンに表示する通貨リスト（必要に応じて追加可能）
CURRENCIES = {
    "USD": "米ドル (USD)",
    "EUR": "ユーロ (EUR)",
    "GBP": "英ポンド (GBP)",
    "AUD": "豪ドル (AUD)",
    "CAD": "カナダドル (CAD)",
    "CHF": "スイスフラン (CHF)",
    "CNY": "中国人民元 (CNY)",
    "KRW": "韓国ウォン (KRW)",
    "SGD": "シンガポールドル (SGD)",
    "THB": "タイバーツ (THB)",
}

@st.cache_data(ttl=3600)
def fetch_jpy_rates():
    """日本円(JPY)を基準とした最新の為替レートを取得（1時間キャッシュ）"""
    url = "https://api.frankfurter.dev/v1/latest"
    params = {"base": "JPY"}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

# 1. 為替レートの取得とエラーハンドリング
try:
    data = fetch_jpy_rates()
    rates = data["rates"]
    rate_date = data["date"]
except requests.exceptions.RequestException as e:
    st.error(f"為替レートの取得に失敗しました。時間をおいて再試行してください。\n詳細: {e}")
    st.stop()

# 2. 外貨選択プルダウン
available_codes = [code for code in CURRENCIES.keys() if code in rates]
selected_code = st.selectbox(
    "換算する外貨を選択してください",
    options=available_codes,
    format_func=lambda code: CURRENCIES[code]
)

# レート計算（1 JPYあたりの外貨 / 1 外貨あたりのJPY）
jpy_to_foreign = rates[selected_code]
foreign_to_jpy = 1.0 / jpy_to_foreign

st.info(
    f"**現在レート:** 1 {selected_code} = **{foreign_to_jpy:,.2f} 円** "
    f"（100 円 = {jpy_to_foreign * 100:,.2f} {selected_code}）｜ 基準日: {rate_date}"
)

st.divider()

# 3. 自由入力の金額シミュレーター
st.subheader("🔢 金額を指定して計算")
col1, col2 = st.columns(2)

with col1:
    jpy_input = st.number_input("日本円 (JPY) を入力", min_value=0, value=10000, step=1000)
    st.metric(
        label=f"{CURRENCIES[selected_code]} への換算額",
        value=f"{jpy_input * jpy_to_foreign:,.2f} {selected_code}"
    )

with col2:
    foreign_input = st.number_input(f"{selected_code} を入力", min_value=0.0, value=100.0, step=10.0)
    st.metric(
        label="日本円 (JPY) への換算額",
        value=f"{foreign_input * foreign_to_jpy:,.0f} 円"
    )

st.divider()

# 4. 早見換算表の作成と表示
st.subheader("📊 金額別・早見換算表")
tab1, tab2 = st.tabs([f"{selected_code} ➔ 日本円", f"日本円 ➔ {selected_code}"])

with tab1:
    foreign_units = [1, 5, 10, 20, 50, 100, 500, 1000]
    df_to_jpy = pd.DataFrame({
        f"外貨 ({selected_code})": [f"{u:,} {selected_code}" for u in foreign_units],
        "日本円 (JPY) 換算": [f"{u * foreign_to_jpy:,.0f} 円" for u in foreign_units]
    })
    st.dataframe(df_to_jpy, use_container_width=True, hide_index=True)

with tab2:
    jpy_units = [100, 500, 1000, 3000, 5000, 10000, 50000, 100000]
    df_to_foreign = pd.DataFrame({
        "日本円 (JPY)": [f"{u:,} 円" for u in jpy_units],
        f"外貨 ({selected_code}) 換算": [f"{u * jpy_to_foreign:,.2f} {selected_code}" for u in jpy_units]
    })
    st.dataframe(df_to_foreign, use_container_width=True, hide_index=True)
