import requests
from bs4 import BeautifulSoup
from collections import Counter
from konlpy.tag import Okt

# --------------------------------------------------
# 1) 공통: 기사 제목 수집 함수
# --------------------------------------------------
def get_all_headlines(url, tag, class_name):
    """
    뉴스 목록 페이지에서 모든 기사 제목을 수집하는 함수.
    
    Parameters:
        url (str): 뉴스 목록 페이지 URL
        tag (str): 뉴스 제목을 감싸고 있는 HTML 태그 이름
        class_name (str): 뉴스 제목 태그의 클래스 이름
        
    Returns:
        list[str]: 모든 기사 제목 리스트
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[오류] 페이지 요청 실패: {url} -> {e}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = [title.get_text(strip=True) for title in soup.find_all(tag, class_=class_name)]
    return headlines

# --------------------------------------------------
# 2) 공통: 2단어 이상 명사구 추출
# --------------------------------------------------
def extract_phrases(texts):
    """
    기사 제목 리스트에서 '연속된 명사 구(2단어 이상)'만 추출.
    
    Parameters:
        texts (list[str]): 기사 제목 리스트
        
    Returns:
        list[str]: 추출된 주요 키워드 구 리스트
    """
    okt = Okt()
    phrases = []

    for text in texts:
        words = okt.pos(text, norm=True, stem=True)

        phrase = []
        for word, pos in words:
            if pos == "Noun":  # 명사일 경우 계속 이어붙이기
                phrase.append(word)
            else:
                # ★ 2개 이상의 연속된 명사일 때만 추가 (서행하다님 의도 유지)
                if len(phrase) > 1:
                    phrases.append(" ".join(phrase))
                phrase = []

        # 문장 끝에 남아있는 명사 구 처리
        if len(phrase) > 1:
            phrases.append(" ".join(phrase))

    return phrases

# --------------------------------------------------
# 3) 공통: 상위 키워드 구 계산
# --------------------------------------------------
def get_top_phrases(headlines, top_n=10):
    """
    기사 제목 리스트에서 가장 많이 언급된 상위 N개의 키워드 구를 반환.
    
    Parameters:
        headlines (list[str]): 기사 제목 리스트
        top_n (int): 상위 몇 개의 키워드를 반환할지
        
    Returns:
        list[tuple[str, int]]: (키워드 구, 빈도수) 튜플 리스트
    """
    phrases = extract_phrases(headlines)
    if not phrases:
        return []

    phrase_counts = Counter(phrases)
    return phrase_counts.most_common(top_n)

# --------------------------------------------------
# 4) 3개 언론사(015/009/021) 합산 실행부
# --------------------------------------------------
def main():
    # ★ 언론사별 설정
    #   - tag, class_name은 015에서 이미 잘 되는 값 기준으로 두고
    #   - 009, 021도 같은 템플릿일 가능성이 높지만
    #     만약 0개 나오면 F12로 구조 확인해서 수정해주면 됨.
    PRESS_CONFIGS = [
        {
            "press_id": "015",
            "name": "한국경제",
            "url": "https://media.naver.com/press/015?sid=101",
            "tag": "span",
            "class_name": "press_edit_news_title",
        },
        {
            "press_id": "009",
            "name": "매일경제",
            "url": "https://media.naver.com/press/009?sid=101",
            "tag": "span",
            "class_name": "press_edit_news_title",
        },
        {
            "press_id": "011",
            "name": "서울경제",
            "url": "https://media.naver.com/press/011?sid=101",
            "tag": "span",
            "class_name": "press_edit_news_title",
        },
    ]

    all_headlines = []

    # 각 언론사에서 제목 수집
    for cfg in PRESS_CONFIGS:
        print(f"\n[정보] {cfg['name']} ({cfg['press_id']}) 기사 제목 수집 중...")
        headlines = get_all_headlines(cfg["url"], cfg["tag"], cfg["class_name"])
        print(f" - 수집된 제목 개수: {len(headlines)}")

        # 예시 몇 개만 보여주기
        if headlines:
            print(" - 예시 제목 3개:", headlines[:3])

        all_headlines.extend(headlines)

    print("\n[정보] 3개 언론사 전체 기사 제목 수:", len(all_headlines))

    if not all_headlines:
        print("[알림] 수집된 제목이 없습니다. tag/class_name 설정을 다시 확인해주세요.")
        return

    # 2단어 이상 명사구 기준 상위 키워드 구 추출
    top_n = 10
    top_phrases = get_top_phrases(all_headlines, top_n=top_n)

    if not top_phrases:
        print("[알림] 추출된 2단어 이상 명사구가 없습니다.")
        return

    print(f"\n📌 오늘의 주요 2단어 이상 키워드 구 (3개 언론사 합산, TOP {top_n}):")
    for phrase, count in top_phrases:
        print(f"- {phrase} ({count}회)")


if __name__ == "__main__":
    main()
