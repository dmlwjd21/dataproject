# Streamlit app: 생활기록부(과목별 세부특기사항) 줄이기 도구
# 파일 구성:
# 1) app.py (이 파일) - 스트림릿 앱
# 2) requirements.txt (아래에 포함)

"""
사용법 요약:
- 텍스트를 붙여넣거나 파일(.txt/.md/.docx 등 텍스트 기반)을 업로드하세요.
- '목표 글자수(과목별)'에 원하는 최대 글자수를 입력하세요.
- '분할 기준'은 입력 텍스트를 과목별/항목별로 나누는 기준입니다. 기본은 빈 줄(한 문단)을 과목 단위로 봅니다.
- 결과를 확인한 뒤 '결과 다운로드(.txt)'로 저장하세요.

알고리즘 요약(간단한 원칙):
- 입력을 여러 '과목 섹션'으로 분리(빈줄 기준). 각 섹션의 첫 줄이 과목명(예: 국어:)이면 제목으로 사용.
- 섹션 내부는 줄바꿈 또는 쉼표/세미콜론 등으로 '평가 항목'을 분리.
- 목표 글자수 내에서 각 평가 항목이 빠지지 않도록, 목표 글자수를 항목 개수에 균등 배분하여 각 항목을 축약.
- 항목 축약은: (1) 괄호/보조 설명 제거, (2) 불필요한 연결어/불용어 제거, (3) 여전히 길면 앞부분+말줄임+뒷부분을 합쳐 요약.

주의: 이 도구는 규칙 기반의 자동 축약기입니다. 의미 보존을 우선하지만 완벽을 보장하지 않으므로 결과를 교사가 최종 확인하세요.
"""

import re
import io
import textwrap
import streamlit as st
from typing import List, Tuple

st.set_page_config(page_title="세특 줄이기 도구", layout="wide")

# --- 유틸리티 함수들 ---
FILLER_WORDS = [
    "또한", "그리고", "및", "같이", "등", "등의", "특히", "주로", "보다", "많이", "약간",
    "수행", "수업", "활동", "관찰", "실험", "연구", "사용", "활용", "적용", "개선", "제안"
]

SEPARATORS = ["\n", ";", "·", "•", "/", "ㆍ", ",", ".", "--"]


def remove_parentheses(text: str) -> str:
    # 괄호 및 괄호 내부 제거 (소괄호, 대괄호, 중괄호)
    return re.sub(r"\([^)]*\)|\[[^]]*\]|\{[^}]*\}", "", text)


def remove_redundant_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_fillers(text: str) -> str:
    # 간단한 불용어 제거: 단어 단위로 검사
    for w in FILLER_WORDS:
        # 경계 단어로만 제거
        text = re.sub(r"\b" + re.escape(w) + r"\b", "", text)
    return remove_redundant_spaces(text)


def split_items(section_text: str) -> List[str]:
    # 우선 줄바꿈으로 나누고, 각 줄에서 추가 구분자(쉼표 등)로 더 나눔
    lines = [l.strip() for l in section_text.splitlines() if l.strip()]
    items = []
    for line in lines:
        # 복수 구분자로 분할(그러나 숫자/연도 등에서 분할하지 않도록 단순 분할)
        parts = re.split(r"[;·/ㆍ•,]\s*", line)
        for p in parts:
            p = p.strip()
            if p:
                items.append(p)
    return items


def compress_item(item: str, allowed: int) -> str:
    item = item.strip()
    if len(item) <= allowed:
        return item

    # 1) 괄호 제거
    s = remove_parentheses(item)
    s = remove_redundant_spaces(s)
    if len(s) <= allowed:
        return s

    # 2) 불용어 제거
    s2 = remove_fillers(s)
    if len(s2) <= allowed:
        return s2

    # 3) 구문 단위로 나눠 덜 중요한 뒷부분부터 제거
    clauses = re.split(r"[,;:\-–—]", s2)
    clauses = [c.strip() for c in clauses if c.strip()]
    if len(clauses) > 1:
        # 각 절을 앞에서부터 합쳐 가능한 만큼 유지
        out = ""
        for c in clauses:
            if len(out) + len((", " if out else "")) + len(c) <= allowed:
                out = (out + ", " + c) if out else c
            else:
                # 더 이상 추가 불가
                continue
        if out:
            return out if len(out) <= allowed else out[:allowed-1] + "…"

    # 4) 최후의 수단: 앞과 뒤를 남겨 중간을 생략
    if allowed <= 6:
        # 매우 짧으면 단순 자르기
        return s2[:allowed]
    # 보존 비율: 앞부분 60%, 뒷부분 40%
    head_len = int(allowed * 0.6)
    tail_len = allowed - head_len - 1
    head = s2[:head_len].rstrip()
    tail = s2[-tail_len:].lstrip() if tail_len > 0 else ""
    return head + "…" + tail


