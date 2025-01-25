import React from 'react';
import styled from 'styled-components';
import { Tag } from '../types/video';

const Sidebar = styled.div`
  width: 240px;
  padding: 1rem;
  background: white;
  border-right: 1px solid #ddd;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  overflow-y: auto;
  
  /* Firefox */
  scrollbar-width: none;
  &:hover:active {
    scrollbar-width: thin;
    scrollbar-color: #999 transparent;
  }
  
  /* Chrome, Safari, Edge */
  &::-webkit-scrollbar {
    width: 0;
  }
  
  &:hover:active::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-thumb {
    background-color: #999;
    border-radius: 3px;
    
    &:hover {
      background-color: #666;
    }
  }
`;

const Title = styled.h2`
  font-size: 1.2rem;
  margin: 0 0 1rem 0;
  color: #333;
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

const TagItem = styled.div<{ colorIndex: number }>`
  padding: 0.35rem 0.5rem;
  margin: 0.2rem 0;
  background: ${props => pastelColors[props.colorIndex]};
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.9rem;
  
  /* 긴 텍스트 처리 */
  word-break: break-all;
  white-space: normal;
  overflow-wrap: break-word;
  
  &:hover {
    filter: brightness(0.95);
  }
`;

interface Props {
  tags: Tag[];
  onTagClick?: (tag: Tag) => void;
}

export const TagList: React.FC<Props> = ({ tags, onTagClick }) => {
  return (
    <Sidebar>
      <Title>태그 목록</Title>
      {tags.map((tag, index) => (
        <TagItem 
          key={tag.id}
          colorIndex={index % pastelColors.length}
          onClick={() => onTagClick?.(tag)}
        >
          {tag.name}
        </TagItem>
      ))}
    </Sidebar>
  );
};