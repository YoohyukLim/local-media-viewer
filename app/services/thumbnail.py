import os
import cv2

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

def ensure_thumbnail(video, file_path: str, settings) -> bool:
    """비디오의 썸네일이 존재하는지 확인하고, 없으면 생성합니다."""
    thumbnail_path = settings.get_thumbnail_path(video.thumbnail_id)
    
    # 썸네일이 없거나 비디오 파일이 더 최신인 경우
    if not os.path.exists(thumbnail_path) or (
        os.path.getmtime(file_path) > os.path.getmtime(thumbnail_path)
    ):
        return create_thumbnail(file_path, thumbnail_path)
    
    return True 