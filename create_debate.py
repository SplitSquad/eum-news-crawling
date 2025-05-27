# 토론글 생성
# POST
# /debate
# {
#   "title": "제목.",
#   "content": "내용.",
#   "category": "카테고리. {정치/시가, 경제, 생활/문화, 국제, 연예, IT/과학, 스포츠} 중 택 1"
# }

import urllib.request
import json
import os
import logging

# Debate-Service 의 토론생성 api 호출
def post_debate(data):
    url = os.environ.get('EUM_DEBATE_SERVICE_URI')
    logging.info(f"post_debate_api_url: {url}")
    DEBATE_SECRET = os.environ.get('DEBATE_SECRET')
    data = json.dumps(data).encode('utf-8')
    print("\n\nDebate-Service api 호출: " + url)
    req = urllib.request.Request(url,
                                 data=data,
                                 headers={
                                     'Content-Type': 'application/json',
                                     'Debate': DEBATE_SECRET
                                     }, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            result = response.read()
            # content = json.loads(result)
            # print(result.decode())
        # return content
    except urllib.error.HTTPError as e:
        error_message = e.read().decode()
        logging.error("service name: Backend-Debate-Service\ncalled api: /debate")
        logging.error(f"error code: {e.code}\nerror reason: {e.reason}")
        logging.error(f"에러 내용: {error_message}")




