import subprocess
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

# 路径设置
# input_dir = "D:\\BaiduNetdiskDownload\\分镜素材\\开头"      # 主视频素材目录
# intro_path = "path/to/intro.mp4"                           # 片头视频路径
# outro_path = "path/to/outro.mp4"                           # 片尾视频路径
# output_dir = "path/to/output"                              # 输出目录
# audio_path = "path/to/audio.mp3"                           # 要添加的音频文件路径
# subtitle_path = "path/to/subtitle.srt"                     # 要添加的字幕文件路径
# os.makedirs(output_dir, exist_ok=True)                     # 如果输出目录不存在则创建

# 视频素材库地址
VIDEO_LOCAL_DATABASE = r"D:\\素材库\\"
# 剪辑好的视频输出地址
OUTPUT_DIR = r"D:\\自动化剪辑视频库\\"
# 视频文件格式
VIDEO_EXTENSIONS = ('.mp4', '.MP4', '.mov', '.MOV', '.avi', '.AVI')

# 每条草稿下，已经剪辑好的分镜视频地址
input_dir = ""
# 每条草稿下，已经剪辑好的分镜视频文件列表
main_video_files = []

logger = logging.getLogger("video_plugin")

def video_generate(video_type, shots, i, first_video_url, video_dir, last_video_url, audio_file_url, caption_file_url):


    # 第i条视频的分段视频存放地址
    videos_for_i_url = video_dir + "\\" + str(i)
    # 根据分镜检索视频
    try:
        search_videos(video_type, shots, videos_for_i_url)
        logger.info(f"第{i}条视频:检索视频success")
    except Exception as e:
        logger.error(f"第{i}条视频:检索视频失败: {e}")
        return

    # 获取所有主视频文件（支持多种格式）
    main_video_files = [f for f in os.listdir(videos_for_i_url) if f.endswith(VIDEO_EXTENSIONS)]
    if not main_video_files:
        print("输入目录中没有找到主视频文件。")
        exit(1)
    """
    处理单个视频文件：
    1. 剪裁主视频为10秒
    2. 拼接片头、主视频、片尾
    3. 添加音频和字幕
    4. 清理临时文件
    """
    input_path = os.path.join(input_dir, filename)                     # 主视频完整路径
    output_path = os.path.join(output_dir, f"final_{filename}")        # 最终输出路径

    # 步骤1：将主视频剪裁为10秒
    # temp_clip_path = os.path.join(output_dir, f"temp_10s_{filename}")  # 临时剪裁文件路径
    # trim_cmd = [
    #     'ffmpeg',
    #     '-i', input_path,
    #     '-ss', '00:00:00',   # 从0秒开始
    #     '-t', '00:00:10',    # 持续10秒
    #     '-c', 'copy',        # 流复制，不重新编码，速度快
    #     '-y',                # 覆盖输出文件
    #     temp_clip_path
    # ]

    # 步骤2：拼接片头、剪裁主视频、片尾
    # 创建一个文件列表，供FFmpeg concat使用
    list_file_path = os.path.join(output_dir, f"concat_list_{filename}.txt")
    with open(list_file_path, 'w') as f:
        f.write(f"file '{os.path.abspath(first_video_url)}'\n")
        f.write(f"file '{os.path.abspath(videos_for_i_url)}'\n")
        f.write(f"file '{os.path.abspath(last_video_url)}'\n")

    # 拼接后的临时文件
    concat_path = os.path.join(output_dir, f"concat_{filename}")
    concat_cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', list_file_path,
        '-c', 'copy',        # 流复制拼接
        '-y',
        concat_path
    ]

    # 步骤3：添加音频和字幕
    # -vf subtitles=xxx.srt 添加字幕
    # -i audio_path 添加音频
    # -map 0:v:0 只用第一个视频流
    # -map 1:a:0 只用第二个输入的音频流
    # -c:v copy 视频流直接复制
    # -c:a aac 音频转码为aac
    final_cmd = [
        'ffmpeg',
        '-i', concat_path,
        '-i', audio_file_url,
        '-vf', f"subtitles={caption_file_url}",
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-y',
        output_path
    ]

    try:
        # 执行切割命令，生成10秒主视频
        # subprocess.run(trim_cmd, check=True, capture_output=True)
        # 执行拼接命令，合成片头+主视频+片尾
        subprocess.run(concat_cmd, check=True, capture_output=True)
        # 执行添加音频和字幕命令，生成最终视频
        subprocess.run(final_cmd, check=True, capture_output=True)
        print(f"成功: {filename}")

        # 步骤4：清理临时文件，避免磁盘空间浪费
        os.remove(temp_clip_path)
        os.remove(list_file_path)
        if os.path.exists(concat_path):
            os.remove(concat_path)
        return True

    except subprocess.CalledProcessError as e:
        # 捕获FFmpeg执行异常，输出错误信息
        print(f"处理 {filename} 失败，错误信息: {e.stderr.decode('utf-8', errors='ignore')}")
        # 清理可能残留的临时文件
        if os.path.exists(temp_clip_path):
            os.remove(temp_clip_path)
        if os.path.exists(list_file_path):
            os.remove(list_file_path)
        if os.path.exists(concat_path):
            os.remove(concat_path)
        return False

