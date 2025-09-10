import os
import logging
import config
from utils import ffmpeg_utils

logger = logging.getLogger("video_plugin")

def video_merge_export(output_for_i_url, first_video_url, videos_for_i_url, last_video_url, audio_file_url, caption_file_url):
    # 收集所有视频片段
    video_segments = []
    if first_video_url:
        video_segments.append(first_video_url)
    # 中间分镜视频
    for file in sorted(os.listdir(videos_for_i_url)):
        if file.endswith(config.VIDEO_EXTENSIONS):
            video_segments.append(os.path.join(videos_for_i_url, file))
    if last_video_url:
        video_segments.append(last_video_url)
    # 创建临时的合并列表文件
    concat_list_path = os.path.join(videos_for_i_url, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for seg in video_segments:
            # 写入路径时统一使用斜杠
            f.write(f"file '{seg.replace('\\', '/')}'\n")

    # 1. 合并视频
    merged_video_path = f"{output_for_i_url}_merged.mp4"
    concat_cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_list_path,
        "-vf", f"scale={config.TARGET_RESOLUTION},fps={config.TARGET_FPS}",
        "-c:v", "libx264", "-crf", config.MERGE_CRF, "-preset", config.MERGE_PRESET,
        "-b:v", config.VIDEO_BITRATE, "-an", "-y", merged_video_path
    ]
    ffmpeg_utils.run_ffmpeg_command(concat_cmd)

    # 2. 添加音频
    current_path = merged_video_path
    if audio_file_url:
        audio_output_path = f"{output_for_i_url}_audio.mp4"
        audio_cmd = [
            "ffmpeg", "-i", merged_video_path, "-i", audio_file_url,
            "-c:v", "copy", # 视频流已符合要求，直接复制
            "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0",
            "-shortest", "-y", audio_output_path
        ]
        ffmpeg_utils.run_ffmpeg_command(audio_cmd)
        current_path = audio_output_path

    # 3. 添加字幕
    final_output_path = f"{output_for_i_url}.mp4"
    if caption_file_url:
        safe_caption_path = ffmpeg_utils.escape_ffmpeg_path(caption_file_url)
        subtitle_cmd = [
            "ffmpeg", "-i", current_path,
            "-vf", f"subtitles={safe_caption_path}:force_style='{config.SUBTITLE_STYLE}'",
            "-c:a", "copy", # 音频流已符合要求，直接复制
            "-c:v", "libx264", "-crf", config.SUBTITLE_CRF, "-preset", config.SUBTITLE_PRESET,
            "-y", final_output_path
        ]
        ffmpeg_utils.run_ffmpeg_command(subtitle_cmd)
    else:
        # 如果没有字幕，直接重命名
        os.rename(current_path, final_output_path)

    logger.info(f"视频合成完成: {final_output_path}")
    return final_output_path


def video_clips(video_type, completed_shots, video_dir, n, currunt_time):
    """
    根据视频类型和已完成的镜头生成视频片段
    :param video_type: 视频类型
    :param completed_shots: 已完成的镜头列表
    :param video_dir: 视频存储目录
    :param n: 当前镜头编号
    :param currunt_time: 当前时间戳
    """
    clip_name = f"{video_type}_{n}_{currunt_time}.mp4"
    clip_path = os.path.join(video_dir, clip_name)

    # 根据已完成镜头生成视频片段
    if completed_shots:
        concat_list_path = os.path.join(video_dir, "clip_concat_list.txt")
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for shot in completed_shots:
                f.write(f"file '{shot.replace('\\', '/')}'\n")

        clip_cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_list_path,
            "-c:v", "libx264", "-crf", config.CLIP_CRF, "-preset", config.CLIP_PRESET,
            "-b:v", config.CLIP_BITRATE, "-an", "-y", clip_path
        ]
        ffmpeg_utils.run_ffmpeg_command(clip_cmd)
    else:
        logger.warning("未提供任何已完成的镜头，无法生成视频片段。")
        return None

    logger.info(f"视频片段生成完成: {clip_path}")
    return clip_path


def video_generate(n, first_video_url, video_dir, last_video_url, audio_file_url, caption_file_url, currunt_time):
    """
    根据提供的参数生成完整视频
    :param n: 当前镜头编号
    :param first_video_url: 开头视频路径
    :param video_dir: 中间视频存储目录
    :param last_video_url: 结尾视频路径
    :param audio_file_url: 音频文件路径
    :param caption_file_url: 字幕文件路径
    :param currunt_time: 当前时间戳
    """
    for i in range(1, n + 1):
        output_for_i_url = os.path.join(video_dir, f"output_{i}_{currunt_time}")
        try:
            final_video_path = video_merge_export(
                output_for_i_url,
                first_video_url,
                video_dir,
                last_video_url,
                audio_file_url,
                caption_file_url
            )
            logger.info(f"完整视频生成完成: {final_video_path}")
            return final_video_path
        except Exception as e:
            logger.error(f"生成完整视频时出错: {e}")
            return None