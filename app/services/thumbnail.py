import os
import cv2

def create_thumbnail(video_path: str, thumbnail_path: str) -> bool:
    """비디오 파일의 중간 프레임을 썸네일로 저장합니다."""
    try:
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
            # 전체 프레임 수 가져오기
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                print(f"Error: Invalid frame count for {video_path}")
                return False
            
            # 중간 프레임으로 이동
            middle_frame = total_frames // 2
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
            
            # 프레임 읽기
            ret, frame = cap.read()
            if not ret:
                print(f"Error: Could not read frame from {video_path}")
                return False
            
            # 이미지 크기 조정 (최대 1080px)
            height, width = frame.shape[:2]
            if width > 1080:
                scale = 1080 / width
                new_width = 1080
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # 썸네일 저장
            cv2.imwrite(thumbnail_path, frame)
            return True
            
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
        return create_thumbnail(file_path, thumbnail_path)
    
    return True 