# 使用线程池并行处理视频文件，提高批量处理速度
# max_workers建议不超过CPU核心数
max_workers = 4

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    # 提交所有视频处理任务
    future_to_file = {executor.submit(video_generate, file): file for file in main_video_files}

    # 等待所有任务完成，并捕获异常
    for future in as_completed(future_to_file):
        file = future_to_file[future]
        try:
            future.result()
        except Exception as exc:
            print(f'{file}  generated an exception: {exc}')



# 在素材库中检索合适的视频
def search_videos(video_type, shots, video_dir):
    """
    在本地素材库OUTPUT_DIR中，根据video_type找到对应的一级文件夹，
    根据shot的classify属性，找到二级文件夹，随机抽取shots数组长度个数的视频，
    剪辑为符合shot时长的视频，输出到video_url对应的路径中，
    剪辑好的视频，按照分镜顺序，分别命名为1.mov,2.mov,3.mov,以此类推
    """
    result_paths = []
    type_dir = os.path.join(VIDEO_LOCAL_DATABASE, video_type)
    if not os.path.exists(type_dir):
        print(f"未找到类型文件夹: {type_dir}")
        return []

    for idx, shot in enumerate(shots, start=1):
        
        shot_classify = shot['classify']
        classify_dir = os.path.join(type_dir, shot_classify)
        if not os.path.exists(classify_dir):
            shot_classify = "其他"
            print(f"未找到分类文件夹: {classify_dir} 按照[其他]处理")
        else:
            video_files = [f for f in os.listdir(classify_dir) if f.endswith(VIDEO_EXTENSIONS)]
            if not video_files:
                shot_classify = "其他"
                print(f"分类文件夹中没有视频: {classify_dir} 按照[其他]处理")


        all_video_files = []     
        if shot_classify == "其他":
            # 在type_dir下的所有子文件夹中，随机抽取一条视频
            for subfolder in os.listdir(type_dir):
                subfolder_path = os.path.join(type_dir, subfolder)
                if os.path.isdir(subfolder_path):
                    files = [f for f in os.listdir(subfolder_path) if f.endswith(VIDEO_EXTENSIONS)]
                    all_video_files.extend([os.path.join(subfolder_path, f) for f in files])        
        else:
            all_video_files = [f for f in os.listdir(classify_dir) if f.endswith(VIDEO_EXTENSIONS)]
        
        if not all_video_files:
            print(f"类型文件夹下没有视频: {type_dir}")
            return
        
        # 在所有符合条件的文件中，随机抽取一个
        org_video_i = random.choice(all_video_files)
        # 剪辑后的视频存放地址
        os.makedirs(video_dir, exist_ok=True)
        new_video_i = os.path.join(video_dir, f"{idx}.mov")
        
        # 剪辑为符合shot时长的视频
        trim_cmd = [
            'ffmpeg',
            '-i', org_video_i,
            '-ss', '00:00:00',
            '-t', str(shot['duration']),
            '-c:v', 
            'copy',
            '-an',  # 移除音频
            '-y',
            new_video_i
        ]
        try:
            subprocess.run(trim_cmd, check=True, capture_output=True)
            result_paths.append(new_video_i)
        except subprocess.CalledProcessError as e:
            print(f"剪辑 {org_video_i} 失败: {e.stderr.decode('utf-8', errors='ignore')}")
            continue

    return result_paths

