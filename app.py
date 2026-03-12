import streamlit as st
import requests

# 1. 모든 API 키 설정
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
NEWSAPI_KEY = st.secrets["NEWSAPI_KEY"]

st.set_page_config(page_title="데일리 뉴스 헤드라인", layout="wide")
st.title("📰 오늘의 핵심 뉴스 (국내/해외)")

# 우측 상단 새로고침
_, btn_col = st.columns([10, 1])
if btn_col.button("🔄 새로고침"):
    st.rerun()

def get_unique_titles(items, title_key, link_key, count=3):
    unique = []
    seen = set()
    for item in items:
        title = item[title_key].replace("<b>", "").replace("</b>", "").replace("&quot;", '"')
        # 중복 판단: 앞 12글자 비교
        short_title = title.replace(" ", "")[:12]
        if short_title not in seen:
            unique.append({'title': title, 'link': item[link_key]})
            seen.add(short_title)
        if len(unique) >= count: break
    return unique

# 레이아웃
col1, col2 = st.columns(2)

# 국내 뉴스 (네이버)
with col1:
    st.header("🇰🇷 국내 경제 TOP 3")
    res = requests.get("https://openapi.naver.com/v1/search/news.json?query=경제&display=15", 
                       headers={"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET})
    if res.status_code == 200:
        for i, n in enumerate(get_unique_titles(res.json()['items'], 'title', 'link')):
            st.subheader(f"{i+1}. {n['title']}")
            st.caption(f"[기사 보기]({n['link']})")
    else: st.error("국내 뉴스 로드 실패")

# 해외 뉴스 (NewsAPI)
with col2:
    st.header("🌎 해외 비즈니스 TOP 3")
    res = requests.get(f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWS_API_KEY}")
    if res.status_code == 200:
        for i, n in enumerate(get_unique_titles(res.json()['articles'], 'title', 'url')):
            st.subheader(f"{i+1}. {n['title']}")
            st.caption(f"[Read More]({n['link']})")
    else: st.error("해외 뉴스 로드 실패 (API 키 확인)")
