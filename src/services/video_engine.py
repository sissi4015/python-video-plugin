import subprocess
import os
import logging
import random
import uuid
import time

from pydantic_core import Url

# 路径设置
# input_dir = "D:\\BaiduNetdiskDownload\\分镜素材\\开头"      # 主视频素材目录
# intro_path = "path/to/intro.mp4"                           # 片头视频路径
# outro_path = "path/to/outro.mp4"                           # 片尾视频路径
# output_dir = "path/to/output"                              # 输出目录
# audio_path = "path/to/audio.mp3"                           # 要添加的音频文件路径
# subtitle_path = "path/to/subtitle.srt"                     # 要添加的字幕文件路径
# os.makedirs(output_dir, exist_ok=True)                     # 如果输出目录不存在则创建

# 视频素材库地址
VIDEO_LOCAL_DATABASE = r"D:\\material_database\\"
# 剪辑好的视频输出地址
OUTPUT_DIR = r"D:\\video_house\\"
# 视频文件格式
VIDEO_EXTENSIONS = ('.mp4', '.MP4', '.mov', '.MOV', '.avi', '.AVI')

# 每条草稿下，已经剪辑好的分镜视频地址
input_dir = ""
# 每条草稿下，已经剪辑好的分镜视频文件列表
main_video_files = []

logger = logging.getLogger("video_plugin")

# 视频生成主函数
def video_generate(n, first_video_url, video_dir, last_video_url, audio_file_url, caption_file_url, currunt_time):
    for i in range(1, n + 1):
        # 第i条视频的分段视频存放地址
        videos_for_i_url = video_dir + "\\" + str(i) 
        # 第i条视频的最终输出地址
        output_for_i_url = OUTPUT_DIR + "\\" + f"{currunt_time}_{i}"
        try:
            video_merge_export(output_for_i_url,first_video_url, videos_for_i_url, last_video_url, audio_file_url, caption_file_url)
        except Exception as e:
            logger.error(f"第{i}条视频:剪辑合成失败: {e}")
            continue

# 视频合成
def video_merge_export(output_for_i_url, first_video_url, videos_for_i_url, last_video_url, audio_file_url, caption_file_url):
    """
    合并开头视频、中间视频文件夹下的所有视频、片尾视频、音频和字幕，输出到OUTPUT_DIR
    """
    # 收集所有视频片段
    video_segments = []
    if first_video_url:
        video_segments.append(first_video_url)
    # 中间分镜视频
    for file in sorted(os.listdir(videos_for_i_url)):
        if file.endswith(VIDEO_EXTENSIONS):
            video_segments.append(os.path.join(videos_for_i_url, file))
    if last_video_url:
        video_segments.append(last_video_url)

    # 创建临时的合并列表文件
    concat_list_path = os.path.join(videos_for_i_url, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for seg in video_segments:
            f.write(f"file '{seg}'\n")

    # 合并视频
    merged_video_path = f"{output_for_i_url}_merged.mp4"
    concat_cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-vf", "scale=1080:1920,fps=30",  # 统一分辨率和帧率
        "-c:v", "libx264",
        "-crf", "20",  # 更高质量
        "-preset", "slow",  # 更慢但更优的压缩
        "-b:v", "5M",  # 设置视频比特率为5Mbps
        "-an",  # 不复制音频
        "-y",
        merged_video_path
    ]
    subprocess.run(concat_cmd, check=True, capture_output=True)

    # 等待合并后的视频是否生成成功
    while not os.path.exists(merged_video_path):
        logger.info("等待视频合成中...")
        time.sleep(1)

    # 添加音频
    if audio_file_url:
        audio_output_path = f"{output_for_i_url}_audio.mp4"
        audio_cmd = [
            "ffmpeg",
            "-i", merged_video_path,
            "-i", audio_file_url,
            "-c:v", "libx264",  # 与视频和字幕一致
            "-crf", "20",
            "-preset", "slow",
            "-b:v", "5M",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-y",
            audio_output_path
        ]
        subprocess.run(audio_cmd, check=True, capture_output=True)
    else:
        audio_output_path = merged_video_path

    # 等待添加音频后的视频是否生成成功
    while not os.path.exists(audio_output_path):
        logger.info("等待音频合成中...")
        time.sleep(1)

    # 添加字幕
    if caption_file_url:
        final_output_path = f"{output_for_i_url}.mp4"
        
        # safe_out_put_path = final_output_path.replace('\\', '/')
        # Use forward slashes for cross-platform compatibility with ffmpeg
        # safe_audio_output_path = audio_output_path.replace('\\', '/')

        # ffmpeg -i D:\\video_house\\2025-09-10_20-33-30.357655_1_audio.mp4 -vf subtitles='E\:\\py-workspace\\python-video-plugin\\temp\\2025-09-10_20-33-30.357655\\script\\captions.srt' -c:a copy -c:v libx264 -crf 23 -preset slow -y D:\\video_house\\2025-09-10_20-33-30.357655_1.mp4
        # ffmpeg -i D:\\video_house\\\2025-09-10_20-59-18.211608_1_audio.mp4 -vf subtitles='E\\:\\py-workspace\\python-video-plugin\\temp\\2025-09-10_20-59-18.211608\\script\\captions.srt' -c:a copy -c:v libx264 -crf 23 -preset slow -y D:\\video_house\\\2025-09-10_20-59-18.211608_1.mp4

        safe_caption_path = caption_file_url.replace('\\', '\\\\').replace(':', '\:')

        subtitle_cmd = [
            "ffmpeg",
            "-i", audio_output_path,
            "-vf", (
            f"subtitles='{safe_caption_path}':force_style="
            "'FontName=SimHei,FontSize=10,PrimaryColour=&FFFFFF,OutlineColour=&000000,"
            "BorderStyle=1,Outline=2,Shadow=1,Alignment=2,WrapStyle=0,MaxLines=1'"
            ),
            "-c:a", "copy",
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "slow",
            "-y",
            final_output_path
        ]
        try:
            subprocess.run(subtitle_cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"添加字幕失败. Command: {' '.join(e.cmd)}. Output: {e.stdout}. Error: {e.stderr}")
            raise
    else:
        final_output_path = audio_output_path

    logger.info(f"视频合成完成: {final_output_path}")
    return final_output_path



