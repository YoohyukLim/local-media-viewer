import React, { useState } from 'react';
import styled from 'styled-components';
import { Video } from '../types/video';

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
    }
  }
`;

const Tag = styled.span`
  background: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
`;

const LoadingPlaceholder = styled.div`
  width: 100%;
  aspect-ratio: 16/9;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
`;

interface Props {
  videos: Video[];
}

export const VideoGrid: React.FC<Props> = ({ videos }) => {
  const [loadingStates, setLoadingStates] = useState<{[key: number]: boolean}>({});
  const [errorStates, setErrorStates] = useState<{[key: number]: boolean}>({});

  const handleImageLoad = (videoId: number) => {
    setLoadingStates(prev => ({ ...prev, [videoId]: false }));
    setErrorStates(prev => ({ ...prev, [videoId]: false }));
  };

  const handleImageError = (videoId: number) => {
    setLoadingStates(prev => ({ ...prev, [videoId]: false }));
    setErrorStates(prev => ({ ...prev, [videoId]: true }));
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleVideoClick = async (videoId: number) => {
    try {
      const response = await fetch(`/api/videos/play/${videoId}`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to play video');
      }
    } catch (error) {
      console.error('Error playing video:', error);
    }
  };

  return (
    <Grid>
      {videos.map(video => (
        <VideoCard key={video.id}>
          {errorStates[video.id] ? (
            <LoadingPlaceholder>
              Loading...
            </LoadingPlaceholder>
          ) : (
            <img 
              src={`/api/videos/thumbnails/${video.thumbnail_id}`}
              alt={video.file_name}
              onLoad={() => handleImageLoad(video.id)}
              onError={() => handleImageError(video.id)}
              onClick={() => handleVideoClick(video.id)}
              title="Click to play video"
            />
          )}
          <div className="info">
            <h3 title={video.file_name}>{video.file_name}</h3>
            <div className="meta">
              {formatDuration(video.duration)}
            </div>
            <div className="tags">
              {video.tags.map(tag => (
                <Tag key={tag.id}>{tag.name}</Tag>
              ))}
            </div>
          </div>
        </VideoCard>
      ))}
    </Grid>
  );
}; 