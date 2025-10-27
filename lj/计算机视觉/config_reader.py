import json
from os import path

class ReadCfg:
    def __init__(self, cfg_path):
        self.cfg_path = cfg_path
        self.hx_app_id = ""
        self.hx_api_secret = ""
        self.hx_api_key = ""
        self.hx_ws_url = ""
        self.hx_domain = ""
        self.bd_app_id = ""
        self.bd_app_key = ""
        self.bd_secret_key = ""

    def get_cfg_info(self):
        with open(self.cfg_path, encoding='utf-8') as f:
            cfg = json.load(f)
            self.hx_app_id = cfg['hx_model']["app_id"]
            self.hx_api_secret = cfg['hx_model']["api_secret"]
            self.hx_api_key = cfg['hx_model']["api_key"]
            self.hx_ws_url = cfg['hx_model']["ws_url"]
            self.hx_domain = cfg['hx_model']["domain"]
            self.bd_app_id = cfg['baidu_asr']["app_id"]
            self.bd_app_key = cfg['baidu_asr']["app_key"]
            self.bd_secret_key = cfg['baidu_asr']["secret_key"]