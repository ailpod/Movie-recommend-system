/**
 * 电影相关类型定义
 */

export interface Movie {
  id: number
  title: string
  description?: string
  poster_path?: string
  avg_rate?: number
  genres?: string | string[]
  release_year?: number
  director?: string
  actors?: string[]
  vote?: number
  backdrop_path?: string
  runtime?: number
  budget?: number
  revenue?: number
  status?: string
  tagline?: string
  homepage?: string
  imdb_id?: string
  original_language?: string
  original_title?: string
  overview?: string
  popularity?: number
  production_companies?: string[]
  production_countries?: string[]
  spoken_languages?: string[]
  video?: boolean
  vote_average?: number
  vote_count?: number
}

export interface MovieSearchResult {
  movies: Movie[]
  total: number
  page: number
  per_page: number
}

export interface Genre {
  id: number
  name: string
}

export interface MovieListResponse {
  results: Movie[]
  total_results: number
  total_pages: number
  page: number
}
