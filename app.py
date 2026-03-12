def translate_titles(titles):
    """뉴스 제목 번역 품질 강화 버전"""
    if not titles: return []
    try:
        # 제목들을 번호와 함께 나열하여 Gemini가 헷갈리지 않게 함
        context = ""
        for i, t in enumerate(titles):
            context += f"{i+1}. {t}\n"
            
        prompt = f"""
        너는 실력 있는 경제/IT 전문 번역가이자 기자야. 
        아래 영문 뉴스 제목들을 한국 독자들이 이해하기 쉽게 자연스러운 한국어 기사 제목 스타일로 번역해줘.
        
        [지침]
        1. 번호 순서대로 한 줄에 하나씩 번역문만 출력해.
        2. '의', '에' 같은 조사를 적절히 써서 한국어 문장답게 만들어.
        3. IT/경제 전문 용어는 업계에서 통용되는 단어를 사용해.
        
        [번역할 제목]
        {context}
        """
        
        response = model.generate_content(prompt)
        translated_text = response.text.strip()
        
        # 번호나 불필요한 공백을 제거하고 리스트로 변환
        translated_list = []
        for line in translated_text.split('\n'):
            # "1. 제목" 형태에서 "제목"만 추출
            clean_line = line.split('. ', 1)[-1] if '. ' in line else line
            if clean_line.strip():
                translated_list.append(clean_line.strip())
        
        return translated_list
    except Exception as e:
        st.error(f"번역 중 오류 발생: {e}")
        return titles
