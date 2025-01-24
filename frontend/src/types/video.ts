export interface Video {
  id: number;
  file_path: string;
  file_name: string;
  thumbnail_id: string;
  duration: number;
  tags: Tag[];
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: number;
  name: string;
}

export interface PageResponse<T> {
  items: T[];
  total: number;
  pages: number;
  page: number;
  size: number;
} 