# 📄 app.py — Streamlit 생활기록부 세특 우선순위 기반 줄이기 도구

import re
import io
import streamlit as st

st.set_page_config(page_title="세특 우선축약 도구", layout="wide")

# ----------------------
# 중요도 기반 축약 함수
# ----------------------
IMPORTANT_WORDS = [
    "분석", "설계", "제안", "활용", "개선", "연구", "작성", "조사", "실험", "발표", "참여", "검증"
]
FILLER_WORDS = [
    "또한", "그리고", "및", "같이", "등", "등의", "특히", "주로", "보다", "많이", "약간",
    "수행", "수업", "활동", "관찰", "사용", "활용", "적용"
]

SEPARATORS = ['\n', ';', '·', '•', '/', 'ㆍ', ',', '.']


def remove_parentheses(text: str) -> str:
    return re.sub(r"\([^)]*\)|\[[^]]*\]|\{[^}]*\}", "", text)


def remove_fillers(text: str) -> str:
    for w in FILLER_WORDS:
        text = re.sub(r"\b" + re.escape(w) + r"\b", "", text)
    return re.sub(r"\s+", " ", text).strip()


def split_items(text: str) -> list:
    lines = [l.strip() for l in re.split(r'\n', text) if l.strip()]
    items = []
    for line in lines:
        parts = re.split(r'[;·/ㆍ•,]', line)
        for p in parts:
            p = p.strip()
            if p:
                items.append(p)
    return items


def score_item(item: str) -> int:
    # 중요 단어 등장 수로 점수 계산
    score = sum(item.count(w) for w in IMPORTANT_WORDS)
    return score


def compress_item(item: str, allowed: int) -> str:
    item = remove_parentheses(item)
    item = remove_fillers(item)
    if len(item) <= allowed:
        return item
    # 앞뒤 핵심 단어 유지, 중간 생략
    head_len = int(allowed*0.6)
    tail_len = allowed - head_len - 1
    return item[:head_len] + '…' + item[-tail_len:] if tail_len>0 else item[:allowed-1]+'…'


def compress_section(text: str, target_len: int) -> str:
    items = split_items(text)
    if not items:
        return compress_item(text, target_len)

    # 중요도 점수로 정렬(높은 순)
    items_sorted = sorted(items, key=lambda x: score_item(x), reverse=True)

    n = len(items_sorted)
    min_each = max(10, target_len // n)
    allowed_per_item = [min_each]*n

    # 비례 조정
    total_alloc = sum(allowed_per_item)
    if total_alloc > target_len:
        factor = target_len / total_alloc
        allowed_per_item = [max(3,int(a*factor)) for a in allowed_per_item]

    # 남은 글자수 분배
    while sum(allowed_per_item) < target_len:
        for i in range(n):
            if sum(allowed_per_item) >= target_len:
                break
            allowed_per_item[i] += 1

    compressed_items = [compress_item(it, al) for it, al in zip(items_sorted, allowed_per_item)]
    compressed_text = '; '.join(compressed_items)
    return compressed_text if len(compressed_text)<=target_len else compressed_text[:target_len-1]+'…'

# ----------------------
# Streamlit UI
# ----------------------
st.title("📝 세부특기사항 우선순위 기반 자동 축약")
st.write("중요 내용 위주로 글자수에 맞게 축약합니다.")

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
            compressed = compress_section(sec, limit)
            results.append(compressed)

        output = '\n\n'.join(results)
        st.subheader("📄 축약 결과")
        st.text_area("결과", output, height=300)

        st.download_button(
            label="📥 결과 다운로드 (.txt)",
            data=output.encode('utf-8'),
            file_name="shortened_se_priority.txt",
            mime="text/plain"
        )

st.markdown("---")
st.markdown("✅ TIP: 빈 줄로 과목을 구분하면 각 과목별로 자동 처리됩니다.")
