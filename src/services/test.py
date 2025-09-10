import subprocess

def merge_video_audio_subtitle(video_path, audio_path, subtitle_path, output_path):
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-vf', f"subtitles={subtitle_path}",
        output_path
    ]
    subprocess.run(cmd, check=True)

# 示例用法
if __name__ == "__main__":
    video = 'input_video.mp4'
    audio = 'input_audio.aac'
    subtitle = 'input_subtitle.srt'
    output = 'output_merged.mp4'
    merge_video_audio_subtitle(video, audio, subtitle, output)



# 测试调用
merge_video_audio_subtitle('D:\\自动化剪辑视频库\\1_merged.mp4', 'E:\\py-workspace\\python-video-plugin\\temp\\2025-09-10_04-01-35.238420\\audios\\oral.wav', 'sample_subtitle.srt', 'final_output.mp4')