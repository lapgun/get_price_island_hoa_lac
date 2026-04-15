import type { ScrapeResponse } from '../types'

export async function scrapeData(): Promise<ScrapeResponse> {
  const res = await fetch('/api/scrape', { method: 'POST' })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export interface ScrapeStartResponse {
  status: string
  job_id: string
}

export interface ScrapeJobStatus {
  id: string
  status: 'queued' | 'running' | 'done' | 'failed'
  created_at: string
  started_at: string | null
  finished_at: string | null
  result: {
    count: number
    raw_count: number
    new_count: number
    skipped: number
  } | null
  error: string | null
}

export async function startScrapeJob(): Promise<ScrapeStartResponse> {
  const res = await fetch('/api/scrape/start', { method: 'POST' })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function getScrapeJobStatus(jobId: string): Promise<ScrapeJobStatus> {
  const res = await fetch(`/api/scrape/status/${jobId}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
