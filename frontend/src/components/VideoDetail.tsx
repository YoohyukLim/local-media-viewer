import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { Video } from '../types/video';

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 2rem;
  z-index: 1000;
  overflow-y: auto;
`;

const DetailContainer = styled.div`
  background: white;
  border-radius: 8px;
  width: 100%;
  max-width: 800px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
`;

const ThumbnailSection = styled.div`
  width: 100%;
  aspect-ratio: 1.9/1;
  background: black;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    transition: opacity 0.2s;
    
    &:hover {
      opacity: 0.8;
    }
  }
`;

const InfoSection = styled.div`
  padding: 2rem;
  
  h2 {
    margin: 0 0 1rem 0;
    font-size: 1.5rem;
    padding-right: 2rem;
    word-break: break-all;
  }
`;

const CloseButton = styled.div`
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  transition: background-color 0.2s;
  
  &:hover {
    background: rgba(0, 0, 0, 0.7);
  }
  
  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 1.2rem;
    height: 2px;
    background: white;
    transform-origin: center;
  }
  
  &::before {
    transform: rotate(45deg);
  }
  
  &::after {
    transform: rotate(-45deg);
  }
`;

const MetaInfo = styled.div`
  margin-bottom: 1.5rem;
  color: #666;
  font-size: 0.9rem;
  
  > div {
    margin-bottom: 0.5rem;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
`;

const TagList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
`;

const Tag = styled.span`
  background: #e9ecef;
  padding: 0.35rem 0.7rem;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  
  &:hover {
    background: #dee2e6;
  }
`;

const AddTagButton = styled.button`
  background: none;
  border: 1px dashed #adb5bd;
  border-radius: 20px;
  padding: 0.35rem 0.7rem;
  font-size: 0.9rem;
  color: #868e96;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  
  &:hover {
    background: #f8f9fa;
    border-color: #868e96;
    color: #495057;
  }
`;

const TagInput = styled.div`
  display: flex;
  gap: 0.5rem;
  align-items: center;
  
  input {
    padding: 0.35rem 0.7rem;
    border: 1px solid #ced4da;
    border-radius: 20px;
    font-size: 0.9rem;
    outline: none;
    
    &:focus {
      border-color: #339af0;
      box-shadow: 0 0 0 2px rgba(51, 154, 240, 0.25);
    }
  }
  
  button {
    padding: 0.35rem 0.7rem;
    border: none;
    border-radius: 4px;
    font-size: 0.9rem;
    cursor: pointer;
    
    &.confirm {
      background: #339af0;
      color: white;
      
      &:hover {
        background: #228be6;
      }
    }
    
    &.cancel {
      background: #e9ecef;
      color: #495057;
      
      &:hover {
        background: #dee2e6;
      }
    }
  }
`;

const NavigationButtons = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
`;

const NavButton = styled.button`
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #495057;
  transition: all 0.2s;
  
  &:hover:not(:disabled) {
    background: #e9ecef;
    border-color: #ced4da;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const TagActionButtons = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-left: auto;

  button {
    width: 32px;
    height: 32px;
    padding: 0;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    
    &.confirm {
      background: #339af0;
      color: white;
      
      &:hover {
        background: #228be6;
      }

      &::before {
        content: '✓';
        font-size: 1.2rem;
      }
    }
    
    &.cancel {
      background: #fa5252;
      color: white;
      
      &:hover {
        background: #e03131;
      }

      &::before {
        content: '×';
        font-size: 1.4rem;
      }
    }
  }
`;

interface Props {
  video: Video;
  onClose: () => void;
  onPrevVideo?: () => void;
  onNextVideo?: () => void;
  hasPrevVideo?: boolean;
  hasNextVideo?: boolean;
  onTagsUpdate?: (tags: Video['tags']) => void;
  onTagClick?: (tag: { id: number; name: string }) => void;
}

export const VideoDetail: React.FC<Props> = ({ 
  video, 
  onClose,
  onPrevVideo,
  onNextVideo,
  hasPrevVideo = false,
  hasNextVideo = false,
  onTagsUpdate,
  onTagClick
}) => {
  const [isAddingTag, setIsAddingTag] = useState(false);
  const [newTagName, setNewTagName] = useState('');
  const [modifiedTags, setModifiedTags] = useState<Video['tags']>(video.tags);
  const [isModified, setIsModified] = useState(false);

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleVideoClick = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`/api/videos/play/${video.id}`, {
        method: 'POST',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to play video');
      }
    } catch (error: unknown) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request was aborted');
      } else {
        console.error('Error playing video:', error);
      }
    }
  };

  useEffect(() => {
    // video prop이 변경될 때마다 modifiedTags 업데이트
    setModifiedTags(video.tags);
    setIsModified(false);
  }, [video]);

  const handleAddTag = () => {
    if (!newTagName.trim()) return;

    // 임시 태그 ID 생성 (실제 저장 시 서버에서 할당될 ID)
    const tempTag = {
      id: -Date.now(),  // 임시 음수 ID로 구분
      name: newTagName.trim()
    };

    setModifiedTags(prev => [...prev, tempTag]);
    setIsModified(true);
    setNewTagName('');
    setIsAddingTag(false);
  };

  const handleTagClick = (tagToRemove: { id: number; name: string }) => {
    // 태그 클릭 시 삭제
    setModifiedTags(prev => prev.filter(tag => tag.id !== tagToRemove.id));
    setIsModified(true);
  };

  const handleConfirmChanges = async () => {
    try {
      // 새로 추가된 태그들 (음수 ID)
      const newTags = modifiedTags.filter(tag => tag.id < 0);
      
      // 삭제된 태그들 (원본 태그 중 modifiedTags에 없는 것들)
      const deletedTags = video.tags.filter(
        originalTag => !modifiedTags.some(tag => tag.id === originalTag.id)
      );

      // 새 태그 추가
      for (const tag of newTags) {
        const response = await fetch(`/api/videos/${video.id}/tags`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: tag.name })
        });

        if (!response.ok) throw new Error('Failed to add tag');
      }

      // 태그 삭제
      for (const tag of deletedTags) {
        const response = await fetch(`/api/videos/${video.id}/tags/${tag.id}`, {
          method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete tag');
      }

      // 모든 변경사항이 성공적으로 저장되면 상위 컴포넌트에 알림
      onTagsUpdate?.(modifiedTags);
      setIsModified(false);
    } catch (error) {
      console.error('Error saving tag changes:', error);
    }
  };

  const handleCancelChanges = () => {
    setModifiedTags(video.tags);
    setIsModified(false);
  };

  // 키보드 이벤트 핸들러 추가
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowLeft':
          if (hasPrevVideo && onPrevVideo) {
            onPrevVideo();
          }
          break;
        case 'ArrowRight':
          if (hasNextVideo && onNextVideo) {
            onNextVideo();
          }
          break;
        case 'Escape':
          onClose();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    
    // 컴포넌트 언마운트 시 이벤트 리스너 제거
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [onPrevVideo, onNextVideo, onClose, hasPrevVideo, hasNextVideo]);

  return (
    <Overlay onClick={onClose}>
      <DetailContainer onClick={e => e.stopPropagation()}>
        <ThumbnailSection onClick={handleVideoClick}>
          <CloseButton onClick={(e) => {
            e.stopPropagation();
            onClose();
          }} />
          <img 
            src={`/api/videos/thumbnails/${video.thumbnail_id}`}
            alt={video.file_name}
            title="Click to play video"
          />
        </ThumbnailSection>
        <InfoSection>
          <h2>{video.file_name}</h2>
          <MetaInfo>
            <div>재생 시간: {formatDuration(video.duration)}</div>
            <div>파일 경로: {video.file_path}</div>
            <div>생성일: {formatDate(video.created_at)}</div>
            <div>수정일: {formatDate(video.updated_at)}</div>
            {video.category && <div>카테고리: {video.category}</div>}
          </MetaInfo>
          <NavigationButtons>
            <NavButton 
              onClick={onPrevVideo}
              disabled={!hasPrevVideo}
            >
              ← 이전 비디오
            </NavButton>
            <NavButton 
              onClick={onNextVideo}
              disabled={!hasNextVideo}
            >
              다음 비디오 →
            </NavButton>
          </NavigationButtons>
          <TagList>
            {modifiedTags.map(tag => (
              <Tag 
                key={tag.id} 
                onClick={() => handleTagClick(tag)}
                title="클릭하여 태그 삭제"
              >
                {tag.name}
              </Tag>
            ))}
            {isAddingTag ? (
              <TagInput>
                <input
                  type="text"
                  value={newTagName}
                  onChange={e => setNewTagName(e.target.value)}
                  placeholder="태그 입력..."
                  autoFocus
                  onKeyDown={e => {
                    if (e.key === 'Enter') handleAddTag();
                    if (e.key === 'Escape') setIsAddingTag(false);
                  }}
                />
                <button className="confirm" onClick={handleAddTag}>확인</button>
                <button className="cancel" onClick={() => setIsAddingTag(false)}>취소</button>
              </TagInput>
            ) : (
              <AddTagButton onClick={() => setIsAddingTag(true)}>
                <span>+</span>
                <span>태그 추가</span>
              </AddTagButton>
            )}
            {isModified && (
              <TagActionButtons>
                <button 
                  className="confirm" 
                  onClick={handleConfirmChanges}
                  title="변경사항 저장"
                />
                <button 
                  className="cancel" 
                  onClick={handleCancelChanges}
                  title="변경사항 취소"
                />
              </TagActionButtons>
            )}
          </TagList>
        </InfoSection>
      </DetailContainer>
    </Overlay>
  );
}; 