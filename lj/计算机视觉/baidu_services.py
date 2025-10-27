import os
from os import path
from aip import AipSpeech
import speech_recognition as sr
from speech_recognition import WaitTimeoutError
from playsound import playsound

class BaiduASR:
    def __init__(self, app_id, api_key, secret_key):
        self.APP_ID = app_id
        self.API_KEY = api_key
        self.SECRET_KEY = secret_key
        self.client = AipSpeech(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        self.r = sr.Recognizer()
        self.path = path.dirname(__file__)
        self._del_asr_file() # 清除上一次保留的音频文件

    def _get_file_content(self, file_path):
        with open(file_path, "rb") as f:
            return f.read()

    def _del_asr_file(self):
        asr_file = os.path.join(self.path, "audio", "speech.wav")
        if os.path.exists(asr_file):
            print("Deleting old asr file...")
            os.remove(asr_file)

    def speech_to_text(self):
        with sr.Microphone(sample_rate=16000) as source:
            self.r.adjust_for_ambient_noise(source, duration=1)
            print("可以开始说话了...")
            audio = self.r.listen(source, timeout=20, phrase_time_limit=5)
        
        # Use Baidu's online ASR
        result = self.client.asr(audio.get_wav_data(), 'wav', 16000, {'dev_pid': 1537})
        
        if result["err_msg"] != "success.":
            error_msg = f"语音识别错误: {result['err_msg']}"
            print(error_msg)
            return "" # Return empty string on error
        else:
            return result["result"][0]

class BaiDuTTS:
    def __init__(self, app_id, api_key, secret_key):
        self.client = AipSpeech(app_id, api_key, secret_key)
        self.path = path.dirname(__file__)
        self._del_tts_file()

    def _del_tts_file(self):
        tts_file = os.path.join(self.path, "audio", "audio_tts.wav")
        if os.path.exists(tts_file):
            print("Deleting old tts file...")
            os.remove(tts_file)

    def text_to_speech_baidu_and_play(self, text):
        result = self.client.synthesis(text, 'zh', 1, {'vol': 5})
        
        tts_file_path = os.path.join(self.path, "audio", "audio_tts.wav")
        if not isinstance(result, dict):
            print("TTS 合成成功")
            with open(tts_file_path, 'wb') as f:
                f.write(result)
            playsound(tts_file_path)
        else:
            print('TTS 合成失败:', result)