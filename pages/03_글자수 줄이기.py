# 📄 app.py — Streamlit 세특 완전한 문장 기반 자동 축약 도구

import re
import io
import streamlit as st

st.set_page_config(page_title="세특 문장 기반 축약 도구", layout="wide")

# ----------------------
# 중요도 기반 문장 축약 함수
# ----------------------
IMPORTANT_WORDS = [
    "분석", "설계", "제안", "활용", "개선", "연구", "작성", "조사", "실험", "발표", "참여", "검증"
]
FILLER_WORDS = [
    "또한", "그리고", "및", "같이", "등", "등의", "특히", "주로", "보다", "많이", "약간",
    "수행", "수업", "활동", "관찰", "사용", "적용"
]


def clean_sentence(sentence: str) -> str:
    # 괄호 제거
    sentence = re.sub(r"\([^)]*\)|\[[^]]*\]|\{[^}]*\}", "", sentence)
    # 불용어 제거
    for w in FILLER_WORDS:
        sentence = re.sub(r"\b" + re.escape(w) + r"\b", "", sentence)
    # 공백 정리
    sentence = re.sub(r"\s+", " ", sentence).strip()
    return sentence


def split_sentences(text: str) -> list:
    # 마침표, 느낌표, 물음표 기준으로 문장 분리
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def score_sentence(sentence: str) -> int:
    # 중요 키워드 등장 횟수로 점수 계산
    return sum(sentence.count(w) for w in IMPORTANT_WORDS)


def compress_sentences(sentences: list, target_len: int) -> str:
    # 중요도 순 정렬
    sentences_sorted = sorted(sentences, key=score_sentence, reverse=True)
    output = ''
    for s in sentences_sorted:
        s_clean = clean_sentence(s)
        if not s_clean:
            continue
        if len(output) + len(s_clean) + 1 <= target_len:
            if output:
                output += ' ' + s_clean
            else:
                output = s_clean
        else:
            # 글자수가 부족하면 앞뒤 핵심 단어 유지
            remaining = target_len - len(output) - 2
            if remaining > 10:
                head_len = int(remaining * 0.6)
                tail_len = remaining - head_len
                s_final = s_clean[:head_len] + '…' + s_clean[-tail_len:] if tail_len>0 else s_clean[:remaining] + '…'
                output += ' ' + s_final
            break
    return output.strip()

# ----------------------
# Streamlit UI
# ----------------------
st.title("📝 세부특기사항 문장 기반 자동 축약")
st.write("학생부 세특용 완전한 문장 형태로 중요 내용 중심 축약")

input_mode = st.radio("입력 방식", ["직접 입력", "파일 업로드"])

if input_mode == "직접 입력":
    text = st.text_area("세특 내용을 입력하세요", height=300)
else:
    uploaded = st.file_uploader(".txt 파일 업로드", type=["txt"])
    text = ""
    if uploaded:
        text = uploaded.read().decode("utf-8")

limit = st.number_input("목표 글자 수", min_value=50, max_value=1000, value=250, step=10)

if st.button("✂️ 줄이기 실행"):
    if not text.strip():
        st.warning("먼저 내용을 입력하세요.")
    else:
        sections = re.split(r'\n\s*\n', text.strip())
        results = []
        for sec in sections:
            sentences = split_sentences(sec)
            compressed = compress_sentences(sentences, limit)
            results.append(compressed)

        output = '\n\n'.join(results)
        st.subheader("📄 축약 결과")
        st.text_area("결과", output, height=300)

        st.download_button(
            label="📥 결과 다운로드 (.txt)",
            data=output.encode('utf-8'),
            file_name="shortened_se_sentences.txt",
            mime="text/plain"
        )

st.markdown("---")
st.markdown("✅ TIP: 빈 줄로 과목을 구분하면 각 과목별로 자연스러운 문장 단위 축약이 가능합니다.")
