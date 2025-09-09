import os
import time
from pickle import FALSE
import asyncio
import datetime
import logging

from services.script_engine import parse_script
from services.audio_engine import audio_generate
from services.captions_engine import caption_generate
from services.video_engine import video_generate, search_videos



def main(script, video_type, n, first_video_url, last_video_url):

    # import sys
    # if len(sys.argv) != 4:
    #     print("Usage: python main.py <script> <videoType> <n> <firstVideoUrl>")
    #     return

    # # 文案
    # script = sys.argv[1]
    # # 视频类型(空调、洗衣、洗鞋、开荒、保姆、月嫂...)
    # video_type = sys.argv[2]
    # # 视频数量(取整数，最小1，最大200)
    # n = int(sys.argv[3])
    # # 开头视频URL
    # first_video_url = sys.argv[4]
    

    # 基础目录
    base_dir = os.getcwd() + "\\temp\\" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")
    script_dir = base_dir + "\\script\\"
    audio_dir = base_dir + "\\audios\\"
    video_dir = base_dir + "\\videos\\"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(script_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)

    # 创建 logger
    logger = logging.getLogger("video_plugin")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(base_dir + "\\main.log", encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    logger.info("初始化success")

    # ------------------Step 1:分镜------------------ 
    try:
        shots = parse_script(video_type, script, script_dir)
    except Exception as e:
        logger.error(f"分镜提取失败，程序结束: {e}")
        return
    logger.info("分镜success")

    # ------------------Step 2:音频------------------ 
    # 音频是否生成成功
    audio_flag = FALSE
    # 音频文件时间线
    timelines = []
    # 音频文件地址(口播)
    audio_file_url = audio_dir + "oral.wav"
    # 调用火山方舟语音合成大模型生成音频文件
    try:
        asyncio.run(audio_generate(script, audio_file_url, audio_flag, timelines))
    except Exception as e:
        logger.error(f"音频生成失败，程序结束: {e}")
        return
    # 等待音频生成完成（必须要口播音频完全生成后，才能确定timeline，才能继续后续的字幕和视频剪辑）
    wait_seconds = 0
    max_wait_seconds = 600
    while not audio_flag:
        wait_seconds += 1
        if wait_seconds > max_wait_seconds:
            logger.error("音频生成超过10分钟,程序结束")
            return
        time.sleep(1)
    logger.info("口播音频success")

    # ------------------Step 3:字幕------------------
    caption_file_url = script_dir + "captions.srt"
    try:
        shots = caption_generate(shots, timelines, script_dir)
    except Exception as e:
        logger.error(f"字幕生成失败，程序结束: {e}")
        return 
    logger.info("字幕success")


    # ------------------Step 4:剪辑------------------ 
    for i in range(1, n + 1):
        try:  
            # 生成草稿
            video_generate(video_type, shots, i, first_video_url, video_dir, last_video_url, audio_file_url, caption_file_url)
            logger.info(f"第{i}条视频:生成草稿success")
        except Exception as e:
            logger.error(f"第{i}条视频生成失败: {e}")
            continue
    logger.info("全部视频生成success")



# 测试调用
# python src/main.py "一冬天都没开过的空调，你都想象不到有多脏。今天58到家9块9洗空调" "空调" "1" ""
if __name__ == "__main__":
    main("心爱的衣服鞋子怕自己洗坏洗不干净？那我建议你试试五八到家这个几千平的中央洗护工厂，十六道洗护消杀工序，全手工处理深层污渍。现在抖音有团购，六十九就可以任洗三件，不管是羽绒服、运动鞋还是羊毛衫，都能给你洗的干干净净。而且提供全国上门快递取送，连门都不用出。有需要的抓紧左下角预约吧", "空调", 1, "", "")