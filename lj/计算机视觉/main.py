from 计算机视觉.config_reader import ReadCfg
from baidu_services import BaiduASR, BaiDuTTS, WaitTimeoutError
from 计算机视觉.huoxing_model import HuoXingModel
import os

# 设置交互方式, 2: 键盘文本输入, 1: 语音交互 (默认)
SWITCH_INPUT = 1

def main():
    # Create audio directory if it doesn't exist
    if not os.path.exists("audio"):
        os.makedirs("audio")

    # --- Initialization ---
    cfg_file = "config.json"
    cfg = ReadCfg(cfg_file)
    cfg.get_cfg_info()

    asr = BaiduASR(cfg.bd_app_id, cfg.bd_app_key, cfg.bd_secret_key)
    tts = BaiDuTTS(cfg.bd_app_id, cfg.bd_app_key, cfg.bd_secret_key)
    spark_client = HuoXingModel(
        cfg.hx_app_id, cfg.hx_api_secret, cfg.hx_api_key,
        cfg.hx_ws_url, cfg.hx_domain
    )

    print("\n智能对话准备开启, 如需停止, 请说出或输入'关闭对话'即可")

    # --- Main Loop ---
    while True:
        input_text = ""
        try:
            # --- Get User Input ---
            if SWITCH_INPUT == 1: # Voice input
                input_text = asr.speech_to_text()
                if input_text:
                    print(f"我: {input_text}")
            else: # Text input
                input_text = input("我: ")

            # --- Process Input ---
            if not input_text or len(input_text.strip()) == 0:
                if SWITCH_INPUT == 2: print("输入为空, 请重新输入")
                continue

            if "关闭对话" in input_text:
                response = "已为您关闭对话"
                print(f"助手: {response}")
                if SWITCH_INPUT == 1: tts.text_to_speech_baidu_and_play(response)
                break
            
            # --- Interact with Spark Model ---
            user_question = spark_client.get_text("user", input_text)
            spark_client.check_question_len(user_question)
            spark_client.start()
            
            # --- Output Response ---
            if SWITCH_INPUT == 1 and spark_client.answer:
                tts.text_to_speech_baidu_and_play(spark_client.answer)

        except WaitTimeoutError:
            response = "1分钟超时, 应用已退出"
            print(response)
            if SWITCH_INPUT == 1: tts.text_to_speech_baidu_and_play(response)
            break
        except Exception as e:
            response = f"应用异常退出: {e}"
            print(response)
            if SWITCH_INPUT == 1: tts.text_to_speech_baidu_and_play(response)
            break

if __name__ == "__main__":
    main()