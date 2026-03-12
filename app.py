import streamlit as st
import requests
import google.generativeai as genai
import random

# 1. API 키 및 모델 설정
try:
    NAVER_ID = st.secrets["NAVER_CLIENT_ID"]
    NAVER_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
    NEWS_API_KEY = st.secrets["NEWSAPI_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Secrets 설정(API 키)을 확인해주세요.")
    st.stop()

# Gemini 설정 (번역 품질을 위해 최신 모델 권장)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# 페이지 설정
st.set_page_config(page_title="종합 뉴스 대시보드", layout="wide", initial_sidebar_state="collapsed")

# 디자인 개선 (CSS)
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; }
    h1 { font-size: 28px !important; color: #0E1117; margin-bottom: 5px; }
    h2 { font-size: 20px !important; color: #1f77b4; border-bottom: 2px solid #1f77b4; padding-bottom: 5px; margin-top: 20px; }
    h3 { font-size: 16px !important; color: #333; margin-top: 10px; }
    .news-card { background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #1f77b4; }
    a { text-decoration: none; color: #1f77b4; font-weight: bold; }
    a:hover { color: #ff4b4b; text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

# 헤더
h_col1, h_col2 = st.columns([9, 1.5])
h_col1.title("🚀 AI 맞춤형 실시간 뉴스 브리핑")
if h_col2.button("🔄 새로운 뉴스 보기"):
    st.rerun()

def clean_text(text):
    if not text: return ""
    return text.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&")

def translate_titles(titles):
    """뉴스 제목 번역 품질 강화 및 후처리 로직"""
    if not titles: return []
    try:
        context = ""
        for i, t in enumerate(titles):
            context += f"{i+1}. {t}\n"
            
        prompt = f"""
        너는 실력 있는 경제/IT 전문 번역가이자 베테랑 기자야. 
        아래 영문 뉴스 제목들을 한국 독자들이 읽기 편하게 자연스러운 '한국어 기사 제목 스타일'로 번역해줘.
        
        [지침]
        1. 번호 순서대로 한 줄에 하나씩 번역문만 출력해.
        2. '의', '에' 같은 조사를 적절히 써서 문장이 매끄럽게 들리도록 해.
        3. IT/경제 전문 용어(예: 엔비디아, 연준, 금리 인상 등)는 표준화된 용어를 사용해.
        4. 원문의 뉘앙스를 살리되, 한국 신문 헤드라인처럼 간결하게 다듬어줘.
        
        [번역할 리스트]
        {context}
        """
        
        response = model.generate_content(prompt)
        translated_text = response.text.strip()
        
        # 줄 단위로 나누고 번호(1. ) 제거 작업
        translated_list = []
        for line in translated_text.split('\n'):
            clean_line = line.split('. ', 1)[-1] if '. ' in line else line
            if clean_line.strip():
                translated_list.append(clean_line.strip())
        
        return translated_list
    except:
        return titles # 실패 시 영문 그대로 반환

def get_unique_news(items, title_key, link_key, count=3, is_global=False):
    """핵심 단어 분석 중복 제거 로직"""
    unique_news = []
    seen_word_sets = []
    
    # 해외 뉴스의 경우 먼저 상위 10개만 번역해서 가져옴
    translated_titles = []
    if is_global:
        raw_titles = [item.get(title_key, "") for item in items[:10]]
        translated_titles = translate_titles(raw_titles)
    
    for i, item in enumerate(items):
        title = translated_titles[i] if is_global and i < len(translated_titles) else clean_text(item.get(title_key, ""))
        link = item.get(link_key, "")
        if not title or len(title) < 5: continue
        
        # 단어 기반 중복 체크 (핵심 키워드 2개 이상 겹치면 중복)
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
    # 랜덤하게 다른 결과를 가져오기 위해 start 위치 조정
    start_pos = random.randint(1, 50)
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=25&start={start_pos}&sort=sim"
    res = requests.get(url, headers={"X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET})
    return res.json().get('items', []) if res.status_code == 200 else []

def fetch_global(category):
    # 페이지를 랜덤하게 선택하여 매번 다른 뉴스 노출
    page_num = random.randint(1, 3)
    url = f"https://newsapi.org/v2/top-headlines?category={category}&language=en&pageSize=20&page={page_num}&apiKey={NEWS_API_KEY}"
    res = requests.get(url)
    return res.json().get('articles', []) if res.status_code == 200 else []

# --- 섹션 1: 경제 ---
st.header("📈 경제 섹션 (Economy)")
e_col1, e_col2 = st.columns(2)

with e_col1:
    st.subheader("🇰🇷 국내 주요 경제")
    for i, n in enumerate(get_unique_news(fetch_naver("경제"), 'title', 'link')):
        st.markdown(f"<div class='news-card'>{i+1}. <a href='{n['link']}' target='_blank'>{n['title']}</a></div>", unsafe_allow_html=True)

with e_col2:
    st.subheader("🌎 해외 Business (번역)")
    for i, n in enumerate(get_unique_news(fetch_global("business"), 'title', 'url', is_global=True)):
        st.markdown(f"<div class='news-card'>{i+1}. <a href='{n['link']}' target='_blank'>{n['title']}</a></div>", unsafe_allow_html=True)

st.write("")

# --- 섹션 2: IT ---
st.header("💻 IT · 테크 섹션 (Technology)")
t_col1, t_col2 = st.columns(2)

with t_col1:
    st.subheader("🇰🇷 국내 IT 소식")
    for i, n in enumerate(get_unique_news(fetch_naver("IT 과학 기술"), 'title', 'link')):
        st.markdown(f"<div class='news-card'>{i+1}. <a href='{n['link']}' target='_blank'>{n['title']}</a></div>", unsafe_allow_html=True)

with t_col2:
    st.subheader("🌎 해외 Tech (번역)")
    for i, n in enumerate(get_unique_news(fetch_global("technology"), 'title', 'url', is_global=True)):
        st.markdown(f"<div class='news-card'>{i+1}. <a href='{n['link']}' target='_blank'>{n['title']}</a></div>", unsafe_allow_html=True)
