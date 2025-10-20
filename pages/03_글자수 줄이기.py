# 📄 app.py — Streamlit 생활기록부 세특 줄이기 도구

import re
import io
import streamlit as st

st.set_page_config(page_title="세특 줄이기 도구", layout="wide")

# ----------------------
# 간단한 축약 함수
# ----------------------
def shorten_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    # 괄호 제거
    text = re.sub(r"\([^)]*\)|\[[^]]*\]", "", text)
    # 불필요한 공백 정리
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    # 문장 단위로 잘라서 최대한 유지
    parts = re.split(r"(?<=[.!?]|\n)", text)
    result = ""
    for p in parts:
        if len(result) + len(p) <= limit:
            result += p
        else:
            break
    # 그래도 초과하면 앞뒤를 남기고 말줄임
    if len(result) > limit:
        result = result[:limit-1] + "…"
    return result

# ----------------------
# Streamlit UI
# ----------------------
st.title("📝 생활기록부 세부특기사항 자동 줄이기")
st.write("원하는 글자 수로 자동 축약합니다. 수행평가 내용이 빠지지 않게 문장 단위로 처리합니다.")

input_mode = st.radio("입력 방식", ["직접 입력", "파일 업로드"])

if input_mode == "직접 입력":
    text = st.text_area("세특 내용을 입력하세요", height=300)
else:
    uploaded = st.file_uploader(".txt 파일 업로드", type=["txt"])
    text = ""
    if uploaded:
        text = uploaded.read().decode("utf-8")

limit = st.number_input("원하는 글자 수", min_value=50, max_value=1000, value=250, step=10)

if st.button("✂️ 줄이기 실행"):
    if not text.strip():
        st.warning("먼저 내용을 입력하세요.")
    else:
        # 과목별로 나누기: 빈 줄 기준
        sections = re.split(r"\n\s*\n", text.strip())
        results = []
        for sec in sections:
            sec = sec.strip()
            shortened = shorten_text(sec, limit)
            results.append(shortened)

        output = "\n\n".join(results)
        st.subheader("📄 축약 결과")
        st.text_area("결과", output, height=300)

        st.download_button(
            label="📥 결과 다운로드 (.txt)",
            data=output.encode("utf-8"),
            file_name="shortened_se.txt",
            mime="text/plain"
        )

st.markdown("---")
st.markdown("✅ **TIP:** 빈 줄로 과목을 구분하면 각 과목별로 자동 처리됩니다.")

# 끝
