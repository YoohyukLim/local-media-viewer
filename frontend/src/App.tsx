import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { VideoGrid } from './components/VideoGrid';
import { Pagination } from './components/Pagination';
import { Video, PageResponse } from './types/video';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const Loading = styled.div`
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #666;
`;

function App() {
  const [videos, setVideos] = useState<Video[]>([]);
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
      console.log('API Response:', data);
      
      setVideos(data.items);
      setTotalPages(data.pages);
    } catch (error) {
      console.error('Failed to fetch videos:', error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchVideos(page);
  }, [page]);
  
  if (loading) {
    return <Loading>Loading...</Loading>;
  }
  
  return (
    <Container>
      <VideoGrid videos={videos} />
      <Pagination
        currentPage={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />
    </Container>
  );
}

export default App;
