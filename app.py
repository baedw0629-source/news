import streamlit as st
import requests

# 1. 모든 API 키 설정
NAVER_CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
NAVER_CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
NEWSAPI_KEY = st.secrets["NEWSAPI_KEY"]

# 페이지 설정: 와이드 모드 및 사이드바 숨김
st.set_page_config(page_title="종합 뉴스 대시보드", layout="wide", initial_sidebar_state="collapsed")

# CSS로 글자 크기 및 간격 미세 조정
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 1rem; }
    h1 { font-size: 28px !important; }
    h2 { font-size: 22px !important; border-bottom: 2px solid #f0f2f6; padding-bottom: 5px; }
    h3 { font-size: 16px !important; line-height: 1.4 !important; margin-bottom: 5px !important; }
    .stCaption { font-size: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# 헤더
head_col1, head_col2 = st.columns([10, 1])
head_col1.title("핵심 뉴스 브리핑 (경제 · IT)")
if head_col2.button("🔄 새로고침"):
    st.rerun()

def clean_text(text):
    if not text: return ""
    return text.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&")

def get_unique_news(items, title_key, link_key, count=3):
    """중복 제거 로직 강화: 제목의 공백을 제거하고 앞부분 15자리를 비교"""
    unique = []
    seen_keys = set()
    
    for item in items:
        title = clean_text(item.get(title_key, ""))
        link = item.get(link_key, "")
        if not title: continue
        
        # 중복 판단 키: 공백 제거 후 앞 15글자 추출 (매우 엄격함)
        match_key = title.replace(" ", "")[:15]
        
        if match_key not in seen_keys:
            unique.append({'title': title, 'link': link})
            seen_keys.add(match_key)
            
        if len(unique) >= count:
            break
    return unique

# 뉴스 데이터 가져오기 함수들
def fetch_naver(query):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=20&sort=sim"
    res = requests.get(url, headers={"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET})
    return res.json().get('items', []) if res.status_code == 200 else []

def fetch_global(category):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&language=en&apiKey={NEWS_API_KEY}"
    res = requests.get(url)
    return res.json().get('articles', []) if res.status_code == 200 else []

# --- 1행: 경제 섹션 ---
st.header("📈 경제 (Economy)")
e_col1, e_col2 = st.columns(2)

with e_col1:
    st.subheader("🇰🇷 국내 경제")
    for i, n in enumerate(get_unique_news(fetch_naver("경제"), 'title', 'link')):
        st.markdown(f"**{i+1}.** [{n['title']}]({n['link']})")

with e_col2:
    st.subheader("🌎 해외 경제 (Biz)")
    for i, n in enumerate(get_unique_news(fetch_global("business"), 'title', 'url')):
        st.markdown(f"**{i+1}.** [{n['title']}]({n['link']})")

st.write("---")

# --- 2행: IT 섹션 ---
st.header("💻 IT · 테크 (Technology)")
t_col1, t_col2 = st.columns(2)

with t_col1:
    st.subheader("🇰🇷 국내 IT")
    for i, n in enumerate(get_unique_news(fetch_naver("IT 기술 테크"), 'title', 'link')):
        st.markdown(f"**{i+1}.** [{n['title']}]({n['link']})")

with t_col2:
    st.subheader("🌎 해외 IT")
    for i, n in enumerate(get_unique_news(fetch_global("technology"), 'title', 'url')):
        st.markdown(f"**{i+1}.** [{n['title']}]({n['link']})")
