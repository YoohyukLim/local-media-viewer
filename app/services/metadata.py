import os
import cv2
from datetime import datetime

def get_video_duration(video_path: str) -> float:
    """비디오 파일의 길이를 초 단위로 반환합니다."""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file - {video_path}")
            return 0.0

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0.0

        cap.release()
        return duration
    except Exception as e:
        print(f"Error getting duration for {video_path}: {str(e)}")
        return 0.0

def is_video_modified(file_path: str, video) -> bool:
    """비디오 파일이 DB 데이터 이후에 수정되었는지 확인합니다."""
    try:
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        return file_mtime > video.updated_at
    except Exception as e:
        print(f"Error checking modification time for {file_path}: {str(e)}")
        return False

def get_directory_tags(file_path: str, base_dir: str) -> list[str]:
    """파일이 포함된 디렉토리들의 이름을 태그로 반환합니다."""
    rel_path = os.path.relpath(os.path.dirname(file_path), base_dir)
    if rel_path == '.':
        return []
    directories = [d for d in rel_path.split(os.sep) if d]
    return directories

def read_video_metadata(file_path: str, base_dir: str) -> tuple[str | None, list[str]]:
    """비디오의 메타데이터 파일을 읽어 카테고리와 태그 목록을 반환합니다."""
    metadata_path = f"{os.path.splitext(file_path)[0]}.info"
    category = None
    tags = []
    
    tags.extend(get_directory_tags(file_path, base_dir))
    
    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('!'):
                        category = line[1:].strip()
                    elif line.startswith('#'):
                        tag = line[1:].strip()
                        if tag and tag not in tags:
                            tags.append(tag)
    except Exception as e:
        print(f"Error reading metadata for {file_path}: {str(e)}")
    
    return category, tags

def update_video_metadata(video, file_path: str, base_dir: str):
    """비디오의 메타데이터를 업데이트합니다."""
    category, tags = read_video_metadata(file_path, base_dir)
    if category is not None:
        video.category = category
    video.tags = tags 