# 在素材库中检索合适的视频
def video_clips(video_type, shots, video_dir, n, currunt_time):
    """
    根据分镜数组shots，为n条视频做素材检索和粗剪。
    在本地素材库中，检索合适视频，粗略剪辑，输出视频片段到video_dir下的i文件夹。
    参数:
        video_type: 一级目录
        shots: 分镜数组，每个元素包含classify和duration
        video_dir: 输出目录
        n: 需要生成的视频数量
    """
    for i in range(1, n + 1):
        output_folder = os.path.join(video_dir, str(i))
        os.makedirs(output_folder, exist_ok=True)
        # 已使用的视频，避免重复使用
        used_videos = set()
        for idx, shot in enumerate(shots):
            classify = shot.get("classify")
            duration = shot.get("duration")
            # 检索素材库
            classify_dir = os.path.join(VIDEO_LOCAL_DATABASE, video_type, classify)
            candidates = []
            if os.path.exists(classify_dir):
                candidates = [
                f for f in os.listdir(classify_dir)
                if f.endswith(VIDEO_EXTENSIONS)
            ] 
            if not candidates:
                # 如果当前分类目录下没有视频，则在video_type目录下所有分类中随机选择一个视频
                # 包括video_type_dir下的视频和其所有一级子目录下的视频
                # 先查找video_type_dir下的视频
                video_type_dir = os.path.join(VIDEO_LOCAL_DATABASE, video_type)
                for f in os.listdir(video_type_dir):
                    file_path = os.path.join(video_type_dir, f)
                    if os.path.isfile(file_path) and f.endswith(VIDEO_EXTENSIONS):
                        candidates.append(file_path)
                # 再查找所有一级子目录下的视频
                for subdir in os.listdir(video_type_dir):
                    subdir_path = os.path.join(video_type_dir, subdir)
                    if os.path.isdir(subdir_path):
                        for f in os.listdir(subdir_path):
                            file_path = os.path.join(subdir_path, f)
                            if os.path.isfile(file_path) and f.endswith(VIDEO_EXTENSIONS):
                                candidates.append(file_path)
                
                if not candidates:
                    logger.warning(f"未找到任何素材: {video_type_dir}")
                    continue
            # 随机选择一个素材
            # 保证同一级目录下不重复选取视频
            while True:
                selected = random.choice(candidates)
                selected_video = os.path.join(classify_dir, selected) if not os.path.isabs(selected) else selected
                if selected_video not in used_videos:
                    used_videos.add(selected_video)
                    break
            # 粗剪视频片段
            output_clip_path = os.path.join(output_folder, f"{currunt_time}_{idx+1}.mp4")
            # 使用ffmpeg从第2秒开始剪辑duration秒
            ffmpeg_cmd = [
                "ffmpeg",
                "-ss", "2",
                "-i", selected_video,
                "-t", str(duration),
                "-vf", "scale=1080:1920,fps=30",  # 统一分辨率和帧率
                "-c:v", "libx264",
                "-crf", "20",  # 更高质量
                "-preset", "slow",  # 更慢但更优的压缩
                "-b:v", "5M",  # 设置视频比特率为5Mbps
                "-an",  # 禁用音频
                "-y",
                output_clip_path
            ]
            try:
                subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
                logger.info(f"生成分镜片段: {output_clip_path}")
            except Exception as e:
                logger.error(f"分镜片段剪辑失败: {output_clip_path}, 错误: {e}")
                continue