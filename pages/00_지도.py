# app.py
import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd

st.set_page_config(page_title="Seoul Top10 for Foreigners", layout="wide")

st.title("📍 Foreigners' Favorite Seoul — Top 10 Tourist Spots")
st.markdown(
    "서울을 처음 방문하는 외국인들이 많이 찾는 **Top 10 관광지**를 지도 위에 표시합니다. "
    "마커를 클릭하면 간단한 설명이 뜹니다."
)

# 중심 좌표(서울 시청 근처)
CENTER = (37.5665, 126.9780)

# 관광지 데이터를 pandas DataFrame으로 구성
data = [
    ["Gyeongbokgung Palace (경복궁)", 37.57961, 126.97704, "조선의 정궁. 경회루, 근정전 등 대표 유적."],
    ["Changdeokgung Palace (창덕궁)", 37.57944, 126.99278, "유네스코 세계유산. 비원(후원)으로 유명."],
    ["Bukchon Hanok Village (북촌한옥마을)", 37.58218, 126.98326, "전통가옥(한옥)이 모여있는 역사적 마을."],
    ["N Seoul Tower / Namsan (N서울타워/남산)", 37.55117, 126.98823, "서울 전경을 볼 수 있는 전망 타워."],
    ["Myeongdong (명동)", 37.56098, 126.98583, "쇼핑·뷰티·길거리음식으로 유명한 쇼핑 거리."],
    ["Insadong (인사동)", 37.57296, 126.98733, "전통 공예품과 찻집이 많은 문화 거리."],
    ["Hongdae (홍대)", 37.55528, 126.92333, "젊음의 거리, 거리공연·카페·클럽 중심지."],
    ["Itaewon (이태원)", 37.53430, 126.99493, "다국적 음식·외국인 거주지·야간 문화 중심."],
    ["Dongdaemun Market (동대문)", 37.5660, 126.9987, "패션·쇼핑의 메카, 야간시장도 활발."],
    ["Gwangjang Market (광장시장)", 37.5700, 126.9990, "전통시장과 길거리 음식(빈대떡·마약김밥)으로 인기."],
]

df = pd.DataFrame(data, columns=["name", "lat", "lon", "desc"])

# Folium 지도 생성
m = folium.Map(location=CENTER, zoom_start=12, control_scale=True)

# 마커 추가
for _, row in df.iterrows():
    popup_html = f"<b>{row['name']}</b><br/>{row['desc']}"
    folium.Marker(
        location=(row["lat"], row["lon"]),
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=row["name"],
        icon=folium.Icon(icon="info-sign")
    ).add_to(m)

st.subheader("🗺️ Seoul Map")
st_folium(m, width=1200, height=700)

st.markdown("---")
st.markdown(
    "데이터 출처(예시): VisitSeoul(서울관광), TripAdvisor, Wikipedia 등. "
    "좌표는 공개 자료에서 취합한 대표 좌표를 사용했습니다."
)
st.caption("앱 소스코드와 requirements.txt를 함께 업로드하면 Streamlit Cloud에서 바로 배포됩니다.")

