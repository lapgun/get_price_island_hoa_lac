import type { DataResponse, StatsResponse } from '../types'

export async function fetchData(session?: string): Promise<DataResponse> {
  const params = new URLSearchParams()
  if (session) params.set('session', session)

  const res = await fetch(`/api/data?${params}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function fetchStats(): Promise<StatsResponse> {
  const res = await fetch('/api/stats')
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
