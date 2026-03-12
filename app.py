import streamlit as st
import requests
import google.generativeai as genai
import random

# 1. API 키 설정
try:
    NAVER_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
    NEWS_API_KEY = st.secrets["NEWSAPI_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Secrets 설정 확인 필요")
    st.stop()

# Gemini 설정 (번역용)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

st.set_page_config(page_title="종합 뉴스 대시보드", layout="wide", initial_sidebar_state="collapsed")

# 스타일 설정
st.markdown("""
    <style>
    h1 { font-size: 26px !important; margin-bottom: 0px; color: #1E1E1E; }
    h2 { font-size: 20px !important; color: #1f77b4; margin-top: 15px; border-bottom: 2px solid #1f77b4; padding-bottom: 5px; }
    h3 { font-size: 16px !important; margin-top: 10px; color: #333; }
    .news-link { text-decoration: none; color: #31333F; font-weight: 500; }
    .news-link:hover { color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 헤더
h_col1, h_col2 = st.columns([10, 1.2])
h_col1.title("🚀 실시간 경제 · IT 뉴스 커스텀 브리핑")
if h_col2.button("🔄 새로운 뉴스"):
    st.rerun()

def clean_text(text):
    if not text: return ""
    return text.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&")

def translate_titles(titles):
    """영어 제목 리스트를 한 번에 번역 (할당량 절약)"""
    if not titles: return []
    try:
        context = "\n".join(titles)
        prompt = f"다음 뉴스 제목들을 문맥에 맞게 자연스러운 한국어로 번역해줘. 리스트 순서대로 번역문만 한 줄씩 출력해:\n\n{context}"
        response = model.generate_content(prompt)
        return response.text.strip().split("\n")
    except:
        return titles # 실패 시 영어 그대로 노출

def get_unique_news(items, title_key, link_key, count=3, is_global=False):
    """강력한 중복 제거 로직"""
    unique_news = []
    seen_word_sets = []
    
    # 해외 뉴스의 경우 번역 전 원문 제목들을 리스트로 추출
    if is_global:
        raw_titles = [item.get(title_key, "") for item in items]
        translated_titles = translate_titles(raw_titles[:10]) # 상위 10개만 번역 시도
    
    for i, item in enumerate(items):
        title = translated_titles[i] if is_global and i < len(translated_titles) else clean_text(item.get(title_key, ""))
        link = item.get(link_key, "")
        
        words = set([w for w in title.split() if len(w) >= 2])
        is_dup = False
        for s in seen_word_sets:
            if len(words.intersection(s)) >= 2:
                is_dup = True; break
        
        if not is_dup:
            unique_news.append({'title': title, 'link': link})
            seen_word_sets.append(words)
        if len(unique_news) >= count: break
    return unique_news

def fetch_naver(query):
    # 랜덤 페이지 설정을 위해 start 값을 1~50 중 랜덤 선택
    start_pos = random.randint(1, 50)
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=20&start={start_pos}&sort=sim"
    res = requests.get(url, headers={"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET})
    return res.json().get('items', []) if res.status_code == 200 else []

def fetch_global(category):
    # NewsAPI는 page 파라미터로 랜덤성 부여
    page = random.randint(1, 3)
    url = f"https://newsapi.org/v2/top-headlines?category={category}&language=en&pageSize=20&page={page}&apiKey={NEWS_API_KEY}"
    res = requests.get(url)
    return res.json().get('articles', []) if res.status_code == 200 else []

# --- 화면 출력 ---
for sec, q, cat in [("📈 경제 (Economy)", "경제", "business"), ("💻 IT · 테크 (Technology)", "IT 과학 기술", "technology")]:
    st.header(sec)
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🇰🇷 국내 소식")
        for i, n in enumerate(get_unique_news(fetch_naver(q), 'title', 'link')):
            st.markdown(f"**{i+1}.** <a class='news-link' href='{n['link']}' target='_blank'>{n['title']}</a>", unsafe_allow_html=True)
            
    with c2:
        st.subheader("🌎 해외 소식 (번역)")
        for i, n in enumerate(get_unique_news(fetch_global(cat), 'title', 'url', is_global=True)):
            st.markdown(f"**{i+1}.** <a class='news-link' href='{n['link']}' target='_blank'>{n['title']}</a>", unsafe_allow_html=True)
    st.write("")
