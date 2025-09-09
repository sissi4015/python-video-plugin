

# 使用whisper获取本地音频文件的时间线（已弃用）

from deprecated import deprecated

import os
import whisper
from types.index import TimeLine

@deprecated(reason="该方法已弃用，改为在audio_engine.py中获取时间线")
def get_audio_timelines(audio_url: str) -> list:
    if not os.path.exists(audio_url):
        raise FileNotFoundError(f"音频文件不存在: {audio_url}")

    model = whisper.load_model("base")
    result = model.transcribe(audio_url, word_timestamps=True)

    timelines = []
    for segment in result["segments"]:
        for word in segment["words"]:
            timelines.append(TimeLine(
                word=word['word'],
                start=word['start'],
                end=word['end']
            ))
    return timelines