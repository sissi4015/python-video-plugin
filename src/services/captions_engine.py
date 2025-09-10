from math import e
import re
import json
import logging


def format_timestamp(seconds):
        ms = int((seconds - int(seconds)) * 1000)
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

def caption_generate(shots, timelines, script_dir):
    """
    shots: 分镜文本数组，每个元素为字符串
    timelines: 字音时间线数组，格式为 {'word': str, 'start': float, 'end': float}
    caption_url: 输出的 .srt 字幕文件路径
    """

    # 将每个分镜文本的所有字的时间合并为整体时间区间
    idx = 1
    char_idx = 0
    completed_shots = []
    
    # 每个分镜的起始时间
    starttime = 0.0
    for shot in shots:
        # 分镜文本
        shotstr = shot['shot']
        # 统计分镜文本中的汉字数（不计标点符号）
        shot_len = len(re.findall(r'[\u4e00-\u9fff]', shotstr))
        # 获取该分镜对应的所有字的时间区间
        endtime = timelines[char_idx + shot_len - 1]['endTime']
        # 获取该分镜的时长
        duration = endtime - starttime
        shot_info = {
            "shot": shotstr,
            "scene": shot['scene'],
            "character": shot['character'],
            "action": shot['action'],
            "mood": shot['mood'],
            "classify": shot['classify'],
            "starttime": starttime,
            "endtime": endtime,
            "duration": duration
        }
        completed_shots.append(shot_info)

        # srt_content += f"{idx}\n"
        # srt_content += f"{format_timestamp(starttime)} --> {format_timestamp(endtime)}\n"
        # srt_content += f"{shotstr}\n\n"

        idx += 1
        char_idx += shot_len
        starttime = endtime


    # SRT文件内容
    srt_content = ""
    # 每一句srt文案
    srt_word = ""
    # SRT字幕数组--设置每条字幕
    srt_array = []
    is_new_srt = True
    srt_start = 0.0
    for item in timelines:

        timeline_word = item['word']
        srt_word += timeline_word

        if is_new_srt:
            srt_start = item['startTime']
            is_new_srt = False
            srt_content += f"{len(srt_array) + 1}\n"
            srt_content += f"{format_timestamp(srt_start)} --> "
        

        is_last_word = re.search(r'[，。！？；：,.!?;:、]', timeline_word) or (item == timelines[-1])
        if is_last_word:
            srt_end = item['endTime']
            srt_array.append({
                "index": len(srt_array) + 1,
                "start": srt_start,
                "end": srt_end,
                "text": timeline_word
            })
            srt_content += f"{format_timestamp(srt_end)}\n"
            srt_content += f"{re.sub(r'[，。！？；：,.!?;:、]', '', srt_word)}\n\n"

            is_new_srt = True
            srt_word = ""


    # 保存字幕文件
    with open(script_dir + "captions.srt", "w", encoding="utf-8") as f:
        f.write(srt_content)
    
    # 保存分镜结果到本地
    try:
        with open(script_dir + "shots.txt", "w", encoding="utf-8") as f:
            f.write(json.dumps(completed_shots, ensure_ascii=False, indent=4))
    except Exception as e:
        logger = logging.getLogger("video_plugin")
        logger.warning(f"保存文案或者分镜结果失败，但不影响后续操作: {e}")

    return completed_shots

# 测试调用数据
# shots = [
#     "第一幕：小明走进教室。",
#     "第二幕：老师开始上课。",
#     "第三幕：同学们认真听讲。"
# ]
# timelines = [
#     {'word':"第", 'start': 0.0, 'end': 5.2},
#     {'word':"一", 'start': 5.2, 'end': 12.8},
#     {'word':"幕", 'start': 12.8, 'end': 20.0},
#     {'word':"：", 'start': 20.0, 'end': 25.0},
#     {'word':"小", 'start': 25.0, 'end': 30.5},
#     {'word':"明", 'start': 30.5, 'end': 35.0},
#     {'word':"走", 'start': 35.0, 'end': 40.0},
#     {'word':"进", 'start': 40.0, 'end': 45.0},
#     {'word':"教", 'start': 45.0, 'end': 50.0},
#     {'word':"室", 'start': 50.0, 'end': 55.0},
#     {'word':"。", 'start': 55.0, 'end': 60.0},
#     {'word':"第", 'start': 60.0, 'end': 65.0},
#     {'word':"二", 'start': 65.0, 'end': 70.0},
#     {'word':"幕", 'start': 70.0, 'end': 75.0},
#     {'word':"：", 'start': 75.0, 'end': 80.0},
#     {'word':"老", 'start': 80.0, 'end': 85.0},
#     {'word':"师", 'start': 85.0, 'end': 90.0},
#     {'word':"开", 'start': 90.0, 'end': 95.0},
#     {'word':"始", 'start': 95.0, 'end': 100.0},
#     {'word':"上", 'start': 100.0, 'end': 105.0},
#     {'word':"课", 'start': 105.0, 'end': 110.0},
#     {'word':"。", 'start': 110.0, 'end': 115.0},
#     {'word':"第", 'start': 115.0, 'end': 120.0},
#     {'word':"三", 'start': 120.0, 'end': 125.0},
#     {'word':"幕", 'start': 125.0, 'end': 130.0},
#     {'word':"：", 'start': 130.0, 'end': 135.0},
#     {'word':"同", 'start': 135.0, 'end': 140.0},
#     {'word':"学", 'start': 140.0, 'end': 145.0},
#     {'word':"们", 'start': 145.0, 'end': 150.0},
#     {'word':"认", 'start': 150.0, 'end': 155.0},
#     {'word':"真", 'start': 155.0, 'end': 160.0},
#     {'word':"听", 'start': 160.0, 'end': 165.0},
#     {'word':"讲", 'start': 165.0, 'end': 170.0},
#     {'word':"。", 'start': 170.0, 'end': 175.0}
# ]
# caption_url = "test_output.srt"
# caption_generate(shots, timelines, caption_url)
# print(f"SRT字幕已生成: {caption_url}")