import os
import cv2
import numpy as np
from sqlalchemy.orm import Session
from ..models.video import Video
from ..config import settings
from datetime import datetime

def create_thumbnail(video_path: str, output_path: str, max_size: int = 1080):
    """비디오 파일로부터 썸네일을 생성합니다."""
    try:
        # 비디오 파일 열기
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file - {video_path}")
            return False

        # 비디오의 중간 프레임으로 이동
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)

        # 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            print(f"Error: Could not read frame from video - {video_path}")
            return False

        # 이미지 크기 조정
        height, width = frame.shape[:2]
        if width > height:
            if width > max_size:
                new_width = max_size
                new_height = int(height * (max_size / width))
        else:
            if height > max_size:
                new_height = max_size
                new_width = int(width * (max_size / height))
        
        if width > max_size or height > max_size:
            frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # 썸네일 저장
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, frame)
        
        cap.release()
        return True
    except Exception as e:
        print(f"Error creating thumbnail for {video_path}: {str(e)}")
        return False

def ensure_thumbnail(video: Video, file_path: str) -> bool:
    """비디오의 썸네일이 존재하는지 확인하고, 없으면 생성합니다."""
    thumbnail_path = settings.get_thumbnail_path(video.thumbnail_id)
    
    # 썸네일이 없거나 비디오 파일이 더 최신인 경우
    if not os.path.exists(thumbnail_path) or (
        os.path.getmtime(file_path) > os.path.getmtime(thumbnail_path)
    ):
        return create_thumbnail(file_path, thumbnail_path)
    
    return True

def get_video_duration(video_path: str) -> float:
    """비디오 파일의 길이를 초 단위로 반환합니다."""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file - {video_path}")
            return 0.0

        # 프레임 수와 FPS로 영상 길이 계산
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0.0

        cap.release()
        return duration
    except Exception as e:
        print(f"Error getting duration for {video_path}: {str(e)}")
        return 0.0

def is_video_modified(file_path: str, video: Video) -> bool:
    """비디오 파일이 DB 데이터 이후에 수정되었는지 확인합니다."""
    try:
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        return file_mtime > video.updated_at
    except Exception as e:
        print(f"Error checking modification time for {file_path}: {str(e)}")
        return False

def get_directory_tags(file_path: str, base_dir: str) -> list[str]:
    """파일이 포함된 디렉토리들의 이름을 태그로 반환합니다."""
    # base_dir과 file_path의 상대 경로를 구함
    rel_path = os.path.relpath(os.path.dirname(file_path), base_dir)
    
    # 상대 경로가 현재 디렉토리('.')인 경우 빈 리스트 반환
    if rel_path == '.':
        return []
    
    # 경로를 디렉토리 이름들로 분리하고 빈 문자열 제거
    directories = [d for d in rel_path.split(os.sep) if d]
    return directories

def read_video_metadata(file_path: str, base_dir: str) -> tuple[str | None, list[str]]:
    """비디오의 메타데이터 파일을 읽어 카테고리와 태그 목록을 반환합니다."""
    metadata_path = f"{os.path.splitext(file_path)[0]}.info"
    category = None
    tags = []
    
    # 디렉토리 이름들을 태그로 추가
    tags.extend(get_directory_tags(file_path, base_dir))
    
    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('!'):
                        # 카테고리는 마지막에 나온 것을 사용
                        category = line[1:].strip()
                    elif line.startswith('#'):
                        # 태그 추가
                        tag = line[1:].strip()
                        if tag and tag not in tags:
                            tags.append(tag)
    except Exception as e:
        print(f"Error reading metadata for {file_path}: {str(e)}")
    
    return category, tags

def update_video_metadata(video: Video, file_path: str, base_dir: str):
    """비디오의 메타데이터를 업데이트합니다."""
    category, tags = read_video_metadata(file_path, base_dir)
    if category is not None:
        video.category = category
    video.tags = tags

def is_file_in_video_directories(file_path: str, video_directories: list[str]) -> bool:
    """파일이 설정된 비디오 디렉토리 중 하나에 포함되어 있는지 확인합니다."""
    file_path = os.path.normpath(file_path)
    for dir_path in video_directories:
        dir_path = os.path.normpath(dir_path)
        if file_path.startswith(dir_path):
            return True
    return False