def compress_section(section_title: str, section_body: str, target_len: int) -> Tuple[str, str]:
    """
    섹션(과목) 단위로 축약.
    - section_title: 과목명(빈 문자열 가능)
    - section_body: 해당 과목의 원문 텍스트
    - target_len: 이 섹션이 최종적으로 가져야 할 총 글자수(공백 포함)
    반환: (title, compressed_text)
    """
    items = split_items(section_body)
    if not items:
        # body가 한 줄 뿐인 경우
        compressed = compress_item(section_body.strip(), target_len)
        return section_title, compressed

    # 각 항목이 최소한 차지할 수 있는 글자수 계산
    n = len(items)
    min_each = max(10, target_len // n)  # 각 항목 최소 10자 보장
    # 만약 min_each * n > target_len (작아질 수 없음), 마지막 항목들은 더 작게 준다
    allowed_per_item = [min_each] * n
    # 조정: 총합이 target_len보다 크면 비례적으로 줄이기
    total_alloc = sum(allowed_per_item)
    if total_alloc > target_len:
        # 비례 축소
        factor = target_len / total_alloc
        allowed_per_item = [max(3, int(a * factor)) for a in allowed_per_item]

    # 마지막으로 남은 여유를 앞쪽 항목에 배분
    while sum(allowed_per_item) < target_len:
        for i in range(n):
            if sum(allowed_per_item) >= target_len:
                break
            allowed_per_item[i] += 1

    compressed_items = []
    for item, allow in zip(items, allowed_per_item):
        compressed_items.append(compress_item(item, allow))

    # 합쳐서 하나의 문단으로
    compressed_text = "; ".join(compressed_items)
    compressed_text = remove_redundant_spaces(compressed_text)
    # 최종 안전장치
    if len(compressed_text) > target_len:
        compressed_text = compressed_text[:target_len-1] + "…"
    return section_title, compressed_text


def parse_sections(text: str) -> List[Tuple[str, str]]:
    # 빈 줄(연속 개행)로 섹션을 분할
    parts = re.split(r"\n\s*\n", text.strip())
    sections = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # 첫 줄이 과목명인 경우(예: 국어:, 국어 - 등) 추출
        lines = p.splitlines()
        first = lines[0].strip()
        m = re.match(r"^([\w가-힣 ]{1,20}[:\-]\s*)(.*)$", first)
        if m:
            title = m.group(1).rstrip(': -')
            body = "\n".join([m.group(2).strip()] + [l.strip() for l in lines[1:]])
        else:
            # 만약 첫 줄이 과목명처럼 보이면 제목 처리
            if len(first) <= 20 and ('과' in first or '교과' in first or first.endswith('과') or first.endswith('교과')):
                title = first
                body = "\n".join(lines[1:])
            else:
                title = ""
                body = p
        sections.append((title, body))
    return sections


# --- Streamlit UI ---
st.title("📝 생활기록부(세부특기사항) 자동 축약기")
st.markdown("간단하고 규칙 기반으로 과목별 세특을 지정한 글자수로 줄여줍니다. (최종 결과는 교사가 확인하세요.)")

col1, col2 = st.columns([2,1])
with col1:
    input_mode = st.radio("입력 방식 선택:", ("텍스트 붙여넣기", "파일 업로드 (.txt/.md)"))
    if input_mode == "텍스트 붙여넣기":
        raw = st.text_area("원문을 여기에 붙여넣기", height=300)
    else:
        uploaded = st.file_uploader("텍스트 파일 업로드(utf-8 텍스트, .txt/.md)", type=["txt", "md"], accept_multiple_files=False)
        raw = ""
        if uploaded is not None:
            try:
                raw = uploaded.read().decode('utf-8')
            except Exception:
                # fallback: 스트림릿이 이미 문자열로 준 경우
                try:
                    raw = uploaded.getvalue().decode('utf-8')
                except Exception:
                    st.error("파일을 읽는 중 오류가 발생했습니다. UTF-8 텍스트 파일인지 확인하세요.")

with col2:
    target_global = st.number_input("목표 글자수 (과목별) — 원하는 최대 글자수 입력:", min_value=30, max_value=2000, value=250, step=10)
    st.write("각 과목별로 이 글자수(또는 근사치)로 줄입니다.")
    option_preserve_lines = st.checkbox("원본 줄(항목) 보존 우선(항목 누락 방지)", value=True)
    st.markdown("---")
    st.markdown("⚠️ 자동 규칙 기반 축약입니다. 결과는 항상 사람이 검토하세요.")

if st.button("줄이기 실행"):
    if not raw or raw.strip() == "":
        st.warning("먼저 원문을 입력하거나 파일을 업로드하세요.")
    else:
        sections = parse_sections(raw)
        # 균등 배분: 각 섹션에 target_global 할당
        results = []
        for title, body in sections:
            t, compressed = compress_section(title, body, target_global)
            results.append((t, compressed))

        # 결과 표시
        st.subheader("✅ 축약 결과")
        out_buf = io.StringIO()
        for t, c in results:
            header = (t + ":") if t else ""
            st.markdown(f"**{header}**")
            st.write(c)
            out_buf.write(header + "\n")
            out_buf.write(c + "\n\n")

        # 다운로드
        st.download_button("결과 다운로드 (.txt)", data=out_buf.getvalue().encode('utf-8'), file_name="se_tuk_shortened.txt", mime='text/plain')

        st.info("각 항목이 최대한 유지되도록 항목 단위로 축약했습니다. 필요하면 목표 글자수를 늘려 더 여유 있게 만드세요.")

# --- Footer / 도움말 ---
st.markdown("---")
st.markdown("### 사용 팁")
st.markdown("- 입력 시 과목을 구분하려면 빈 줄로 분리하세요.\n- 과목명 뒤에 ':'를 붙이면 제목으로 인식합니다 (예: 국어:).\n- 결과는 반드시 교사가 최종 검토 후 사용하세요.")

# === requirements.txt (아래 복사해서 별도 파일로 저장하세요) ===
# requirements.txt
# streamlit만으로 동작합니다.

# streamlit==1.26.0


# (끝)
