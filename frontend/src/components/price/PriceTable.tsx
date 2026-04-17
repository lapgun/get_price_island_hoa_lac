import { useMemo } from 'react'
import { Card, Table, List } from 'antd'
import type { PriceItem } from '../../types'
import { getPriceColumns } from './PriceColumns'
import PriceCard from './PriceCard'
import { useIsMobile } from '../../hooks/useIsMobile'

interface PriceTableProps {
  data: PriceItem[]
  loading: boolean
}

export default function PriceTable({ data, loading }: PriceTableProps) {
  const columns = useMemo(() => getPriceColumns(), [])
  const isMobile = useIsMobile()

  if (isMobile) {
    return (
      <List
        dataSource={data}
        loading={loading}
        className="apple-mobile-list"
        pagination={{ pageSize: 10, simple: true, style: { textAlign: 'center', padding: '12px 0' } }}
        locale={{ emptyText: 'Nhấn "Đồng bộ" để bắt đầu' }}
        renderItem={(item: PriceItem, index: number) => (
          <PriceCard item={item} index={index} />
        )}
      />
    )
  }

  return (
    <Card
      className="apple-panel apple-table-card"
      size="small"
      title={<span>Bảng dữ liệu</span>}
      extra={<span className="apple-table-count">{data.length} bản ghi</span>}
      styles={{ body: { padding: 0 } }}
    >
      <Table<PriceItem>
        columns={columns}
        dataSource={data}
        rowKey={(r: PriceItem) => `${r.post_id}-${r.source}`}
        loading={loading}
        size="small"
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          pageSizeOptions: [10, 20, 50, 100],
          showTotal: (total, range) => `${range[0]}-${range[1]} / ${total}`,
        }}
        scroll={{ x: 1080 }}
        sticky
        rowClassName={(_, index) => (index % 2 === 0 ? 'apple-table-row-even' : 'apple-table-row-odd')}
        locale={{ emptyText: 'Nhấn "Đồng bộ dữ liệu" để bắt đầu' }}
      />
    </Card>
  )
}
