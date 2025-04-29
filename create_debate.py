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

def post_debate(data):
    url = str(os.environ.get('EUM_DEBATE_SERVICE_URI')) + "/debate"
    
    data = json.dumps(data).encode('utf-8')
    urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')





