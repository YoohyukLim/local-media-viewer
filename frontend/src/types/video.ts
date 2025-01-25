export interface Video {
  id: number;
  file_path: string;
  file_name: string;
  thumbnail_id: string;
  duration: number;
  category: string | null;
  created_at: string;
  updated_at: string;
  tags: Tag[];
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