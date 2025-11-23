import requests
from bs4 import BeautifulSoup
from collections import Counter
from konlpy.tag import Okt

def get_all_headlines(url, tag, class_name):
    """
    뉴스 목록 페이지에서 모든 기사 제목을 수집하는 함수.
    
    Parameters:
        url (str): 뉴스 목록 페이지 URL
        tag (str): 뉴스 제목을 감싸고 있는 HTML 태그 이름 (예: "strong")
        class_name (str): 뉴스 제목 태그의 클래스 이름 (예: "sa_text_strong")
        
    Returns:
        list: 모든 기사 제목 리스트
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 페이지에 있는 모든 기사 제목 수집
    headlines = [title.text for title in soup.find_all(tag, class_=class_name)]
    return headlines

def extract_phrases(texts):
    """
    기사 제목 리스트에서 연속된 명사 구를 추출하여 키워드를 생성하는 함수.
    
    Parameters:
        texts (list): 기사 제목 리스트
        
    Returns:
        list: 추출된 주요 키워드 구 리스트
    """
    okt = Okt()
    phrases = []

    for text in texts:
        # 형태소 분석
        words = okt.pos(text, norm=True, stem=True)
        
        # 연속된 명사 구 추출
        phrase = []
        for word, pos in words:
            if pos == "Noun":  # 명사일 경우
                phrase.append(word)
            else:
                if len(phrase) > 1:  # 2개 이상의 연속된 명사일 때만 추가
                    phrases.append(" ".join(phrase))
                phrase = []  # 초기화
        if len(phrase) > 1:
            phrases.append(" ".join(phrase))  # 마지막 구도 추가
    
    return phrases

def get_top_phrases(headlines, top_n=5):
    """
    기사 제목 리스트에서 가장 많이 언급된 상위 N개의 키워드 구를 반환하는 함수.
    
    Parameters:
        headlines (list): 기사 제목 리스트
        top_n (int): 상위 몇 개의 키워드를 반환할지 설정 (기본값: 5)
        
    Returns:
        list: 상위 N개의 키워드 구와 빈도수 리스트
    """
    phrases = extract_phrases(headlines)
    phrase_counts = Counter(phrases)
    return phrase_counts.most_common(top_n)

# 메인 실행
# 뉴스 목록 페이지 URL 및 해당 페이지 구조의 태그 이름과 클래스 이름 설정
url = "https://media.naver.com/press/015?sid=101"  # 네이버 뉴스 메인 또는 특정 뉴스 목록 페이지 URL
tag = "span"  # 뉴스 제목을 감싸고 있는 태그 이름 입력
class_name = "press_edit_news_title"  # 뉴스 제목 태그의 클래스 이름 입력

# 모든 기사 제목 수집 및 키워드 분석
headlines = get_all_headlines(url, tag, class_name)
print("수집된 제목 개수:", len(headlines))
print("예시 제목 3개:", headlines[:3])
top_phrases = get_top_phrases(headlines)

print("오늘의 주요 키워드 구:", top_phrases)
