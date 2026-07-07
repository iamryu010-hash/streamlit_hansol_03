import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="🎵 노래 추천 서비스", page_icon="🎵", layout="centered")

st.title("🎵 AI 노래 추천 서비스")
st.markdown("몇 가지 질문에 답하면 딱 맞는 노래를 추천해 드려요!")

with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    if api_key:
        st.success("API 키가 입력되었습니다.")
    else:
        st.warning("API 키를 입력해주세요.")

# ── 탭 구성 ──────────────────────────────────────────────
tab1, tab2 = st.tabs(["📋 설문으로 추천받기", "🔍 노래 / 가수 검색"])

# ════════════════════════════════════════════════════════
# TAB 1 : 설문 추천
# ════════════════════════════════════════════════════════
with tab1:
    st.subheader("📋 설문 조사")

    col1, col2 = st.columns(2)

    with col1:
        mood = st.selectbox(
            "1. 지금 기분이 어떠세요?",
            ["😊 기쁘고 활기차요", "😢 슬프고 감성적이에요", "😌 편안하고 여유로워요",
             "😤 에너지가 넘쳐요", "🥱 피곤하고 지쳐있어요", "💭 생각이 많아요"]
        )

        activity = st.selectbox(
            "2. 지금 무엇을 하고 있나요?",
            ["🏃 운동 중", "📚 공부/작업 중", "🚗 이동 중", "🛁 휴식 중",
             "🍽️ 식사 중", "😴 잠들기 전"]
        )

        genre = st.multiselect(
            "3. 선호하는 음악 장르를 선택하세요 (복수 선택 가능)",
            ["팝 (Pop)", "K-Pop", "R&B / Soul", "힙합 (Hip-hop)", "록 (Rock)",
             "재즈 (Jazz)", "클래식 (Classical)", "인디 (Indie)", "발라드", "댄스/EDM"],
            default=["팝 (Pop)"]
        )

    with col2:
        era = st.selectbox(
            "4. 선호하는 음악 시대는?",
            ["상관없음", "2020년대", "2010년대", "2000년대", "1990년대", "1980년대 이전"]
        )

        tempo = st.select_slider(
            "5. 원하는 템포는?",
            options=["매우 느림", "느림", "보통", "빠름", "매우 빠름"],
            value="보통"
        )

        language = st.radio(
            "6. 선호하는 언어는?",
            ["상관없음", "한국어", "영어", "일본어", "기타"]
        )

    lyrics_mood = st.text_area(
        "7. 어떤 분위기의 가사를 원하시나요? (선택 사항)",
        placeholder="예: 위로가 되는 가사, 신나는 파티 분위기, 사랑 노래, 이별 노래...",
        height=80
    )

    num_songs = st.slider("추천받을 노래 수", min_value=3, max_value=10, value=5)

    st.divider()

    if st.button("🎵 노래 추천받기", type="primary", use_container_width=True):
        if not api_key:
            st.error("사이드바에서 OpenAI API 키를 먼저 입력해주세요.")
        elif not genre:
            st.error("선호하는 장르를 최소 1개 이상 선택해주세요.")
        else:
            with st.spinner("AI가 딱 맞는 노래를 찾고 있어요... 🎶"):
                try:
                    client = OpenAI(api_key=api_key)

                    prompt = f"""당신은 음악 전문가입니다. 사용자의 설문 응답을 바탕으로 노래를 추천해주세요.

사용자 정보:
- 현재 기분: {mood}
- 현재 활동: {activity}
- 선호 장르: {', '.join(genre)}
- 선호 시대: {era}
- 원하는 템포: {tempo}
- 선호 언어: {language}
- 원하는 가사 분위기: {lyrics_mood if lyrics_mood else '특별한 요구 없음'}

위 조건에 맞는 노래 {num_songs}곡을 추천해주세요.

각 노래에 대해 다음 형식으로 답변해주세요:
**[번호]. 곡명 - 아티스트명**
- 🎵 장르: (장르)
- 📅 발매년도: (년도)
- 💡 추천 이유: (이 사용자에게 왜 이 곡이 잘 맞는지 1-2문장)

마지막에 전체적인 플레이리스트 분위기를 한 줄로 요약해주세요."""

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "당신은 음악 취향 분석 전문가입니다. 사용자의 감정과 상황에 맞는 최적의 노래를 추천합니다."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.8,
                        max_tokens=1500
                    )

                    result = response.choices[0].message.content

                    st.success("추천 완료! 🎉")
                    st.subheader("🎧 추천 플레이리스트")
                    st.markdown(result)

                    st.divider()
                    with st.expander("📊 내 설문 요약 보기"):
                        st.markdown(f"""
| 항목 | 선택 |
|------|------|
| 기분 | {mood} |
| 활동 | {activity} |
| 장르 | {', '.join(genre)} |
| 시대 | {era} |
| 템포 | {tempo} |
| 언어 | {language} |
""")

                except Exception as e:
                    error_msg = str(e)
                    if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "401" in error_msg:
                        st.error("❌ API 키가 올바르지 않습니다. 유효한 OpenAI API 키를 입력해주세요.")
                    elif "quota" in error_msg.lower() or "429" in error_msg:
                        st.error("❌ API 사용량 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
                    else:
                        st.error(f"❌ 오류가 발생했습니다: {error_msg}")

# ════════════════════════════════════════════════════════
# TAB 2 : 노래 / 가수 검색
# ════════════════════════════════════════════════════════
with tab2:
    st.subheader("🔍 노래 / 가수 검색")
    st.markdown("가수 이름이나 노래 제목을 입력하면 관련 정보와 비슷한 곡을 알려드려요.")

    search_type = st.radio(
        "검색 유형",
        ["🎤 가수로 검색", "🎵 노래 제목으로 검색"],
        horizontal=True
    )

    if search_type == "🎤 가수로 검색":
        search_input = st.text_input(
            "가수 이름을 입력하세요",
            placeholder="예: 아이유, BTS, Taylor Swift, The Beatles..."
        )
        search_detail = st.selectbox(
            "원하는 정보",
            ["대표곡 추천", "숨겨진 명곡 추천", "최신곡 위주 추천", "가수 소개 + 추천곡"]
        )
        num_search = st.slider("결과 노래 수", min_value=3, max_value=10, value=5, key="search_num")
    else:
        search_input = st.text_input(
            "노래 제목을 입력하세요",
            placeholder="예: Dynamite, 밤편지, Shape of You, 봄날..."
        )
        search_detail = st.selectbox(
            "원하는 정보",
            ["노래 상세 정보 + 비슷한 곡 추천", "비슷한 분위기 곡 추천", "같은 가수의 다른 곡 추천"]
        )
        num_search = st.slider("결과 노래 수", min_value=3, max_value=10, value=5, key="search_num2")

    st.divider()

    if st.button("🔍 검색하기", type="primary", use_container_width=True, key="search_btn"):
        if not api_key:
            st.error("사이드바에서 OpenAI API 키를 먼저 입력해주세요.")
        elif not search_input.strip():
            st.error("검색어를 입력해주세요.")
        else:
            with st.spinner("AI가 정보를 찾고 있어요... 🔍"):
                try:
                    client = OpenAI(api_key=api_key)

                    if search_type == "🎤 가수로 검색":
                        prompt = f"""당신은 음악 전문가입니다.
가수 "{search_input}"에 대해 "{search_detail}" 방식으로 노래 {num_search}곡을 알려주세요.

다음 형식으로 답변해주세요:

## 🎤 {search_input} 소개
(가수에 대한 간략한 소개 2-3문장)

## 🎵 추천곡 목록
각 노래에 대해:
**[번호]. 곡명**
- 📅 발매년도: (년도)
- 🎵 장르: (장르)
- ✨ 곡 소개: (이 곡의 특징이나 매력 1-2문장)

마지막에 이 가수의 음악적 특징을 한 줄로 요약해주세요."""
                    else:
                        prompt = f"""당신은 음악 전문가입니다.
노래 "{search_input}"에 대해 "{search_detail}" 방식으로 정보를 제공하고 노래 {num_search}곡을 추천해주세요.

다음 형식으로 답변해주세요:

## 🎵 "{search_input}" 정보
- 🎤 아티스트: (아티스트명)
- 📅 발매년도: (년도)
- 🎵 장르: (장르)
- ✨ 곡 소개: (이 곡의 특징이나 매력 2-3문장)

## 🎧 관련 추천곡
각 노래에 대해:
**[번호]. 곡명 - 아티스트명**
- 📅 발매년도: (년도)
- 💡 추천 이유: (원곡과 어떤 점이 비슷한지 1문장)

마지막에 이 곡과 추천곡들의 공통된 분위기를 한 줄로 요약해주세요."""

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "당신은 음악 전문가입니다. 정확하고 유익한 음악 정보를 제공합니다."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1500
                    )

                    result = response.choices[0].message.content

                    st.success("검색 완료! 🎉")
                    st.markdown(result)

                except Exception as e:
                    error_msg = str(e)
                    if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "401" in error_msg:
                        st.error("❌ API 키가 올바르지 않습니다. 유효한 OpenAI API 키를 입력해주세요.")
                    elif "quota" in error_msg.lower() or "429" in error_msg:
                        st.error("❌ API 사용량 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
                    else:
                        st.error(f"❌ 오류가 발생했습니다: {error_msg}")

st.markdown("---")
st.markdown("<div style='text-align:center; color:gray; font-size:0.85em'>Powered by OpenAI gpt-4o-mini</div>", unsafe_allow_html=True)
