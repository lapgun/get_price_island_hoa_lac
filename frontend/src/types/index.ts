export interface PriceItem {
  id?: number
  post_id: string
  group_name: string
  post_type: string
  source: string
  link: string
  author: string
  phone: string
  text_snippet: string
  price_ty: string
  price_tr_m2: string
  price_trieu: string
  area: string
  location: string
  ai_summary: string
  estimated_price_ty: number | null
  scrape_session?: string | null
  created_at?: string | null
}

export interface ScrapeResponse {
  status: string
  count: number
  raw_count: number
  new_count: number
  skipped: number
  scraped_at: string | null
  data: PriceItem[]
}

export interface DataResponse {
  scraped_at: string | null
  count: number
  data: PriceItem[]
}

export interface StatsResponse {
  scraped_at: string | null
  total: number
  raw_count: number
  by_type: Record<string, number>
  by_location: Record<string, number>
  sessions: string[]
}
