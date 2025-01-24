import os
import cv2
import numpy as np
from PIL import Image
from app.config import Settings

def create_thumbnail(video_path: str, thumbnail_path: str, settings: Settings) -> bool:
    """비디오 파일의 중간 부분에서 프레임을 추출하여 WebP 애니메이션으로 저장합니다."""
    try:
        # 설정에서 값 가져오기
        duration_sec = settings.THUMBNAIL_DURATION
        fps = settings.THUMBNAIL_FPS
        max_size = settings.THUMBNAIL_MAX_SIZE
        
        # 경로를 운영체제에 맞게 정규화
        video_path = os.path.normpath(video_path)
        thumbnail_path = os.path.normpath(thumbnail_path)
        
        # 썸네일 디렉토리 생성
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        
        # 비디오 파일 열기
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file - {video_path}")
            return False
        
        try:
            # 전체 프레임 수와 원본 FPS 가져오기
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            if total_frames <= 0 or video_fps <= 0:
                print(f"Error: Invalid frame count or FPS for {video_path}")
                return False
            
            # 중간 지점 계산
            middle_frame = total_frames // 2
            start_frame = middle_frame - int(duration_sec * video_fps / 2)
            start_frame = max(0, start_frame)  # 시작 프레임이 0 이하가 되지 않도록
            
            # 추출할 프레임 수 계산
            frames_to_extract = int(duration_sec * fps)
            frame_interval = int(video_fps / fps)
            
            # 시작 위치로 이동
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            frames = []
            for _ in range(frames_to_extract):
                # 프레임 읽기
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 이미지 크기 조정 (최대 max_size px)
                height, width = frame.shape[:2]
                if width > height:
                    if width > max_size:
                        scale = max_size / width
                        new_width = max_size
                        new_height = int(height * scale)
                        frame = cv2.resize(frame, (new_width, new_height))
                else:
                    if height > max_size:
                        scale = max_size / height
                        new_width = int(width * scale)
                        new_height = max_size
                        frame = cv2.resize(frame, (new_width, new_height))
                
                # BGR에서 RGB로 변환
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(frame_rgb))
                
                # 다음 프레임으로 이동
                for _ in range(frame_interval - 1):
                    cap.read()
            
            if frames:
                # WebP 애니메이션으로 저장
                duration_ms = int(1000 / fps)  # 프레임당 지속 시간 (밀리초)
                frames[0].save(
                    thumbnail_path,
                    format='WEBP',
                    append_images=frames[1:],
                    save_all=True,
                    duration=duration_ms,
                    loop=0,
                    quality=80,
                    method=6  # 최상의 압축
                )
                return True
            
            return False
            
        finally:
            cap.release()
            
    except Exception as e:
        print(f"Error creating thumbnail for {video_path}: {str(e)}")
        return False

def ensure_thumbnail(video, file_path: str, settings) -> bool:
    """비디오의 썸네일이 존재하는지 확인하고, 없으면 생성합니다."""
    thumbnail_path = settings.get_thumbnail_path(video.thumbnail_id)
    
    # 썸네일이 없거나 비디오 파일이 더 최신인 경우
    if not os.path.exists(thumbnail_path) or (
        os.path.getmtime(file_path) > os.path.getmtime(thumbnail_path)
    ):
        return create_thumbnail(file_path, thumbnail_path, settings)
    
    return True 