import { useState, useMemo, useEffect, useCallback } from 'react'
import { message } from 'antd'
import type { PriceItem, StatsResponse } from '../types'
import { fetchData, fetchStats } from '../api'
import { getScrapeJobStatus, startScrapeJob } from '../api/scrape'

export function usePriceData() {
  const [data, setData] = useState<PriceItem[]>([])
  const [rawCount, setRawCount] = useState(0)
  const [scrapedAt, setScrapedAt] = useState<string | null>(null)
  const [sessions, setSessions] = useState<string[]>([])
  const [selectedSession, setSelectedSession] = useState<string | undefined>(undefined)
  const [loading, setLoading] = useState(false)
  const [loadingData, setLoadingData] = useState(false)
  const [messageApi, contextHolder] = message.useMessage()

  const loadFromDB = useCallback(async (session?: string) => {
    setLoadingData(true)
    try {
      const json = await fetchData(session)
      setData(json.data || [])
      setScrapedAt(json.scraped_at)
    } catch (e: unknown) {
      messageApi.error(`Lỗi tải dữ liệu: ${e instanceof Error ? e.message : 'Unknown'}`)
    } finally {
      setLoadingData(false)
    }
  }, [messageApi])

  const loadStats = useCallback(async () => {
    try {
      const json: StatsResponse = await fetchStats()
      setSessions(json.sessions || [])
      setRawCount(json.total)
      if (json.scraped_at) setScrapedAt(json.scraped_at)
    } catch {
      // ignore
    }
  }, [])

  useEffect(() => {
    loadStats()
    loadFromDB()
  }, [loadStats, loadFromDB])

  const doScrape = useCallback(async () => {
    setLoading(true)
    try {
      const start = await startScrapeJob()
      const jobId = start.job_id

      messageApi.info('Đang đồng bộ nền... Bạn có thể tiếp tục dùng hệ thống.')

      const maxPolls = 240 // ~20 phút (mỗi 5s)
      for (let i = 0; i < maxPolls; i += 1) {
        await new Promise((resolve) => setTimeout(resolve, 5000))
        const st = await getScrapeJobStatus(jobId)

        if (st.status === 'done') {
          setSelectedSession(undefined)
          await loadFromDB()
          await loadStats()
          const result = st.result
          messageApi.success(
            `Đồng bộ xong: ${result?.new_count ?? 0} mới, ${result?.skipped ?? 0} trùng bỏ qua. Tổng DB: ${result?.count ?? 0} bản ghi.`,
          )
          return
        }

        if (st.status === 'failed') {
          throw new Error(st.error || 'Job scrape thất bại')
        }
      }

      throw new Error('Job scrape chạy quá lâu, vui lòng kiểm tra lại sau.')
    } catch (e: unknown) {
      messageApi.error(`Lỗi: ${e instanceof Error ? e.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }, [messageApi, loadStats, loadFromDB])

  const onSessionChange = useCallback((session: string | undefined) => {
    setSelectedSession(session)
    loadFromDB(session)
  }, [loadFromDB])

  const stats = useMemo(() => {
    const byType: Record<string, number> = {}
    let withPhone = 0
    data.forEach((d) => {
      byType[d.post_type] = (byType[d.post_type] || 0) + 1
      if (d.phone) withPhone++
    })
    return { byType, withPhone }
  }, [data])

  return {
    data,
    rawCount,
    scrapedAt,
    sessions,
    selectedSession,
    loading,
    loadingData,
    stats,
    contextHolder,
    doScrape,
    onSessionChange,
  }
}
