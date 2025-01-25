import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Video } from '../types/video';
import { VideoDetail } from './VideoDetail';

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1rem;
  padding: 1rem;
`;

const VideoCard = styled.div`
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  
  img {
    width: 100%;
    aspect-ratio: 16/9;
    object-fit: cover;
    background: #f8f9fa;
    cursor: pointer;
    
    &:hover {
      opacity: 0.8;
    }
  }
  
  .info {
    padding: 0.5rem;
    
    h3 {
      margin: 0 0 0.5rem 0;
      font-size: 0.9rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .meta {
      font-size: 0.8rem;
      color: #666;
      margin-bottom: 0.5rem;
    }
    
    .tags {
      display: flex;
      flex-wrap: wrap;
      gap: 0.25rem;
      max-height: 3.2rem;
      overflow: hidden;
    }
  }
`;

const Tag = styled.span`
  background: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  white-space: nowrap;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
  
  &:hover {
    background: #dee2e6;
  }
`;

const ThumbnailContainer = styled.div`
  width: 100%;
  aspect-ratio: 16/9;
  background: #f8f9fa;
  position: relative;
  overflow: hidden;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    cursor: pointer;
    position: absolute;
    top: 0;
    left: 0;
    
    &:hover {
      opacity: 0.8;
    }
  }
`;

const LoadingPlaceholder = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  position: absolute;
  top: 0;
  left: 0;
`;

interface ThumbnailState {
  loading: boolean;
  error: boolean;
  retryCount: number;
  retryTimer?: NodeJS.Timeout;
  loadedUrl?: string;  // 성공적으로 로드된 URL 저장
}

interface Props {
  videos: Video[];
  onTagClick?: (tag: { id: number; name: string }) => void;
}

export const VideoGrid: React.FC<Props> = ({ videos, onTagClick }) => {
  const [thumbnailStates, setThumbnailStates] = useState<{ [key: number]: ThumbnailState }>({});
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);

  // 컴포넌트 언마운트 시 타이머 정리
  useEffect(() => {
    return () => {
      Object.values(thumbnailStates).forEach(state => {
        if (state.retryTimer) {
          clearTimeout(state.retryTimer);
        }
      });
    };
  }, [thumbnailStates]);

  const handleImageLoad = (videoId: number, url: string) => {
    setThumbnailStates(prev => ({
      ...prev,
      [videoId]: { 
        loading: false, 
        error: false, 
        retryCount: 0,
        loadedUrl: url 
      }
    }));
  };

  const handleImageError = (videoId: number) => {
    setThumbnailStates(prev => {
      const currentState = prev[videoId] || { 
        loading: false, 
        error: false, 
        retryCount: 0 
      };
      const newRetryCount = currentState.retryCount + 1;
      
      if (currentState.retryTimer) {
        clearTimeout(currentState.retryTimer);
      }

      const retryTimer = setTimeout(() => {
        setThumbnailStates(latest => ({
          ...latest,
          [videoId]: {
            ...latest[videoId],
            loading: true,
            error: false,
            retryTimer: undefined
          }
        }));
      }, 3000);

      return {
        ...prev,
        [videoId]: {
          ...currentState,
          loading: false,
          error: true,
          retryCount: newRetryCount,
          retryTimer
        }
      };
    });
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleVideoClick = async (videoId: number) => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`/api/videos/play/${videoId}`, {
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

  const handlePrevVideo = () => {
    if (selectedVideo) {
      const currentIndex = videos.findIndex(v => v.id === selectedVideo.id);
      if (currentIndex > 0) {
        setSelectedVideo(videos[currentIndex - 1]);
      }
    }
  };

  const handleNextVideo = () => {
    if (selectedVideo) {
      const currentIndex = videos.findIndex(v => v.id === selectedVideo.id);
      if (currentIndex < videos.length - 1) {
        setSelectedVideo(videos[currentIndex + 1]);
      }
    }
  };

  return (
    <>
      <Grid>
        {videos.map(video => {
          const state = thumbnailStates[video.id] || { 
            loading: true, 
            error: false, 
            retryCount: 0 
          };
          
          const thumbnailUrl = `/api/videos/thumbnails/${video.thumbnail_id}`;
          const imageUrl = state.error ? 
            `${thumbnailUrl}?t=${Date.now()}` : 
            thumbnailUrl;
          
          return (
            <VideoCard key={video.id}>
              <ThumbnailContainer>
                {state.error ? (
                  <LoadingPlaceholder>
                    Loading...
                  </LoadingPlaceholder>
                ) : (
                  <img 
                    src={imageUrl}
                    alt={video.file_name}
                    onLoad={() => handleImageLoad(video.id, imageUrl)}
                    onError={() => handleImageError(video.id)}
                    onClick={() => handleVideoClick(video.id)}
                    title="Click to play video"
                    style={{ 
                      opacity: state.loadedUrl ? 1 : 0,
                      transition: 'opacity 0.3s'
                    }}
                  />
                )}
              </ThumbnailContainer>
              <div className="info">
                <h3 
                  title={video.file_name}
                  onClick={() => setSelectedVideo(video)}
                  style={{ cursor: 'pointer' }}
                >
                  {video.file_name}
                </h3>
                <div className="meta">
                  {formatDuration(video.duration)}
                </div>
                <div className="tags">
                  {video.tags.map(tag => (
                    <Tag 
                      key={tag.id}
                      onClick={(e) => {
                        e.stopPropagation();
                        onTagClick?.(tag);
                      }}
                    >
                      {tag.name}
                    </Tag>
                  ))}
                </div>
              </div>
            </VideoCard>
          );
        })}
      </Grid>
      
      {selectedVideo && (
        <VideoDetail 
          video={selectedVideo} 
          onClose={() => setSelectedVideo(null)}
          onPrevVideo={handlePrevVideo}
          onNextVideo={handleNextVideo}
          hasPrevVideo={videos.findIndex(v => v.id === selectedVideo.id) > 0}
          hasNextVideo={videos.findIndex(v => v.id === selectedVideo.id) < videos.length - 1}
        />
      )}
    </>
  );
}; 