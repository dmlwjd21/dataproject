# app.py
import streamlit as st
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Seoul Top10 for Foreigners", layout="wide")

st.title("📍 Foreigners' Favorite Seoul — Top 10 Tourist Spots")
st.markdown(
    "서울을 처음 방문하는 외국인들이 많이 찾는 **Top 10 관광지**를 지도 위에 표시합니다. "
    "마커를 클릭하면 간단한 설명이 뜹니다."
)

# 중심 좌표(서울 시청 근처)
CENTER = (37.5665, 126.9780)

# Top10 명소 (이름, 위도, 경도, 한줄 설명)
places = [
    {"name": "Gyeongbokgung Palace (경복궁)", "lat": 37.57961, "lon": 126.97704,
     "desc": "조선의 정궁. 경회루, 근정전 등 대표 유적."},
    {"name": "Changdeokgung Palace (창덕궁)", "lat": 37.57944, "lon": 126.99278,
     "desc": "유네스코 세계유산. 비원(후원)으로 유명."},
    {"name": "Bukchon Hanok Village (북촌한옥마을)", "lat": 37.58218, "lon": 126.98326,
     "desc": "전통가옥(한옥)이 모여있는 역사적 마을."},
    {"name": "N Seoul Tower / Namsan (N서울타워/남산)", "lat": 37.55117, "lon": 126.98823,
     "desc": "서울 전경을 볼 수 있는 전망 타워."},
    {"name": "Myeongdong (명동)", "lat": 37.56098, "lon": 126.98583,
     "desc": "쇼핑·뷰티·길거리음식으로 유명한 쇼핑 거리."},
    {"name": "Insadong (인사동)", "lat": 37.57296, "lon": 126.98733,
     "desc": "전통 공예품과 찻집이 많은 문화 거리."},
    {"name": "Hongdae (홍대)", "lat": 37.55528, "lon": 126.92333,
     "desc": "젊음의 거리, 거리공연·카페·클럽 중심지."},
    {"name": "Itaewon (이태원)", "lat": 37.53430, "lon": 126.99493,
     "desc": "다국적 음식·외국인 거주지·야간 문화 중심."},
    {"name": "Dongdaemun Market (동대문)", "lat": 37.5660, "lon": 126.9987,
     "desc": "패션·쇼핑의 메카, 야간시장도 활발."},
    {"name": "Gwangjang Market (광장시장)", "lat": 37.5700, "lon": 126.9990,
     "desc": "전통시장과 길거리 음식(빈대떡·마약김밥)으로 인기."},
]

# Folium 지도 생성
m = folium.Map(location=CENTER, zoom_start=12, control_scale=True)

# 마커 추가
for p in places:
    popup_html = f"<b>{p['name']}</b><br/>{p['desc']}"
    folium.Marker(
        location=(p["lat"], p["lon"]),
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=p["name"],
        icon=folium.Icon(icon="info-sign")
    ).add_to(m)

# 추가 레이어 (클러스터 등) 원하시면 주석 해제 후 사용
# from folium.plugins import MarkerCluster
# marker_cluster = MarkerCluster().add_to(m)
# for p in places:
#     folium.Marker((p['lat'], p['lon']), popup=p['name']).add_to(marker_cluster)

st.subheader("🗺️ Seoul Map")
# streamlit_folium로 Folium 지도 렌더링
st_folium(m, width=1200, height=700)

st.markdown("---")
st.markdown(
    "데이터 출처(예시): VisitSeoul(서울관광), TripAdvisor, Wikipedia 등. "
    "좌표는 공개 자료에서 취합한 대표 좌표를 사용했습니다."
)
st.caption("앱 소스코드와 requirements.txt를 같이 업로드하면 Streamlit Cloud에서 바로 배포됩니다.")
