import { Layout } from 'antd'
import { usePriceData } from '../hooks/usePriceData'
import { useFilters } from '../hooks/useFilters'
import AppHeader from '../components/layout/AppHeader'
import FilterBar from '../components/price/FilterBar'
import StatsBar from '../components/price/StatsBar'
import PriceTable from '../components/price/PriceTable'
import GroupsPanel from '../components/price/GroupsPanel'

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

  const {
    filteredData,
    minPrice, setMinPrice,
    maxPrice, setMaxPrice,
    filterType, setFilterType,
    searchText, setSearchText,
    filterPrice, setFilterPrice,
    filterPhone, setFilterPhone,
  } = useFilters(data)

  const heroUpdateText = scrapedAt
    ? `Cập nhật ${new Date(scrapedAt).toLocaleString('vi-VN')}`
    : 'Chưa có dữ liệu mới'

  return (
    <>
      {contextHolder}
      <Layout className="apple-shell">
        <AppHeader scrapedAt={scrapedAt} totalRecords={data.length} />

        <Content className="apple-content">
          <section className="apple-hero">
            <div className="apple-container">
              <p className="apple-eyebrow">Price Intelligence</p>
              <h1 className="apple-hero-title">Giá đất Hoà Lạc</h1>
              <p className="apple-hero-subtitle">
                Theo dõi biến động bài đăng mua bán đất tại Thạch Thất và Quốc Oai trong một giao diện tinh gọn,
                tập trung dữ liệu và tối ưu cho quyết định nhanh.
              </p>
              <div className="apple-hero-meta">
                <span>{heroUpdateText}</span>
                <span>{filteredData.length} bản ghi sau lọc</span>
                <span>{rawCount} bản ghi trước lọc</span>
              </div>
            </div>
          </section>

          <section className="apple-surface">
            <div className="apple-container apple-stack">
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
                onScrape={doScrape}
              />

              <GroupsPanel />

              <StatsBar
                total={filteredData.length}
                rawCount={rawCount}
                withPhone={stats.withPhone}
                byType={stats.byType}
              />

              <PriceTable
                data={filteredData}
                loading={loading || loadingData}
              />
            </div>
          </section>
        </Content>
      </Layout>
    </>
  )
}
