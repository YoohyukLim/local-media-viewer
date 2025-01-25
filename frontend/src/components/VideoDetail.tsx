import React from 'react';
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
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
`;

const Tag = styled.span`
  background: #e9ecef;
  padding: 0.35rem 0.7rem;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background: #dee2e6;
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

interface Props {
  video: Video;
  onClose: () => void;
  onPrevVideo?: () => void;
  onNextVideo?: () => void;
  hasPrevVideo?: boolean;
  hasNextVideo?: boolean;
}

export const VideoDetail: React.FC<Props> = ({ 
  video, 
  onClose,
  onPrevVideo,
  onNextVideo,
  hasPrevVideo = false,
  hasNextVideo = false
}) => {
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
            {video.tags.map(tag => (
              <Tag key={tag.id}>
                {tag.name}
              </Tag>
            ))}
          </TagList>
        </InfoSection>
      </DetailContainer>
    </Overlay>
  );
}; 