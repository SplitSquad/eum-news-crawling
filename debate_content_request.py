# 토론주제 생성
# POST
# /api/v1/discussion
# Request
# [
#   {
#       title: "",
#       date: "",
#       content: ""
#   }
# ]
# 
# Response
# "discussion": {
#   title: "",
#   category: "",
#   content: ""
# }

import urllib.request
import logging
import json
import os

# AI 서비스에서 토론글생성 api를 호출한다
def request_create_debate(data):
    url = os.environ.get('EUM_DISCUSSION_ROOM_URI')
    data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url,
                                 data=data,
                                 headers={
                                     'Content-Type': 'application/json'
                                     }, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = response.read()
            content = json.loads(result)
        return content
    except urllib.error.HTTPError as e:
        error_message = e.read().decode()

        logging.error("service name: AI-Discussion-Service\ncalled api: /api/v1/discussion")
        logging.error(f"error code: {e.code}\nerror reason: {e.reason}")
        logging.error(f"에러 내용: {error_message}")