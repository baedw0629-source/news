import streamlit as st
import requests
import google.generativeai as genai

# 1. 모든 API 키 설정
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
NEWSAPI_KEY = st.secrets["NEWSAPI_KEY"]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

st.set_page_config(page_title="경제/IT 지능형 브리핑", layout="wide", initial_sidebar_state="collapsed")

# 우측 상단 새로고침 버튼
head_col1, head_col2 = st.columns([10, 1])
with head_col1:
    st.title("🚀 AI 맞춤형 통합 뉴스 대시보드")
with head_col2:
    if st.button("🔄 새로고침"):
        st.rerun()

def clean_text(text):
    return text.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&")

def is_duplicate(new_title, seen_sets):
    """단어 집합 비교를 통한 중복 체크"""
    # 2글자 이상의 단어만 추출하여 집합으로 만듦
    new_words = set([word for word in new_title.split() if len(word) >= 2])
    
    for seen_words in seen_sets:
        # 이미 본 뉴스 단어들과 현재 뉴스 단어들의 교집합 확인
        intersection = new_words.intersection(seen_words)
        # 핵심 단어가 3개 이상 겹치면 중복으로 간주
        if len(intersection) >= 3:
            return True
    return False

def get_news(query, count=30):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={count}&sort=sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        return []
    
    items = res.json().get('items', [])
    unique_news = []
    seen_sets = []

    for item in items:
        title = clean_text(item['title'])
        if not is_duplicate(title, seen_sets):
            unique_news.append(item)
            # 현재 기사의 단어 집합을 저장
            current_words = set([word for word in title.split() if len(word) >= 2])
            seen_sets.append(current_words)
            
        if len(unique_news) >= 3:
            break
            
    return unique_news

def get_ai_summary(title, description):
    try:
        # 할당량 초과 방지를 위한 간결한 프롬프트
        prompt = f"핵심요약 3줄(번호없이):\n제목:{title}\n내용:{description}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ 할당량 초과! 1분만 기다려주세요."
        return "⚠️ 요약 실패"

# --- 화면 출력 ---
for section_title, query in [("📈 오늘의 주요 경제 소식", "경제"), ("💻 오늘의 핵심 IT/테크", "IT 테크 최신")]:
    st.header(section_title)
    news_list = get_news(query)
    
    if news_list:
        cols = st.columns(3)
        for i, item in enumerate(news_list):
            with cols[i]:
                title = clean_text(item['title'])
                desc = clean_text(item['description'])
                st.subheader(title)
                # 즉시 실행하되 실패 시 메시지 처리
                summary_area = st.empty()
                with st.spinner("요약 중..."):
                    summary = get_ai_summary(title, desc)
                    summary_area.info(summary)
                st.caption(f"[기사 원문 읽기]({item['link']})")
    st.divider()
