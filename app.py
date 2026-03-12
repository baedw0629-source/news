import streamlit as st
import requests
import google.generativeai as genai

# 1. 모든 API 키 설정
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
NEWSAPI_KEY = st.secrets["NEWSAPI_KEY"]

# Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# 사이드바 제거 및 레이아웃 설정
st.set_page_config(page_title="경제/IT 지능형 브리핑", layout="wide", initial_sidebar_state="collapsed")

# 우측 상단 새로고침 버튼 배치를 위한 헤더 영역
head_col1, head_col2 = st.columns([8, 1])
with head_col1:
    st.title("🚀 AI 맞춤형 통합 뉴스 대시보드")
with head_col2:
    if st.button("🔄 새로고침"):
        st.rerun()

# --- 유틸리티 함수 ---

def clean_text(text):
    """HTML 태그 및 특수문자 제거"""
    return text.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&")

def get_news(query, count=20):
    """중복 제거 로직 강화 버전"""
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={count}&sort=sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        return []
    
    items = res.json().get('items', [])
    unique_news = []
    seen_keywords = set()

    for item in items:
        title = clean_text(item['title'])
        # [강력 중복 제거] 제목에서 공백 제거 후 앞 10자리를 비교 키로 사용
        # 핵심 단어가 포함된 부분을 더 넓게 잡음
        compare_key = title.replace(" ", "")[:12] 
        
        if compare_key not in seen_keywords:
            unique_news.append(item)
            seen_keywords.add(compare_key)
            
        if len(unique_news) >= 3: # 서로 다른 뉴스 3개만 확보하면 중단
            break
            
    return unique_news

def get_ai_summary(title, description):
    """3줄 요약 생성"""
    try:
        prompt = f"너는 뉴스 전문 앵커야. 아래 뉴스의 핵심 내용을 3줄로 요약해줘.\n제목: {title}\n내용: {description}"
        response = model.generate_content(prompt)
        return response.text
    except:
        return "요약 중 할당량 초과가 발생했습니다. 잠시 후 새로고침하세요."

# --- 메인 화면 레이아웃 ---

# 1. 경제 섹션
st.header("📈 오늘의 주요 경제 소식")
econ_news = get_news("경제", count=25) # 넉넉하게 25개 긁어서 중복 필터링

if econ_news:
    cols = st.columns(3)
    for i, item in enumerate(econ_news):
        with cols[i]:
            title = clean_text(item['title'])
            desc = clean_text(item['description'])
            st.subheader(title)
            with st.status("AI 자동 브리핑 생성 중...", expanded=True):
                st.write(get_ai_summary(title, desc))
            st.caption(f"[기사 원문 읽기]({item['link']})")
else:
    st.error("경제 뉴스를 불러오지 못했습니다.")

st.write("") # 간격 조절
st.divider()

# 2. IT 섹션
st.header("💻 오늘의 핵심 IT/테크")
it_news = get_news("IT 테크 최신 정보", count=25)

if it_news:
    cols_it = st.columns(3)
    for i, item in enumerate(it_news):
        with cols_it[i]:
            title = clean_text(item['title'])
            desc = clean_text(item['description'])
            st.subheader(title)
            with st.status("AI 기술 분석 중...", expanded=True):
                st.write(get_ai_summary(title, desc))
            st.caption(f"[기사 원문 읽기]({item['link']})")
