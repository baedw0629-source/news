import streamlit as st
import requests
import google.generativeai as genai

# 1. 모든 API 키 설정
NAVER_CLIENT_ID = "gSg91KNBvsNYAeTYW5o3"
NAVER_CLIENT_SECRET = "wusIlWS8Dz"
GEMINI_API_KEY = "AIzaSyDIv7Zm_XQBwyzuDOdgf_-DzUt5BbcE_BI"
NEWSAPI_KEY = "NEWSAPI_키387c37399be0430087a289dd2acb11d1"
# Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

st.set_page_config(page_title="경제/IT 지능형 브리핑", layout="wide")
st.title("🚀 AI 맞춤형 통합 뉴스 대시보드")

# --- 유틸리티 함수 ---

def clean_text(text):
    """HTML 태그 및 특수문자 제거"""
    return text.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&apos;", "'")

def get_news(query, count=10):
    """네이버 뉴스 가져오기 및 중복 제거"""
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={count}&sort=sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        return []
    
    items = res.json().get('items', [])
    unique_news = []
    seen_titles = set()

    for item in items:
        title = clean_text(item['title'])
        # 제목 앞 15글자 정도가 겹치면 중복으로 간주 (지능형 필터링)
        title_summary = title[:15].replace(" ", "")
        if title_summary not in seen_titles:
            unique_news.append(item)
            seen_titles.add(title_summary)
            
    return unique_news[:3] # 최종적으로 서로 다른 뉴스 3개만 반환

def get_ai_summary(title, description):
    """3줄 요약 생성"""
    try:
        prompt = f"너는 전문 뉴스 브리핑 비서야. 아래 뉴스를 핵심만 3줄 요약해줘.\n제목: {title}\n내용: {description}"
        response = model.generate_content(prompt)
        return response.text
    except:
        return "요약 중 할당량 초과가 발생했습니다. 잠시 후 새로고침하세요."

# --- 메인 화면 ---

# 1. 경제 섹션
st.header("📈 오늘의 주요 경제 소식")
econ_news = get_news("경제", count=15) # 15개 중 중복 제거 후 3개 추출

if econ_news:
    cols = st.columns(3)
    for i, item in enumerate(econ_news):
        with cols[i]:
            title = clean_text(item['title'])
            desc = clean_text(item['description'])
            st.subheader(title)
            with st.status("AI 자동 브리핑 생성 중..."):
                st.write(get_ai_summary(title, desc))
            st.caption(f"[기사 원문 읽기]({item['link']})")
else:
    st.error("경제 뉴스를 불러오지 못했습니다.")

st.divider()

# 2. IT 섹션
st.header("💻 오늘의 핵심 IT/테크")
it_news = get_news("IT 테크 최신 정보", count=15)

if it_news:
    cols_it = st.columns(3)
    for i, item in enumerate(it_news):
        with cols_it[i]:
            title = clean_text(item['title'])
            desc = clean_text(item['description'])
            st.subheader(title)
            with st.status("AI 기술 분석 중..."):
                st.write(get_ai_summary(title, desc))
            st.caption(f"[기사 원문 읽기]({item['link']})")
else:
    st.info("IT 섹션 데이터를 불러오는 중이거나 결과가 없습니다.")

# 새로고침 버튼
if st.sidebar.button("🔄 전체 뉴스 새로고침"):
    st.rerun()