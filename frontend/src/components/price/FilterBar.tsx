import type { ChangeEvent } from 'react'
import { Card, Space, Typography, InputNumber, Select, Input, Button, Switch } from 'antd'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons'
import { POST_TYPE_OPTIONS } from '../../constants/postType'

const { Text } = Typography

interface FilterBarProps {
  minPrice: number
  maxPrice: number
  filterType: string | undefined
  searchText: string
  loading: boolean
  filterPrice: boolean
  filterPhone: boolean
  onMinPriceChange: (v: number) => void
  onMaxPriceChange: (v: number) => void
  onFilterTypeChange: (v: string | undefined) => void
  onSearchTextChange: (v: string) => void
  onFilterPriceChange: (v: boolean) => void
  onFilterPhoneChange: (v: boolean) => void
  onScrape: () => void
}

export default function FilterBar({
  minPrice,
  maxPrice,
  filterType,
  searchText,
  loading,
  filterPrice,
  filterPhone,
  onMinPriceChange,
  onMaxPriceChange,
  onFilterTypeChange,
  onSearchTextChange,
  onFilterPriceChange,
  onFilterPhoneChange,
  onScrape,
}: FilterBarProps) {
  return (
    <Card className="apple-panel" size="small">
      <div className="apple-filter-bar">
        <div className="apple-filter-toggles">
          <Space size={8}>
            <Switch size="small" checked={filterPrice} onChange={onFilterPriceChange} />
            <Text className="apple-filter-label">Lọc giá</Text>
          </Space>
          <Space size={8}>
            <Switch size="small" checked={filterPhone} onChange={onFilterPhoneChange} />
            <Text className="apple-filter-label">Có SĐT</Text>
          </Space>
        </div>

        {filterPrice && (
          <div className="apple-filter-price-range">
            <div className="apple-filter-price-field">
              <Text className="apple-filter-label">Từ (tỷ)</Text>
              <InputNumber
                value={minPrice}
                onChange={(v) => onMinPriceChange(v ?? 0)}
                step={0.1}
                min={0}
                className="apple-control-input apple-filter-number"
              />
            </div>
            <div className="apple-filter-price-field">
              <Text className="apple-filter-label">đến (tỷ)</Text>
              <InputNumber
                value={maxPrice}
                onChange={(v) => onMaxPriceChange(v ?? 10)}
                step={0.1}
                min={0}
                className="apple-control-input apple-filter-number"
              />
            </div>
          </div>
        )}

        <Select
          placeholder="Loại bài"
          allowClear
          value={filterType}
          onChange={onFilterTypeChange}
          options={POST_TYPE_OPTIONS}
          className="apple-control-input apple-filter-select"
        />

        <Input
          placeholder="Tìm SĐT, tên, vị trí..."
          prefix={<SearchOutlined />}
          allowClear
          value={searchText}
          onChange={(e: ChangeEvent<HTMLInputElement>) => onSearchTextChange(e.target.value)}
          className="apple-control-input apple-filter-search"
        />

        <Button
          type="primary"
          icon={<ReloadOutlined />}
          loading={loading}
          onClick={onScrape}
          className="apple-primary-btn apple-filter-btn"
        >
          Đồng bộ dữ liệu
        </Button>
      </div>
    </Card>
  )
}
