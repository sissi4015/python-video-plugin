


# TYPES_AND_CLASSIFYS 映射
TYPES_AND_CLASSIFYS = {
    "空调": ["拆卸外壳", "拆卸风轮", "拆卸滤网", "清洗外壳前", "清洗风轮前", "清洗滤网前", "清洗外壳中", "清洗风轮中", "清洗滤网中", "清洗外壳后", "清洗风轮后", "清洗滤网后", "专业设备", "其他"],
    "开荒": ["厨房", "客厅", "拖地", "扫地", "擦桌子", "擦玻璃", "其他"],
    "洗衣洗鞋": ["羽绒服", "大衣", "洗衣", "洗鞋", "其他"]
}

# 输入参数
class InputParameters:
    def __init__(self, script: str, video_type: str, video_count: int, first_video_url: str, last_video_url: str):
        self.script = script
        self.video_type = video_type
        self.video_count = video_count
        self.first_video_url = first_video_url
        self.last_video_url = last_video_url


# 视频分镜
class Shot:
    def __init__(self, shot: str, scene: str, character: str, action: str, mood: str, classify: str, keywords: str, startTime: float, endTime: float, duration: float):
        self.shot = shot
        self.scene = scene
        self.character = character
        self.action = action
        self.mood = mood
        self.classify = classify
        self.keywords = keywords
        self.startTime = startTime
        self.endTime = endTime
        self.duration = duration
    def __repr__(self):
        return f"Shot(shot={self.shot!r}, scene={self.scene!r}, character={self.character!r}, action={self.action!r}, mood={self.mood!r}, classify={self.classify!r}, keywords={self.keywords!r}, startTime={self.startTime}, endTime={self.endTime}, duration={self.duration})"

# 时间线
class TimeLine:
        def __init__(self, word, startTime, endTime, confidence):
            self.word = word
            self.startTime = startTime
            self.endTime = endTime
            self.confidence = confidence

        def __repr__(self):
            return f"TimeLine(word={self.word!r}, start={self.startTime}, end={self.endTime}, confidence={self.confidence})"


# 视频草稿
class Draft:
    def __init__(self, draft_url, first_video_url, video_dir, last_video_url, audio_file_url, caption_file_url):
        self.draft_url = draft_url
        self.first_video_url = first_video_url
        self.video_dir = video_dir
        self.last_video_url = last_video_url
        self.audio_file_url = audio_file_url
        self.caption_file_url = caption_file_url