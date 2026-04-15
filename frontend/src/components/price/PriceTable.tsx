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
        pagination={{ pageSize: 10, simple: true, style: { textAlign: 'center', padding: '12px 0' } }}
        locale={{ emptyText: 'Nhấn "Đồng bộ" để bắt đầu' }}
        renderItem={(item: PriceItem, index: number) => (
          <PriceCard item={item} index={index} />
        )}
      />
    )
  }

  return (
    <Card size="small" bodyStyle={{ padding: 0 }}>
      <Table<PriceItem>
        columns={columns}
        dataSource={data}
        rowKey={(r: PriceItem, i?: number) => `${r.post_id}-${r.source}-${i}`}
        loading={loading}
        size="small"
        pagination={{ pageSize: 20, showSizeChanger: true, pageSizeOptions: [10, 20, 50, 100] }}
        scroll={{ x: 1200 }}
        locale={{ emptyText: 'Nhấn "Đồng bộ dữ liệu" để bắt đầu' }}
      />
    </Card>
  )
}
