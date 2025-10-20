import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="국가별 MBTI 비율 시각화", layout="centered")

st.title("🌍 국가별 MBTI 비율 시각화")
st.write("국가를 선택하면 해당 국가의 MBTI 분포를 막대그래프로 확인할 수 있습니다.")

# CSV 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

# 국가 목록 추출
if "Country" not in df.columns:
    st.error("⚠️ CSV 파일에 'Country' 컬럼이 없습니다. 파일 구조를 확인하세요.")
else:
    countries = sorted(df["Country"].unique())
    selected_country = st.selectbox("국가를 선택하세요 🌏", countries)

    # 선택한 국가의 MBTI 데이터 추출
    country_row = df[df["Country"] == selected_country].iloc[0, 1:]
    country_df = pd.DataFrame({
        "MBTI": country_row.index,
        "비율": country_row.values
    }).sort_values("비율", ascending=False)

    # 색상 지정 (1등은 빨강, 나머지는 그라데이션)
    color_list = ['#FF0000'] + [f'rgba(255, {int(230 - i*8)}, {int(230 - i*8)}, 0.9)' for i in range(1, len(country_df))]

    # Plotly 그래프
    fig = px.bar(
        country_df,
        x="MBTI",
        y="비율",
        text="비율",
        title=f"🇨🇳 {selected_country}의 MBTI 비율",
    )

    # 색상 적용
    fig.update_traces(marker_color=color_list, texttemplate="%{text:.1f}", textposition="outside")

    # 그래프 레이아웃 꾸미기
    fig.update_layout(
        xaxis_title="MBTI 유형",
        yaxis_title="비율(%)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14),
        title_font_size=22,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption("데이터 출처: countriesMBTI_16types.csv")
