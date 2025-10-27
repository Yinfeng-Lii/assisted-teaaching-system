import base64
import hashlib
import hmac
import json
import ssl
import threading
import websocket
from datetime import datetime
from time import mktime
from urllib.parse import urlparse, urlencode
from wsgiref.handlers import format_date_time

class HuoXingModel:
    def __init__(self, app_id, api_secret, api_key, url, domain):
        self.app_id = app_id
        self.api_secret = api_secret
        self.api_key = api_key
        self.url = url
        self.domain = domain
        self.history = []
        self.answer = ""

    def get_auth_url(self):
        host = urlparse(self.url).netloc
        path = urlparse(self.url).path
        cur_time = datetime.now()
        date = format_date_time(mktime(cur_time.timetuple()))

        tmp = f"host: {host}\n"
        tmp += f"date: {date}\n"
        tmp += f"GET {path} HTTP/1.1"

        tmp_sha = hmac.new(self.api_secret.encode('utf-8'), tmp.encode('utf-8'), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(tmp_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        v = {"authorization": authorization, "date": date, "host": host}
        return self.url + '?' + urlencode(v)

    def get_text(self, role, content):
        return {"role": role, "content": content}

    def check_question_len(self, text):
        # A simple history management to keep context within token limits
        while len(json.dumps(self.history)) + len(json.dumps(text)) > 8000:
            self.history.pop(0)
        self.history.append(text)
        return self.history

    def start(self):
        auth_url = self.get_auth_url()
        ws_client = WsClient(url=auth_url, question=self.history, app_id=self.app_id, domain=self.domain)
        ws_client.start()
        self.answer = ws_client.answer
        self.history.append(self.get_text("assistant", self.answer))

class WsClient:
    def __init__(self, url, question, app_id, domain):
        self.url = url
        self.app_id = app_id
        self.domain = domain
        self.question = question
        self.ws = None
        self.answer = ""
        self.send_msg = self.gen_params()

    def gen_params(self):
        data = {
            "header": {"app_id": self.app_id, "uid": "1234"},
            "parameter": {"chat": {
                "domain": self.domain, "temperature": 0.5, "max_tokens": 2048
            }},
            "payload": {"message": {"text": self.question}}
        }
        return data

    def on_open(self, ws):
        print("WebSocket onOpen")
        threading.Thread(target=self.run, args=()).start()

    def run(self):
        data = json.dumps(self.send_msg)
        self.ws.send(data)

    def on_message(self, ws, message):
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            self.ws.close()
            return
        
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        self.answer += content

        if status == 2:
            print(f"星火: {self.answer}")
            self.ws.close()

    def on_error(self, ws, error):
        print("WebSocket onError:", error)

    def on_close(self, ws, one, two):
        print("WebSocket onClose")

    def start(self):
        self.ws = websocket.WebSocketApp(
            url=self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})