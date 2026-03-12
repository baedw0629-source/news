import streamlit as st
import requests
import google.generativeai as genai

# 1. 모든 API 키 설정
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
NEWSAPI_KEY = st.secrets["NEWSAPI_KEY"]

st.set_page_config(page_title="데일리 뉴스 헤드라인", layout="wide")

# 헤더 및 새로고침 버튼
head_col1, head_col2 = st.columns([10, 1])
with head_col1:
    st.title("📰 오늘의 핵심 뉴스 헤드라인")
with head_col2:
    if st.button("🔄 새로고침"):
        st.rerun()

def clean_text(text):
    """HTML 태그 제거"""
    if not text: return ""
    return text.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&")

def get_unique_news(items, count=3):
    """제목 기준 중복 제거 로직"""
    unique_list = []
    seen_titles = set()
    
    for item in items:
        # 네이버와 NewsAPI의 필드명이 다르므로 처리
        title = clean_text(item.get('title', ''))
        link = item.get('link') if item.get('link') else item.get('url')
        
        # 제목 앞 10자리가 겹치면 중복으로 간주
        title_key = title.replace(" ", "")[:10]
        if title_key not in seen_titles and title:
            unique_list.append({'title': title, 'link': link})
            seen_titles.add(title_key)
            
        if len(unique_list) >= count:
            break
    return unique_list

# 1. 국내 뉴스 가져오기 (네이버)
def get_domestic_news():
    url = "https://openapi.naver.com/v1/search/news.json?query=경제&display=15&sort=sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return get_unique_news(res.json().get('items', []))
    return []

# 2. 해외 뉴스 가져오기 (NewsAPI)
def get_global_news():
    # 세계 주요 뉴스(Top Headlines) 가져오기
    url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWSAPI_KEY}"
    res = requests.get(url)
    if res.status_code == 200:
        return get_unique_news(res.json().get('articles', []))
    return []

# --- 화면 출력 ---
col_dom, col_glo = st.columns(2)

with col_dom:
    st.header("🇰🇷 국내 주요 뉴스 (경제)")
    domestic = get_domestic_news()
    if domestic:
        for i, news in enumerate(domestic):
            st.subheader(f"{i+1}. {news['title']}")
            st.write(f"[기사 보기]({news['link']})")
            st.write("")
    else:
        st.write("국내 뉴스를 불러올 수 없습니다.")

with col_glo:
    st.header("🌎 해외 주요 뉴스 (Business)")
    global_news = get_global_news()
    if global_news:
        for i, news in enumerate(global_news):
            st.subheader(f"{i+1}. {news['title']}")
            st.write(f"[Original Link]({news['link']})")
            st.write("")
    else:
        st.write("해외 뉴스를 불러올 수 없습니다. (API 키 확인 필요)")

st.divider()
st.caption("AI 요약 기능을 제외하여 할당량 제한 없이 실시간 뉴스를 빠르게 제공합니다.")
