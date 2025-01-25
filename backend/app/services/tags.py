from sqlalchemy.orm import Session
from app.models.tag import Tag
from app.models.video import Video
from typing import List, Tuple
from ..config import settings  # 싱글톤 settings import
from ..logger import logger
import os

def update_info_file_tags(file_path: str, tags_to_add: List[str] = None, tags_to_remove: List[str] = None):
    """비디오의 .info 파일의 태그를 수정합니다."""
    metadata_path = f"{os.path.splitext(file_path)[0]}.info"
    
    # 현재 파일 내용 읽기
    lines = []
    category = None
    current_tags = set()
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('!'):
                    category = line
                    lines.append(line)
                elif line.startswith('#'):
                    tag = line[1:].strip()
                    if tags_to_remove and tag in tags_to_remove:
                        continue  # 제거할 태그는 건너뛰기
                    current_tags.add(tag)
                    lines.append(line)
    
    # 새로운 태그 추가
    if tags_to_add:
        for tag in tags_to_add:
            if tag not in current_tags:
                lines.append(f"#{tag}")
    
    # 파일 쓰기
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
        if lines and not lines[-1].endswith('\n'):
            f.write('\n')

def get_or_create_tag(db: Session, tag_name: str) -> Tag:
    """태그를 가져오거나 없으면 생성합니다."""
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        db.add(tag)
        try:
            db.flush()  # commit 전에 flush하여 ID 생성
        except:
            db.rollback()
            raise
    return tag

def update_video_tags(db: Session, video: Video, tag_names: List[str]):
    """비디오의 태그를 업데이트합니다."""
    try:
        # 기존 태그 모두 제거
        video.tags.clear()
        
        # 새로운 태그 추가
        for tag_name in tag_names:
            if tag_name.strip():  # 빈 태그 제외
                tag = get_or_create_tag(db, tag_name.strip())
                video.tags.append(tag)
        
        db.commit()  # 여기서 한 번에 커밋
    except:
        db.rollback()
        raise

def get_all_tags(db: Session) -> List[Tag]:
    """모든 태그 목록을 반환합니다."""
    return db.query(Tag).all()

def add_video_tag(db: Session, video_id: int, tag_name: str) -> Tuple[Video, bool]:
    """비디오에 태그를 추가합니다."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        return None, False
    
    # 이미 존재하는 태그인지 확인
    if any(tag.name == tag_name for tag in video.tags):
        return video, False
        
    # 태그 추가
    tag = get_or_create_tag(db, tag_name)
    video.tags.append(tag)
    db.commit()
    
    # info 파일 업데이트
    update_info_file_tags(video.file_path, tags_to_add=[tag_name])
    
    return video, True

def remove_video_tag(db: Session, video_id: int, tag_id: int) -> Tuple[Video, bool]:
    """비디오에서 태그를 제거합니다."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        return None, False
    
    # 태그 찾기
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag or tag not in video.tags:
        return video, False
    
    # 태그 제거
    video.tags.remove(tag)
    db.commit()
    
    # info 파일 업데이트
    update_info_file_tags(video.file_path, tags_to_remove=[tag.name])
    
    return video, True

def cleanup_unused_tags(db: Session):
    """사용되지 않는 태그들을 삭제합니다."""
    unused_tags = db.query(Tag).filter(~Tag.videos.any()).all()
    
    for tag in unused_tags:
        db.delete(tag)
    
    if unused_tags:
        logger.info(f"Removed {len(unused_tags)} unused tags")
        db.commit() 