import subprocess
import logging

logger = logging.getLogger("video_plugin")

def run_ffmpeg_command(cmd_list):
    """通用 ffmpeg 命令执行函数"""
    try:
        # 将所有路径中的反斜杠替换为斜杠，以获得最佳兼容性
        safe_cmd = [str(item).replace('\\', '/') for item in cmd_list]
        logger.debug(f"Executing FFmpeg command: {' '.join(safe_cmd)}")
        result = subprocess.run(safe_cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        logger.debug(f"FFmpeg stdout: {result.stdout}")
        if result.stderr:
            logger.info(f"FFmpeg stderr: {result.stderr}")
    except subprocess.CalledProcessError as e:
        error_message = (
            f"FFmpeg command failed with exit code {e.returncode}.\n"
            f"Command: {' '.join(e.cmd)}\n"
            f"Stdout: {e.stdout}\n"
            f"Stderr: {e.stderr}"
        )
        logger.error(error_message)
        raise

def get_video_duration(video_path):
    """使用 ffprobe 获取视频时长"""
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    result = subprocess.run(probe_cmd, check=True, capture_output=True, text=True)
    return float(result.stdout.strip())

def escape_ffmpeg_path(path):
    """为 ffmpeg 滤镜中的 Windows 路径进行转义"""
    if not path:
        return ""
    # 1. 将所有反斜杠替换为斜杠
    path = path.replace('\\', '/')
    # 2. 转义盘符后的冒号
    if ":" in path:
        parts = path.split(':', 1)
        path = f"{parts[0]}\\:{parts[1]}"
    return path