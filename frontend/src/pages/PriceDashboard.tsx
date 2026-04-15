import { useState, useMemo } from 'react'
import { Layout } from 'antd'
import { usePriceData } from '../hooks/usePriceData'
import { useIsMobile } from '../hooks/useIsMobile'
import AppHeader from '../components/layout/AppHeader'
import FilterBar from '../components/price/FilterBar'
import StatsBar from '../components/price/StatsBar'
import PriceTable from '../components/price/PriceTable'
import GroupsPanel from '../components/price/GroupsPanel'
import type { PriceItem } from '../types'

const { Content } = Layout

export default function PriceDashboard() {
  const {
    data,
    rawCount,
    scrapedAt,
    loading,
    loadingData,
    stats,
    contextHolder,
    doScrape,
  } = usePriceData()

  const isMobile = useIsMobile()
  const [minPrice, setMinPrice] = useState(1.0)
  const [maxPrice, setMaxPrice] = useState(2.0)
  const [filterType, setFilterType] = useState<string | undefined>(undefined)
  const [searchText, setSearchText] = useState('')

  const [filterPrice, setFilterPrice] = useState(false)
  const [filterPhone, setFilterPhone] = useState(false)

  const filteredData = useMemo(() => {
    let result: PriceItem[] = data
    if (filterType) {
      result = result.filter((d) => d.post_type === filterType)
    }
    if (filterPrice) {
      result = result.filter((d) => {
        const est = d.estimated_price_ty
        if (est == null) return false
        return est >= minPrice && est <= maxPrice
      })
    }
    if (filterPhone) {
      result = result.filter((d) => !!d.phone)
    }
    if (searchText) {
      const s = searchText.toLowerCase()
      result = result.filter(
        (d) =>
          (d.phone || '').toLowerCase().includes(s) ||
          (d.author || '').toLowerCase().includes(s) ||
          (d.location || '').toLowerCase().includes(s) ||
          (d.text_snippet || '').toLowerCase().includes(s) ||
          (d.group_name || '').toLowerCase().includes(s),
      )
    }
    return result
  }, [data, filterType, filterPrice, filterPhone, minPrice, maxPrice, searchText])

  return (
    <>
      {contextHolder}
      <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
        <AppHeader scrapedAt={scrapedAt} totalRecords={data.length} />

        <Content style={{ padding: isMobile ? '8px' : '16px 20px' }}>
          <FilterBar
            minPrice={minPrice}
            maxPrice={maxPrice}
            filterType={filterType}
            searchText={searchText}
            loading={loading}
            onMinPriceChange={setMinPrice}
            onMaxPriceChange={setMaxPrice}
            onFilterTypeChange={setFilterType}
            onSearchTextChange={setSearchText}
            filterPrice={filterPrice}
            filterPhone={filterPhone}
            onFilterPriceChange={setFilterPrice}
            onFilterPhoneChange={setFilterPhone}
            onScrape={() => doScrape()}
          />

          <GroupsPanel />

          <StatsBar
            total={data.length}
            rawCount={rawCount}
            withPhone={stats.withPhone}
            byType={stats.byType}
          />

          <PriceTable
            data={filteredData}
            loading={loading || loadingData}
          />
        </Content>
      </Layout>
    </>
  )
}
