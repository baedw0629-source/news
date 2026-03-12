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

# 헤더 및 새로고침 버튼
head_col1, head_col2 = st.columns([10, 1])
with head_col1:
    st.title("🚀 AI 맞춤형 통합 뉴스 대시보드")
with head_col2:
    if st.button("🔄 새로고침"):
        st.rerun()

def clean_text(text):
    return text.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&")

def get_raw_news(query, count=10):
    """네이버에서 뉴스 원본 데이터를 넉넉히 가져옴"""
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={count}&sort=sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', []) if res.status_code == 200 else []

def get_combined_summary(news_list):
    """뉴스 리스트를 통째로 넘겨서 중복 제거 후 통합 요약 (요청 횟수 절감)"""
    if not news_list: return "뉴스가 없습니다."
    
    # AI에게 보낼 텍스트 구성
    context = ""
    for i, item in enumerate(news_list):
        context += f"기사{i+1}\n제목: {item['title']}\n내용: {item['description']}\n\n"
    
    prompt = f"""
    아래 뉴스 리스트를 보고 다음 규칙에 따라 리포트해줘:
    1. 비슷한 내용의 기사는 하나로 통합해라.
    2. 가장 중요한 서로 다른 주제 3가지를 선정해라.
    3. 각 주제별로 핵심 내용을 한국어 3줄로 요약해라.
    4. 출력 형식: 
       ### [주제 제목]
       - 요약문1
       - 요약문2
       - 요약문3
    
    뉴스 리스트:
    {context}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ 현재 AI 사용량이 많습니다. 1분만 기다렸다가 새로고침해 주세요."
        return "⚠️ 요약 생성 중 오류가 발생했습니다."

# --- 섹션별 출력 ---
sections = [("📈 오늘의 주요 경제 소식", "경제"), ("💻 오늘의 핵심 IT/테크", "IT 테크 최신")]

for section_title, query in sections:
    st.header(section_title)
    raw_news = get_raw_news(query)
    
    if raw_news:
        with st.status(f"{section_title} 분석 중...", expanded=True):
            # 섹션당 1번만 AI 호출 (경제 1번, IT 1번 = 총 2번 호출로 끝!)
            summary_result = get_combined_summary(raw_news)
            st.markdown(summary_result)
            
            # 원문 링크들을 모아서 아래에 작게 표시
            with st.expander("🔗 관련 기사 원문 보기"):
                for item in raw_news[:5]:
                    st.caption(f"[{clean_text(item['title'])}]({item['link']})")
    st.divider()
