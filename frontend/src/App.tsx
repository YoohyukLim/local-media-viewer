import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { VideoGrid } from './components/VideoGrid';
import { Pagination } from './components/Pagination';
import { TagList } from './components/TagList';
import { Video, PageResponse, Tag } from './types/video';

const Container = styled.div<{ $sidebarWidth: number }>`
  margin-left: ${props => props.$sidebarWidth}px;
  padding: 2rem;
`;

const MainContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Loading = styled.div`
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #666;
`;

const MainLoading = styled.div`
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #666;
`;

const SelectedTagsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const SelectedTags = styled.div`
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  flex: 1;
`;

const SelectedTag = styled.div`
  display: flex;
  align-items: center;
  background: #e9ecef;
  padding: 0.35rem 0.7rem;
  border-radius: 20px;
  font-size: 0.9rem;
  
  button {
    background: none;
    border: none;
    margin-left: 0.5rem;
    cursor: pointer;
    padding: 0;
    font-size: 1.1rem;
    color: #666;
    display: flex;
    align-items: center;
    
    &:hover {
      color: #333;
    }
  }
`;

const ClearButton = styled.button`
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.35rem 0.7rem;
  font-size: 0.9rem;
  color: #666;
  cursor: pointer;
  margin-left: 1rem;
  white-space: nowrap;
  
  &:hover {
    background: #f8f9fa;
    color: #333;
  }
`;

const ModeToggleButton = styled.button<{ mode: 'AND' | 'OR' }>`
  background: ${props => props.mode === 'AND' ? '#e7f5ff' : '#fff4e6'};
  border: 1px solid ${props => props.mode === 'AND' ? '#74c0fc' : '#ffd8a8'};
  border-radius: 4px;
  padding: 0.35rem 0.7rem;
  font-size: 0.9rem;
  color: ${props => props.mode === 'AND' ? '#1c7ed6' : '#fd7e14'};
  cursor: pointer;
  margin-left: 1rem;
  white-space: nowrap;
  font-weight: 500;
  
  &:hover {
    background: ${props => props.mode === 'AND' ? '#d0ebff' : '#ffe8cc'};
  }
`;

function App() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [mainLoading, setMainLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [sidebarWidth, setSidebarWidth] = useState(240);
  const [selectedTags, setSelectedTags] = useState<Tag[]>([]);
  const [searchMode, setSearchMode] = useState<'AND' | 'OR'>('AND');
  
  const handleTagClick = (tag: Tag) => {
    setPage(1);
    setSelectedTags(prev => {
      const isSelected = prev.some(t => t.id === tag.id);
      if (isSelected) {
        return prev.filter(t => t.id !== tag.id);
      }
      return [...prev, tag];
    });
  };

  const removeTag = (tagId: number) => {
    setPage(1);
    setSelectedTags(prev => prev.filter(tag => tag.id !== tagId));
  };

  const toggleSearchMode = () => {
    setPage(1);
    setSearchMode(prev => prev === 'AND' ? 'OR' : 'AND');
  };

  const fetchVideos = async (pageNum: number, tagIds?: number[]) => {
    try {
      setMainLoading(true);
      let url = `/api/videos/list?page=${pageNum}&size=25`;
      if (tagIds && tagIds.length > 0) {
        url += tagIds.map(id => `&tag_ids=${id}`).join('');
        url += `&tag_mode=${searchMode.toLowerCase()}`;
      }
      const response = await fetch(url);
      const data: PageResponse<Video> = await response.json();
      setVideos(data.items);
      setTotalPages(data.pages);
    } catch (error) {
      console.error('Failed to fetch videos:', error);
    } finally {
      setMainLoading(false);
    }
  };

  const fetchTags = async () => {
    try {
      const response = await fetch('/api/videos/tags');
      const data: Tag[] = await response.json();
      setTags(data);
    } catch (error) {
      console.error('Failed to fetch tags:', error);
    } finally {
      setInitialLoading(false);
    }
  };
  
  useEffect(() => {
    fetchVideos(page, selectedTags.map(tag => tag.id));
  }, [page, selectedTags, searchMode]);

  useEffect(() => {
    fetchTags();
  }, []);
  
  if (initialLoading) {
    return <Loading>Loading...</Loading>;
  }
  
  return (
    <>
      <TagList 
        tags={tags}
        onTagClick={handleTagClick}
        onWidthChange={setSidebarWidth}
      />
      <Container $sidebarWidth={sidebarWidth}>
        <MainContent>
          {selectedTags.length > 0 && (
            <SelectedTagsHeader>
              <SelectedTags>
                {selectedTags.map(tag => (
                  <SelectedTag key={tag.id}>
                    {tag.name}
                    <button onClick={() => removeTag(tag.id)}>×</button>
                  </SelectedTag>
                ))}
              </SelectedTags>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <ModeToggleButton 
                  mode={searchMode}
                  onClick={toggleSearchMode}
                >
                  {searchMode}
                </ModeToggleButton>
                <ClearButton onClick={() => setSelectedTags([])}>
                  초기화
                </ClearButton>
              </div>
            </SelectedTagsHeader>
          )}
          {mainLoading ? (
            <MainLoading>Loading...</MainLoading>
          ) : (
            <VideoGrid 
              videos={videos} 
              onTagClick={handleTagClick}
            />
          )}
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={setPage}
          />
        </MainContent>
      </Container>
    </>
  );
}

export default App;
