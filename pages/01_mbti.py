import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="국가별 MBTI 비율 시각화", layout="centered")

st.title("🌍 국가별 MBTI 비율 시각화")
st.write("국가를 선택하면 해당 국가의 MBTI 분포를 확인할 수 있습니다.")

# CSV 파일 로드
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

# 국가 선택
country_list = sorted(df["Country"].unique())
selected_country = st.selectbox("국가를 선택하세요", country_list)

# 선택한 국가의 MBTI 비율 추출
country_data = df[df["Country"] == selected_country].iloc[0, 1:]
country_df = pd.DataFrame({
    "MBTI": country_data.index,
    "비율": country_data.values
}).sort_values("비율", ascending=False)

# 색상 설정: 1등은 빨강, 나머지는 그라데이션
colors = ['#ff0000'] + px.colors.sequential.Reds[2:len(country_df)]  # 1등 빨강, 이후 붉은계열

# Plotly 그래프 생성
fig = px.bar(
    country_df,
    x="MBTI",
    y="비율",
    color="비율",
    color_continuous_scale=colors,
    title=f"🇨🇳 {selected_country}의 MBTI 비율"
)

# 1등 막대 빨강으로 고정
fig.update_traces(marker_color=[
    '#ff0000' if i == 0 else f'rgba(255,{100 + i*5}, {100 + i*10}, 0.8)'
    for i in range(len(country_df))
])

fig.update_layout(
    xaxis_title="MBTI 유형",
    yaxis_title="비율(%)",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    title_font_size=20
)

st.plotly_chart(fig, use_container_width=True)

st.caption("데이터 출처: countriesMBTI_16types.csv")
