import streamlit as st
import requests

# 1. API 키 설정
try:
    NAVER_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
    NEWS_API_KEY = st.secrets["NEWSAPI_KEY"]
except Exception:
    st.error("Secrets 설정 확인 필요")
    st.stop()

st.set_page_config(page_title="종합 뉴스 대시보드", layout="wide", initial_sidebar_state="collapsed")

# 레이아웃 스타일
st.markdown("""
    <style>
    h1 { font-size: 24px !important; margin-bottom: 0px; }
    h2 { font-size: 18px !important; color: #1f77b4; margin-top: 10px; border-bottom: 1px solid #ddd; }
    h3 { font-size: 15px !important; margin-top: 5px; }
    .news-box { padding: 5px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 헤더 영역
h_col1, h_col2 = st.columns([10, 1])
h_col1.title("📰 뉴스 브리핑 (경제 · IT)")
if h_col2.button("🔄 새로고침"):
    st.rerun()

def clean_text(text):
    if not text: return ""
    return text.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&")

def get_strong_unique_news(items, title_key, link_key, count=3):
    """제목의 핵심 단어를 추출하여 중복을 원천 차단하는 로직"""
    unique_news = []
    seen_word_sets = []
    
    for item in items:
        title = clean_text(item.get(title_key, ""))
        link = item.get(link_key, "")
        
        # 제목에서 2글자 이상의 단어만 추출 (조사 제외 목적)
        words = set([w for w in title.split() if len(w) >= 2])
        
        # 기존에 저장된 뉴스 단어셋들과 비교
        is_dup = False
        for existing_set in seen_word_sets:
            # 단어가 2개 이상 겹치면 같은 뉴스라고 판단
            if len(words.intersection(existing_set)) >= 2:
                is_dup = True
                break
        
        if not is_dup:
            unique_news.append({'title': title, 'link': link})
            seen_word_sets.append(words)
            
        if len(unique_news) >= count:
            break
    return unique_news

def fetch_naver(query):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=30&sort=sim"
    headers = {"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', []) if res.status_code == 200 else []

def fetch_global(category):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&language=en&apiKey={NEWS_API_KEY}"
    res = requests.get(url)
    return res.json().get('articles', []) if res.status_code == 200 else []

# --- 대시보드 배치 ---
# 1행: 경제
st.header("📈 경제 (Economy)")
e_col1, e_col2 = st.columns(2)
with e_col1:
    st.subheader("🇰🇷 국내 주요 경제")
    for i, n in enumerate(get_strong_unique_news(fetch_naver("경제"), 'title', 'link')):
        st.markdown(f"**{i+1}.** [{n['title']}]({n['link']})")
with e_col2:
    st.subheader("🌎 해외 Business")
    for i, n in enumerate(get_strong_unique_news(fetch_global("business"), 'title', 'url')):
        st.markdown(f"**{i+1}.** [{n['title']}]({n['link']})")

# 2행: IT
st.header("💻 IT · 테크 (Technology)")
t_col1, t_col2 = st.columns(2)
with t_col1:
    st.subheader("🇰🇷 국내 IT 소식")
    for i, n in enumerate(get_strong_unique_news(fetch_naver("IT 기술 테크"), 'title', 'link')):
        st.markdown(f"**{i+1}.** [{n['title']}]({n['link']})")
with t_col2:
    st.subheader("🌎 해외 Tech")
    for i, n in enumerate(get_strong_unique_news(fetch_global("technology"), 'title', 'url')):
        st.markdown(f"**{i+1}.** [{n['title']}]({n['link']})")
