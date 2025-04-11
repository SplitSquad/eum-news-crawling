from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import time
from bs4 import BeautifulSoup
import json
import os
import sys
import urllib.request

load_dotenv()

def crawl_real_time_trend_keyword():
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 헤드리스 모드 비활성화
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 웹드라이버 초기화
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 페이지 로드
        print("웹페이지 로딩 중...")
        driver.get("https://kdx.kr/service/searchtrend/view")
        
        # 페이지가 완전히 로드될 때까지 대기
        wait = WebDriverWait(driver, 2)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # iframe의 페이지 소스 가져오기
        iframe = driver.find_element(By.XPATH, '//*[@id="registerStep2"]/div/iframe')
        driver.switch_to.frame(iframe)
        print("iframe으로 전환 완료")
        time.sleep(1)
        iframe_source = driver.page_source
        print(f"iframe 내부 페이지 소스 길이: {len(iframe_source)}")
        
        # BeautifulSoup으로 파싱 및 소스 찾기
        soup = BeautifulSoup(iframe_source, 'html.parser')
        highlight_elements = soup.find_all(class_='ibox-tr-highlight')
        
        if highlight_elements:
            print(f"\n=== ibox-tr-highlight 클래스를 가진 요소 ({len(highlight_elements)}개) ===")
            
            # 결과를 저장할 리스트
            results = []
            count = 1
            for element in highlight_elements:
                if count > 10:
                    break
                count += 1
                # 각 필드 추출 및 객체 생성
                rank = element.find(class_='ibox-td-rank').get_text(strip=True) if element.find(class_='ibox-td-rank') else ''
                keyword = element.find(class_='on-highlight-bold on-highlight-darkblue ibox-td-text').get_text(strip=True) if element.find(class_='on-highlight-bold on-highlight-darkblue ibox-td-text') else ''
                search_volume = element.find(class_='icon-double-up').get_text(strip=True) if element.find(class_='icon-double-up') else ''
                result = {
                    'rank': rank,
                    'keyword': keyword,
                    'search_volume': search_volume,
                }
                
                results.append(result)
                print(f"- 순위: {rank}, 키워드: {keyword}, 검색량: {search_volume}")
            
            # rank를 기준으로 내림차순 정렬
            results.sort(key=lambda x: int(x['search_volume']) if x['search_volume'].isdigit() else float('inf'), reverse=True)
            
            # 결과를 JSON 파일로 저장
            with open('highlight_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print("\n결과가 highlight_results.json 파일에 저장되었습니다.")
        else:
            print("ibox-tr-highlight 클래스를 가진 요소를 찾을 수 없습니다.")
            
        # 메인 프레임으로 다시 전환
        driver.switch_to.default_content()
            
    except Exception as e:
        print(f"에러 발생: {str(e)}")
    finally:
        # 브라우저 종료
        driver.quit()
    return results
        
def crawl_articles_by_keyword(articles):
    # 크롤링 한 키워드 기반 뉴스 검색
    # 네이버 뉴스 api 호출
    client_id = os.environ.get('NAVER_CLIENT_ID')
    client_secret = os.environ.get('NAVER_CLIENT_SECRET')
    responses = {}
    
    # 각 키워드별 뉴스 검색 결과 저장
    for result in articles:
        encText = urllib.parse.quote(f"{result['keyword']}")
        url = "https://openapi.naver.com/v1/search/news.json?query=" + encText + "&display=30" # JSON 결과
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id",client_id)
        request.add_header("X-Naver-Client-Secret",client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if(rescode==200):
            response_body = response.read()
            print(response_body.decode('utf-8'))
            responses[f"{result['keyword']}"] = json.loads(response_body.decode('utf-8'))
        else:
            print("Error Code:" + rescode)
        # 결과 JSON 파일로 저장
        with open('highlight_results_responses.json', 'w', encoding='utf-8') as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)
        print("\n결과가 highlight_results_responses.json 파일에 저장되었습니다.")
    return responses

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
        print(f"뉴스 기사 로딩 중... ({url})")
        driver.get(url)
        wait = WebDriverWait(driver, 3)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_source = driver.page_source
        print(f"페이지 소스 길이: {len(page_source)}")
        
        # BeautifulSoup으로 파싱, 클래스 찾기
        soup = BeautifulSoup(page_source, 'html.parser')
        article = soup.find(class_='newsct_article')
        
        if article:
            print("\n=== 뉴스 기사 내용 ===")
            
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
        print(f"에러 발생: {str(e)}")
    finally:
        # 브라우저 종료
        driver.quit()

def crawl_each_article_at_articles(article_list):
    # 네이버뉴스 api에서 받아온 뉴스 리스트에서 각 뉴스 크롤링
    # article_list 에서 뉴스 링크추출
    results = {}
    for keyword, articles in article_list.items():
        print(f"[{keyword}]")
        for article in articles['items']:
            url = article['link']
            if 'naver' in url:
                # 특정 뉴스기사 크롤링
                result = crawling_naver_news(url)

                # 키워드별 뉴스 기사 저장
                if keyword not in results:
                    results[keyword] = []
                results[keyword].append(result)
        with open('naver_news_article.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("\n결과가 naver_news_article.json 파일에 저장되었습니다.")

def crawling_news():
    articles = crawl_real_time_trend_keyword()
    article_list = crawl_articles_by_keyword(articles)
    crawl_each_article_at_articles(article_list)

if __name__ == "__main__":
    crawling_news() 