def remove_missing_videos(db: Session, existing_files: set[str], video_directories: list[str]):
    """실제로 존재하지 않거나 설정된 디렉토리 외부에 있는 비디오 파일들을 DB에서 삭제합니다."""
    # DB의 모든 비디오 가져오기
    all_videos = db.query(Video).all()
    
    for video in all_videos:
        # 파일이 존재하지 않거나 설정된 디렉토리 외부에 있는 경우
        if (video.file_path not in existing_files or 
            not is_file_in_video_directories(video.file_path, video_directories)):
            print(f"Removing video from DB: {video.file_path}")
            # 썸네일 파일 삭제
            try:
                thumbnail_path = settings.get_thumbnail_path(video.thumbnail_id)
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
            except Exception as e:
                print(f"Error removing thumbnail file: {str(e)}")
            # DB에서 비디오 정보 삭제
            db.delete(video)
    
    db.commit()

def reload_settings() -> None:
    """설정 파일을 다시 로드합니다."""
    global settings
    from ..config import Settings
    settings = Settings()

def scan_videos(db: Session):
    """설정된 디렉토리들의 비디오 파일들을 스캔하여 DB에 저장합니다."""
    # 설정 파일 다시 로드
    reload_settings()
    
    video_extensions = ('.mp4', '.avi', '.mkv', '.mov')
    existing_files = set()  # 실제 존재하는 파일 경로들
    
    for base_dir in settings.VIDEO_DIRECTORIES:
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(video_extensions):
                    file_path = os.path.join(root, file)
                    existing_files.add(file_path)  # 존재하는 파일 기록
                    
                    # DB에 이미 존재하는지 확인
                    existing_video = db.query(Video).filter(Video.file_path == file_path).first()
                    if existing_video:
                        # 파일이 수정되었는지 확인
                        if is_video_modified(file_path, existing_video):
                            print(f"Updating modified video: {file_path}")
                            # 썸네일 재생성
                            if not ensure_thumbnail(existing_video, file_path):
                                print(f"Failed to create thumbnail for existing video: {file_path}")
                            
                            # 영상 길이와 메타데이터 업데이트
                            duration = get_video_duration(file_path)
                            if duration > 0:
                                existing_video.duration = duration
                                existing_video.file_name = Video.get_file_name(file_path)
                                update_video_metadata(existing_video, file_path, base_dir)
                                db.add(existing_video)
                        else:
                            # 썸네일과 메타데이터만 확인
                            if not ensure_thumbnail(existing_video, file_path):
                                print(f"Failed to create thumbnail for existing video: {file_path}")
                            update_video_metadata(existing_video, file_path, base_dir)
                            db.add(existing_video)
                    else:
                        # 새 비디오 추가
                        thumbnail_id = Video.generate_thumbnail_id()
                        thumbnail_path = settings.get_thumbnail_path(thumbnail_id)
                        
                        # 썸네일 생성 및 영상 길이 가져오기
                        if create_thumbnail(file_path, thumbnail_path):
                            duration = get_video_duration(file_path)
                            video = Video(
                                file_path=file_path,
                                file_name=Video.get_file_name(file_path),
                                thumbnail_id=thumbnail_id,
                                duration=duration,
                                tags=[]  # 기본값 설정
                            )
                            update_video_metadata(video, file_path, base_dir)
                            db.add(video)
                        else:
                            print(f"Skipping {file_path} due to thumbnail creation failure")
    
    # 실제로 존재하지 않거나 설정된 디렉토리 외부에 있는 파일들을 DB에서 삭제
    remove_missing_videos(db, existing_files, settings.VIDEO_DIRECTORIES)
    
    db.commit()

def get_videos(db: Session):
    """저장된 모든 비디오 목록을 반환합니다."""
    videos = db.query(Video).all()
    # 썸네일 전체 경로 추가
    for video in videos:
        video.thumbnail_path = settings.get_thumbnail_path(video.thumbnail_id)
    return videos 