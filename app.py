import streamlit as st
import requests

# 1. API 키 설정 (가장 먼저 수행)
# Streamlit Cloud의 Secrets에 적은 이름과 정확히 일치해야 합니다.
try:
    NAVER_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
    NEWS_API_KEY = st.secrets["NEWSAPI_KEY"]
except Exception as e:
    st.error("API 키를 찾을 수 없습니다. Secrets 설정을 확인하세요.")
    st.stop() # 키가 없으면 실행 중단

# 페이지 설정
st.set_page_config(page_title="종합 뉴스 대시보드", layout="wide", initial_sidebar_state="collapsed")

# CSS: 글자 크기 줄이기 및 화면 최적화
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 1rem; }
    h1 { font-size: 24px !important; }
    h2 { font-size: 18px !important; color: #1f77b4; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
    .news-item { font-size: 14px !important; margin-bottom: 8px; line-height: 1.4; }
    a { text-decoration: none; color: #31333F; font-weight: 500; }
    a:hover { color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 헤더
head_col1, head_col2 = st.columns([10, 1.2])
head_col1.title("📰 실시간 핵심 뉴스 (경제 · IT)")
if head_col2.button("🔄 새로고침"):
    st.rerun()

def clean_text(text):
    if not text: return ""
    return text.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&")

def get_unique_news(items, title_key, link_key, count=3):
    """중복 제거 로직 강화: 공백 제거 후 15자 비교"""
    unique = []
    seen_keys = set()
    
    for item in items:
        title = clean_text(item.get(title_key, ""))
        link = item.get(link_key, "")
        if not title: continue
        
        # 중복 판단 키: 공백 제거 후 앞 15글자 (이게 같으면 같은 뉴스로 취급)
        match_key = title.replace(" ", "")[:15]
        
        if match_key not in seen_keys:
            unique.append({'title': title, 'link': link})
            seen_keys.add(match_key)
            
        if len(unique) >= count:
            break
    return unique

# 뉴스 가져오기 함수들 (상단에 정의된 NAVER_ID 사용)
def fetch_naver(query):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=20&sort=sim"
    # 여기서 NAVER_ID와 NAVER_SECRET을 정확히 사용합니다.
    headers = {"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', []) if res.status_code == 200 else []

def fetch_global(category):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&language=en&apiKey={NEWS_API_KEY}"
    res = requests.get(url)
    return res.json().get('articles', []) if res.status_code == 200 else []

# --- 대시보드 화면 구성 (4분할) ---

# 1. 경제 섹션
st.header("📈 경제 (Economy)")
e_col1, e_col2 = st.columns(2)

with e_col1:
    st.subheader("🇰🇷 국내 주요 경제")
    news = get_unique_news(fetch_naver("경제"), 'title', 'link')
    for i, n in enumerate(news):
        st.markdown(f"<div class='news-item'>{i+1}. <a href='{n['link']}' target='_blank'>{n['title']}</a></div>", unsafe_allow_html=True)

with e_col2:
    st.subheader("🌎 해외 Business")
    news = get_unique_news(fetch_global("business"), 'title', 'url')
    for i, n in enumerate(news):
        st.markdown(f"<div class='news-item'>{i+1}. <a href='{n['link']}' target='_blank'>{n['title']}</a></div>", unsafe_allow_html=True)

st.write("") # 간격

# 2. IT 섹션
st.header("💻 IT · 테크 (Technology)")
t_col1, t_col2 = st.columns(2)

with t_col1:
    st.subheader("🇰🇷 국내 IT 소식")
    news = get_unique_news(fetch_naver("IT 과학 기술"), 'title', 'link')
    for i, n in enumerate(news):
        st.markdown(f"<div class='news-item'>{i+1}. <a href='{n['link']}' target='_blank'>{n['title']}</a></div>", unsafe_allow_html=True)

with t_col2:
    st.subheader("🌎 해외 Tech")
    news = get_unique_news(fetch_global("technology"), 'title', 'url')
    for i, n in enumerate(news):
        st.markdown(f"<div class='news-item'>{i+1}. <a href='{n['link']}' target='_blank'>{n['title']}</a></div>", unsafe_allow_html=True)
