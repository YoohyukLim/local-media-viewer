import React, { useState, useCallback, useEffect } from 'react';
import styled from 'styled-components';
import { Tag } from '../types/video';

const MIN_WIDTH = 200;
const MAX_WIDTH = 400;

const Sidebar = styled.div<{ width: number }>`
  width: ${props => props.width}px;
  padding: 1rem 0;
  background: white;
  border-right: 1px solid #ddd;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  overflow-y: auto;
  
  /* Firefox */
  scrollbar-width: none;
  
  /* Chrome, Safari, Edge */
  &::-webkit-scrollbar {
    display: none;
  }
  
  /* 스크롤바 완전히 숨기기 */
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
`;

const Resizer = styled.div`
  width: 8px;
  height: 100vh;
  position: absolute;
  right: -4px;
  top: 0;
  cursor: ew-resize;
  
  &::after {
    content: '';
    position: absolute;
    left: 3px;
    width: 2px;
    height: 100%;
    background: transparent;
    transition: background-color 0.2s;
  }
  
  &:hover::after {
    background: #999;
  }
  
  &:active::after {
    background: #666;
  }
`;

const Title = styled.h2`
  font-size: 1.2rem;
  margin: 0 1rem 1rem 1rem;
  color: #333;
`;

const TagsContainer = styled.div`
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
`;

const SearchContainer = styled.div`
  position: relative;
  width: calc(100% - 1rem);
  margin: 0.2rem 0;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 0.35rem 0.5rem;
  padding-right: 2rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  box-sizing: border-box;
  
  &:focus {
    outline: none;
    border-color: #999;
  }
  
  &::placeholder {
    color: #999;
  }
`;

const ClearButton = styled.button`
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  padding: 0;
  width: 16px;
  height: 16px;
  cursor: pointer;
  opacity: 0.5;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    opacity: 0.8;
  }
  
  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 12px;
    height: 2px;
    background: #666;
    border-radius: 1px;
  }
  
  &::before {
    transform: rotate(45deg);
  }
  
  &::after {
    transform: rotate(-45deg);
  }
`;

const TagItem = styled.div`
  width: calc(100% - 1rem);
  padding: 0.35rem 0.5rem;
  margin: 0.2rem 0;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.9rem;
  box-sizing: border-box;
  
  /* 긴 텍스트 처리 */
  word-break: break-all;
  white-space: normal;
  overflow-wrap: break-word;
  
  &:hover {
    filter: brightness(0.95);
  }
`;

// 파스텔톤 색상 배열
const pastelColors = [
  '#FFE5E5', // 연한 분홍
  '#E5FFE5', // 연한 초록
  '#E5E5FF', // 연한 파랑
  '#FFE5FF', // 연한 보라
  '#FFFFE5', // 연한 노랑
  '#E5FFFF', // 연한 하늘
];

interface Props {
  tags: Tag[];
  onTagClick?: (tag: Tag) => void;
  onWidthChange?: (width: number) => void;
}

export const TagList: React.FC<Props> = ({ tags, onTagClick, onWidthChange }) => {
  const [width, setWidth] = useState(240);
  const [isResizing, setIsResizing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const startResizing = useCallback((e: React.MouseEvent) => {
    setIsResizing(true);
    e.preventDefault();
  }, []);

  const stopResizing = useCallback(() => {
    setIsResizing(false);
  }, []);

  const resize = useCallback((e: MouseEvent) => {
    if (isResizing) {
      const newWidth = Math.min(Math.max(e.clientX, MIN_WIDTH), MAX_WIDTH);
      setWidth(newWidth);
      onWidthChange?.(newWidth);
    }
  }, [isResizing, onWidthChange]);

  useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', resize);
      window.addEventListener('mouseup', stopResizing);
    }

    return () => {
      window.removeEventListener('mousemove', resize);
      window.removeEventListener('mouseup', stopResizing);
    };
  }, [isResizing, resize, stopResizing]);

  const filteredTags = tags.filter(tag => 
    tag.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Sidebar width={width}>
      <Title>태그 목록</Title>
      <TagsContainer>
        <SearchContainer>
          <SearchInput
            type="text"
            placeholder="태그 검색..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <ClearButton
              onClick={() => setSearchTerm('')}
              title="검색어 지우기"
            />
          )}
        </SearchContainer>
        {filteredTags.map((tag, index) => (
          <TagItem 
            key={tag.id}
            onClick={() => onTagClick?.(tag)}
            style={{ background: pastelColors[index % pastelColors.length] }}
          >
            {tag.name}
          </TagItem>
        ))}
      </TagsContainer>
      <Resizer onMouseDown={startResizing} />
    </Sidebar>
  );
};