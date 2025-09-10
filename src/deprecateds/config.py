# 路径配置
VIDEO_LOCAL_DATABASE = r"D:/material_database/"
OUTPUT_DIR = r"D:/video_house/"
FONT_PATH = "C:/Windows/Fonts/simhei.ttf" # 字体文件路径，例如黑体

# 视频参数
# 视频文件格式
VIDEO_EXTENSIONS = ('.mp4', '.MP4', '.mov', '.MOV', '.avi', '.AVI')
TARGET_RESOLUTION = "1080:1920"
TARGET_FPS = 30
VIDEO_BITRATE = "5M"

# 编码质量配置
CLIP_PRESET = "slow"
CLIP_CRF = "20"

MERGE_PRESET = "slow"
MERGE_CRF = "20"

SUBTITLE_PRESET = "slow"
SUBTITLE_CRF = "23"

# 字幕样式配置
SUBTITLE_STYLE = (
    "FontName=SimHei,FontSize=16,PrimaryColour=&HFFFFFF&,"
    "OutlineColour=&H000000&,BorderStyle=1,Outline=2,Shadow=0,"
    "Alignment=2,MarginV=30"
)