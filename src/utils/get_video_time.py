import os
from moviepy.video.io.VideoFileClip import VideoFileClip

def get_video_durations(folder_path):
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
    results = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(video_extensions):
            video_path = os.path.join(folder_path, filename)
            try:
                clip = VideoFileClip(video_path)
                duration = clip.duration  # seconds (float)
                results.append((filename, duration))
                clip.close()
            except Exception as e:
                results.append((filename, f"Error: {e}"))
    return results

if __name__ == "__main__":
    folder = r"E:\py-workspace\python-video-plugin\temp\2025-09-12_02-44-16.803503\videos\1"
    durations = get_video_durations(folder)
    for name, duration in durations:
        print(f"{name}: {duration}")