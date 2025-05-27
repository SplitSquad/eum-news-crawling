from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
import json
import os
import urllib.request
import re
import datetime
from debate_content_request import request_create_debate
from create_debate import post_debate
load_dotenv()

# 실시간 인기 검색어 크롤링
def crawl_real_time_trend_keyword():
    today = datetime.datetime.now()
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 헤드리스 모드 비활성화
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 웹드라이버 초기화
    driver = webdriver.Chrome(options=chrome_options)
    
    # 페이지 로드
    driver.get("https://kdx.kr/main")
    
    # 페이지가 완전히 로드될 때까지 대기
    wait = WebDriverWait(driver, 2)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    page_source = driver.page_source

    
    # BeautifulSoup으로 파싱 및 소스 찾기
    soup = BeautifulSoup(page_source, 'html.parser')
    popular_items = soup.find_all(class_='product-item')
    results = []

    for popular_item in popular_items:
        title_div = popular_item.select_one('.title')
        if not title_div:
            continue

        # 랭킹 추출 (font 태그)
        font_tag = title_div.find('font')
        rank_raw = font_tag.get_text(strip=True) if font_tag else None
        rank = re.search(r'\d+', rank_raw).group() if rank_raw and re.search(r'\d+', rank_raw) else None
    
        # 이름 추출: font와 span 제거 후 나머지 텍스트
        for tag in title_div.find_all(['font', 'span']):
            tag.extract()
        name = title_div.get_text(strip=True)

        results.append({
            'rank': rank,
            'keyword': name
        })

    with open(f'keyword_list/keyword_list_{today}.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logging.info(f"\n결과가 keyword_list_{today}.json 파일에 저장되었습니다.")

    # 출력 확인
    return results

# # 네이버뉴스 api 호출, 각 키워드별 뉴스 크롤링 및 저장
# # entertain 이랑 분리 필요
def crawl_articles_by_keyword(keywords):
    # 크롤링 한 키워드 기반 뉴스 검색

    client_id = os.environ.get('NAVER_CLIENT_ID')
    client_secret = os.environ.get('NAVER_CLIENT_SECRET')
    responses = {}
    today = datetime.datetime.now()
    # 각 키워드별 뉴스 검색 결과 저장
    for result in keywords:
        encText = urllib.parse.quote(f"{result['keyword']}")
        url = "https://openapi.naver.com/v1/search/news.json?query=" + encText + "&display=30" # JSON 결과
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id",client_id)
        request.add_header("X-Naver-Client-Secret",client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if(rescode==200):
            response_body = response.read()
            responses[f"{result['keyword']}"] = json.loads(response_body.decode('utf-8'))
        else:
            logging.error("Error Code: " + rescode)
        # 결과 JSON 파일로 저장
    with open(f'newslist/newslist_by_keyword_{today}.json', 'w', encoding='utf-8') as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)
    logging.info(f"\n결과가 newslist_by_keyword_{today}.json 파일에 저장되었습니다.")
    return responses


# 일반 네이버뉴스 크롤링
def crawling_naver_news(url):
    # Chrome 옵션 설정
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 헤드리스 모드 비활성화
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # 웹드라이버 초기화
    driver = webdriver.Chrome(options=chrome_options)
    try:
        # 페이지 로드, 및 소스 가져오기
        driver.get(url)
        wait = WebDriverWait(driver, 3)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_source = driver.page_source
        
        # BeautifulSoup으로 파싱, 클래스 찾기
        soup = BeautifulSoup(page_source, 'html.parser')
        article = soup.find(class_='newsct_article')
        
        if article:
            # 기사 제목, 작성일, 내용 추출 및 결과 객체 생성
            title = soup.find('h2', class_='media_end_head_headline').get_text(strip=True) if soup.find('h2', class_='media_end_head_headline') else ''
            date = soup.find('span', class_='media_end_head_info_datestamp_time').get_text(strip=True) if soup.find('span', class_='media_end_head_info_datestamp_time') else ''
            content = article.get_text(strip=True)
            result = {
                'title': title,
                'date': date,
                'content': content
            }
            return result
    except Exception as e:
        logging.info(f"에러 발생: {str(e)}")
    finally:
        # 브라우저 종료
        driver.quit()

# 스포츠뉴스 크롤링
def crawling_naver_sports_news(url):
    # Chrome 옵션 설정
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 헤드리스 모드 비활성화
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # 웹드라이버 초기화
    driver = webdriver.Chrome(options=chrome_options)
    try:
        # 페이지 로드, 및 소스 가져오기
        driver.get(url)
        wait = WebDriverWait(driver, 3)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_source = driver.page_source
        
        # BeautifulSoup으로 파싱, 클래스 찾기
        soup = BeautifulSoup(page_source, 'html.parser')
        article = soup.find(class_='_article_content')
        
        if article:
            # 기사 제목, 작성일, 내용 추출 및 결과 객체 생성
            title = soup.find('h2', class_='NewsEndMain_article_title__kqEzS').get_text(strip=True) if soup.find('h2', class_='NewsEndMain_article_title__kqEzS') else ''
            date = soup.find('em', class_='NewsEndMain_date__xjtsQ').get_text(strip=True) if soup.find('em', class_='NewsEndMain_date__xjtsQ') else ''
            content = article.get_text(strip=True)
            result = {
                'title': title,
                'date': date,
                'content': content
            }
            return result
    except Exception as e:
        logging.error(f"에러 발생: {str(e)}")
    finally:
        # 브라우저 종료
        driver.quit()

# 엔터뉴스 크롤링
def crawling_naver_entertain_news(url):
    # Chrome 옵션 설정
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 헤드리스 모드 비활성화
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # 웹드라이버 초기화
    driver = webdriver.Chrome(options=chrome_options)
    try:
        # 페이지 로드, 및 소스 가져오기
        driver.get(url)
        wait = WebDriverWait(driver, 3)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_source = driver.page_source
        
        # BeautifulSoup으로 파싱, 클래스 찾기
        soup = BeautifulSoup(page_source, 'html.parser')
        article = soup.find(class_='_article_content')
        
        if article:      
            # 기사 제목, 작성일, 내용 추출 및 결과 객체 생성
            title = soup.find('h2', class_='NewsEndMain_article_title__kqEzS').get_text(strip=True) if soup.find('h2', class_='NewsEndMain_article_title__kqEzS') else ''
            date = soup.find('em', class_='date').get_text(strip=True) if soup.find('em', class_='date') else ''
            content = article.get_text(strip=True)
            result = {
                'title': title,
                'date': date,
                'content': content
            }
            return result
    except Exception as e:
        logging.info(f"에러 발생: {str(e)}")
    finally:
        # 브라우저 종료
        driver.quit()

# 네이버뉴스 api에서 받아온 뉴스 리스트에서 각 뉴스 크롤링
def crawl_each_article_at_articles(article_list):
    # article_list 에서 뉴스 링크추출
    today = datetime.datetime.now()
    results = {}
    for keyword, articles in article_list.items():
        temp_result = {}
        for article in articles['items']:
            result = {}
            url = article['link']
            netloc = urlparse(url).netloc
            # 특정 뉴스기사 크롤링
            if 'news.naver' in netloc:
                result = crawling_naver_news(url)
            elif 'sports.naver' in netloc:
                result = crawling_naver_sports_news(url)
            elif 'entertain.naver' in netloc:
                result = crawling_naver_entertain_news(url)

            # 키워드별 뉴스 기사 저장
            if keyword not in results:
                results[keyword] = []
                temp_result[keyword] = []
            if result:
                temp_result[keyword].append(result)
#############################################################################################
        ##### 토론주제 생성
        # response = request_create_debate(temp_result[keyword])
        
        ###### 테스팅 하고 위에걸로 변경
        temp_temp_result = {}
        temp_temp_result[keyword] = []
        temp_temp_result[keyword].append(temp_result[keyword][0])
        print("\n\n토론글 생성 입력데이터: ")
        print(temp_temp_result[keyword])
        response = request_create_debate(temp_temp_result[keyword])
        
        print("\n토론글 생성 출력데이터: ")
        print(response)

#############################################################################################
        ##### 토론글 생성
        post_debate_request = {
            "title": f"{response['discussion']['title']}",
            "content": f"{response['discussion']['content']} \n\n토론주제: {response['discussion']['vote']}\n찬성측의견: {response['discussion']['positive']}\n반대측의견: {response['discussion']['negative']}",
            "category": f"{response['discussion']['category']}"
        }
        logging.info(f"토론글생성 api data: {post_debate_request}")

        post_debate(post_debate_request)
        logging.info("post_dabate api call success!")
        if temp_result is not None:
            results[keyword].append(temp_result[keyword])

    with open(f'crawled_news/naver_news_article_{today}.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logging.info(f"\n결과가 naver_news_article_{today}.json 파일에 저장되었습니다.")

# 뉴스 크롤링 및 토론글생성
def crawling_news():
    logging.basicConfig(filename='crawl_news.log', level=logging.INFO)
    keywords = crawl_real_time_trend_keyword()
    article_list = crawl_articles_by_keyword(keywords)
    crawl_each_article_at_articles(article_list)

if __name__ == "__main__":
    crawling_news()
