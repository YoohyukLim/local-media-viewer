from sqlalchemy.orm import Session
from ..models.tag import Tag
from ..models.video import Video
from typing import List

def get_or_create_tag(db: Session, tag_name: str) -> Tag:
    """태그를 가져오거나 없으면 생성합니다."""
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        db.add(tag)
        db.commit()
    return tag

def update_video_tags(db: Session, video: Video, tag_names: List[str]):
    """비디오의 태그를 업데이트합니다."""
    # 기존 태그 모두 제거
    video.tags.clear()
    
    # 새로운 태그 추가
    for tag_name in tag_names:
        if tag_name.strip():  # 빈 태그 제외
            tag = get_or_create_tag(db, tag_name.strip())
            video.tags.append(tag)

def get_all_tags(db: Session) -> List[Tag]:
    """모든 태그 목록을 반환합니다."""
    return db.query(Tag).all()

def search_videos_by_tags(db: Session, tags: List[str], require_all: bool = False):
    """태그로 비디오를 검색합니다."""
    query = db.query(Video).distinct()
    
    if require_all:
        # 모든 태그를 포함하는 비디오 검색
        for tag in tags:
            query = query.filter(Video.tags.any(Tag.name == tag))
    else:
        # 태그 중 하나라도 포함하는 비디오 검색
        query = query.filter(Video.tags.any(Tag.name.in_(tags)))
    
    return query.all() 