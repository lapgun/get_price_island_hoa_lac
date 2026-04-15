import React from 'react'
import { Card, Row, Col, Space, Typography, InputNumber, Select, Input, Button, Switch } from 'antd'
import {
  SearchOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { POST_TYPE_OPTIONS } from '../../constants/postType'
import { useIsMobile } from '../../hooks/useIsMobile'

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
  const isMobile = useIsMobile()

  if (isMobile) {
    return (
      <Card size="small" style={{ marginBottom: 8, borderRadius: 10 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {/* Toggle switches */}
          <Row gutter={8}>
            <Col span={12}>
              <Space>
                <Switch size="small" checked={filterPrice} onChange={onFilterPriceChange} />
                <Text style={{ fontSize: 12 }}>Lọc theo giá</Text>
              </Space>
            </Col>
            <Col span={12}>
              <Space>
                <Switch size="small" checked={filterPhone} onChange={onFilterPhoneChange} />
                <Text style={{ fontSize: 12 }}>Có SĐT</Text>
              </Space>
            </Col>
          </Row>

          {/* Price range row */}
          {filterPrice && (
          <Row gutter={8}>
            <Col span={12}>
              <Text strong style={{ fontSize: 11 }}>Giá từ (tỷ)</Text>
              <InputNumber
                value={minPrice}
                onChange={(v: number | null) => onMinPriceChange(v ?? 0)}
                step={0.1}
                min={0}
                style={{ width: '100%' }}
                size="middle"
              />
            </Col>
            <Col span={12}>
              <Text strong style={{ fontSize: 11 }}>đến (tỷ)</Text>
              <InputNumber
                value={maxPrice}
                onChange={(v: number | null) => onMaxPriceChange(v ?? 10)}
                step={0.1}
                min={0}
                style={{ width: '100%' }}
                size="middle"
              />
            </Col>
          </Row>
          )}

          {/* Filter type + Search */}
          <Select
            placeholder="Loại bài"
            allowClear
            style={{ width: '100%' }}
            value={filterType}
            onChange={(v: string | undefined) => onFilterTypeChange(v)}
            options={POST_TYPE_OPTIONS}
            size="middle"
          />
          <Input
            placeholder="Tìm SĐT, tên, vị trí..."
            prefix={<SearchOutlined />}
            allowClear
            style={{ width: '100%' }}
            value={searchText}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => onSearchTextChange(e.target.value)}
            size="middle"
          />

          {/* Buttons */}
          <Button
            type="primary"
            icon={<ReloadOutlined />}
            loading={loading}
            onClick={onScrape}
            block
          >
            Đồng bộ dữ liệu
          </Button>
        </div>
      </Card>
    )
  }

  return (
    <Card size="small" style={{ marginBottom: 12 }}>
      <Space wrap size="middle">
        <Space>
          <Switch size="small" checked={filterPrice} onChange={onFilterPriceChange} />
          <Text style={{ fontSize: 12 }}>Lọc giá</Text>
        </Space>
        {filterPrice && (
          <>
            <Space>
              <Text strong style={{ fontSize: 12 }}>Từ (tỷ):</Text>
              <InputNumber
                value={minPrice}
                onChange={(v: number | null) => onMinPriceChange(v ?? 0)}
                step={0.1}
                min={0}
                style={{ width: 90 }}
              />
            </Space>
            <Space>
              <Text strong style={{ fontSize: 12 }}>đến:</Text>
              <InputNumber
                value={maxPrice}
                onChange={(v: number | null) => onMaxPriceChange(v ?? 10)}
                step={0.1}
                min={0}
                style={{ width: 90 }}
              />
            </Space>
          </>
        )}
        <Space>
          <Switch size="small" checked={filterPhone} onChange={onFilterPhoneChange} />
          <Text style={{ fontSize: 12 }}>Có SĐT</Text>
        </Space>
        <Select
          placeholder="Loại bài"
          allowClear
          style={{ minWidth: 150 }}
          value={filterType}
          onChange={(v: string | undefined) => onFilterTypeChange(v)}
          options={POST_TYPE_OPTIONS}
        />
        <Input
          placeholder="Tìm SĐT, tên, vị trí..."
          prefix={<SearchOutlined />}
          allowClear
          style={{ width: 220 }}
          value={searchText}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => onSearchTextChange(e.target.value)}
        />
        <Button
          type="primary"
          icon={<ReloadOutlined />}
          loading={loading}
          onClick={onScrape}
        >
          Đồng bộ dữ liệu
        </Button>
      </Space>
    </Card>
  )
}
