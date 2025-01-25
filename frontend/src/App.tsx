import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { VideoGrid } from './components/VideoGrid';
import { Pagination } from './components/Pagination';
import { TagList } from './components/TagList';
import { Video, PageResponse, Tag } from './types/video';

const Container = styled.div`
  margin-left: 240px;  // 200px -> 240px로 증가
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

function App() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  
  const fetchVideos = async (pageNum: number) => {
    try {
      setLoading(true);
      const response = await fetch(
        `/api/videos/list?page=${pageNum}&size=25`
      );
      const data: PageResponse<Video> = await response.json();
      setVideos(data.items);
      setTotalPages(data.pages);
    } catch (error) {
      console.error('Failed to fetch videos:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTags = async () => {
    try {
      const response = await fetch('/api/videos/tags');
      const data: Tag[] = await response.json();
      setTags(data);
    } catch (error) {
      console.error('Failed to fetch tags:', error);
    }
  };
  
  useEffect(() => {
    fetchVideos(page);
  }, [page]);

  useEffect(() => {
    fetchTags();
  }, []);
  
  if (loading) {
    return <Loading>Loading...</Loading>;
  }
  
  return (
    <>
      <TagList tags={tags} />
      <Container>
        <MainContent>
          <VideoGrid videos={videos} />
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
