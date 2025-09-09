from typing import List


# 视频类型
class VideoType:
    VIDEO_TYPE_1 = "空调"
    VIDEO_TYPE_2 = "洗衣洗鞋"
    VIDEO_TYPE_3 = "开荒保洁"

# 分镜关键词
class VideoClassfy:
    VIDEO_CLASSFY_1 = "拆卸"
    VIDEO_CLASSFY_2 = "风轮"
    VIDEO_CLASSFY_3 = "主播"
    # TODOOOO 需要补全

# 视频素材路径
class VideoMaterialPaths:
    MATERIAL_DIRECTORY = r"F:\dockerSyncFiles\material"


# 输入参数
class InputParameters:
    def __init__(self, text: str, video_type: str, video_count: int, first_video_url: str):
        self.text = text
        self.video_type = video_type
        self.video_count = video_count
        self.first_video_url = first_video_url



# 视频分镜
class Shot:
    def __init__(self, shot: str, scene: str, character: str, action: str, mood: str, classify: str, starttime: float, endtime: float, duration: float):
        self.shot = shot
        self.scene = scene
        self.character = character
        self.action = action
        self.mood = mood
        self.classify = classify
        self.starttime = starttime
        self.endtime = endtime
        self.duration = duration


# 视频口播
class Voiceover:
    def __init__(self, voiceover: str, starttime: float, endtime: float):
        self.voiceover = voiceover
        self.starttime = starttime
        self.endtime = endtime

# 时间线
class TimeLine:
        def __init__(self, word, start, end):
            self.word = word
            self.start = start
            self.end = end

        def __repr__(self):
            return f"TimeLine(word={self.word!r}, start={self.start}, end={self.end})"

# 视频字幕
class Subtitle:
    def __init__(self, shot: str, starttime: float, endtime: float):
        self.shot = shot
        self.starttime = starttime
        self.endtime = endtime

# 分镜视频
class ShotVideo:
    def __init__(self, shotvideo: object, starttime: float, endtime: float):
        self.shotvideo = shotvideo
        self.starttime = starttime
        self.endtime = endtime

# 视频草稿
class Draft:
    def __init__(self, voiceovers: List[Voiceover],  subtitles: List[Subtitle], videos: List[ShotVideo]):
        self.voiceovers = voiceovers
        self.subtitles = subtitles
        self.videos = videos