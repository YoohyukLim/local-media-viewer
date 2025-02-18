import React from 'react';
import styled from 'styled-components';

const Nav = styled.nav`
  display: flex;
  justify-content: center;
  padding: 1rem;
  gap: 0.5rem;
`;

const PageButton = styled.button<{ $active?: boolean }>`
  padding: 0.5rem 1rem;
  margin: 0 0.25rem;
  border: 1px solid ${props => props.$active ? '#339af0' : '#dee2e6'};
  border-radius: 4px;
  background: ${props => props.$active ? '#339af0' : 'white'};
  color: ${props => props.$active ? 'white' : '#495057'};
  cursor: pointer;
  
  &:hover {
    background: ${props => props.$active ? '#1c7ed6' : '#f8f9fa'};
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }
`;

interface Props {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export const Pagination: React.FC<Props> = ({
  currentPage,
  totalPages,
  onPageChange,
}) => {
  const JUMP_SIZE = 5; // 한 번에 이동할 페이지 수
  
  // 디버깅을 위한 로그 추가
  console.log('Pagination props:', { currentPage, totalPages });
  
  // 표시할 페이지 번호 계산
  const getPageNumbers = (): number[] => {
    const pageNumbers: number[] = [];
    const maxVisible = 5;  // 최대 표시 개수
    
    if (totalPages <= 0) return pageNumbers;
    
    let start = Math.max(1, currentPage - 2);
    let end = Math.min(totalPages, start + maxVisible - 1);
    
    // end가 최대값에 도달하지 않은 경우 start를 조정
    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }
    
    for (let i = start; i <= end; i++) {
      pageNumbers.push(i);
    }
    
    console.log('Page numbers:', pageNumbers);
    return pageNumbers;
  };

  // 이전/다음 5페이지 이동
  const handleJumpPrev = () => {
    const newPage = Math.max(1, currentPage - JUMP_SIZE);
    onPageChange(newPage);
  };

  const handleJumpNext = () => {
    const newPage = Math.min(totalPages, currentPage + JUMP_SIZE);
    onPageChange(newPage);
  };

  // totalPages가 0이면 페이지네이션을 표시하지 않음
  if (totalPages <= 0) return null;

  return (
    <Nav>
      <PageButton 
        onClick={() => onPageChange(1)}
        disabled={currentPage === 1}
      >
        {'<<'}
      </PageButton>
      <PageButton 
        onClick={handleJumpPrev}
        disabled={currentPage === 1}
      >
        {'-5'}
      </PageButton>
      <PageButton 
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        {'<'}
      </PageButton>
      
      {getPageNumbers().map(pageNum => (
        <PageButton
          key={pageNum}
          $active={pageNum === currentPage}
          onClick={() => onPageChange(pageNum)}
        >
          {pageNum}
        </PageButton>
      ))}
      
      <PageButton 
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        {'>'}
      </PageButton>
      <PageButton 
        onClick={handleJumpNext}
        disabled={currentPage === totalPages}
      >
        {'+5'}
      </PageButton>
      <PageButton 
        onClick={() => onPageChange(totalPages)}
        disabled={currentPage === totalPages}
      >
        {'>>'}
      </PageButton>
    </Nav>
  );
}; 