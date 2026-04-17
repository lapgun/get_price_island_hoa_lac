import { Layout, Typography } from 'antd'

const { Header: AntHeader } = Layout
const { Title, Text } = Typography

interface AppHeaderProps {
  scrapedAt: string | null
  totalRecords: number
}

export default function AppHeader({ scrapedAt, totalRecords }: AppHeaderProps) {
  return (
    <AntHeader className="apple-nav">
      <div className="apple-nav-brand">
        <Title className="apple-nav-title" level={5} style={{ margin: 0 }}>
          Giá đất Hoà Lạc – Thạch Thất – Quốc Oai
        </Title>
        <Text className="apple-nav-meta">
          {scrapedAt
            ? `Cập nhật: ${new Date(scrapedAt).toLocaleString('vi-VN')}`
            : 'Chưa có dữ liệu. Nhấn "Đồng bộ" để bắt đầu.'}
        </Text>
      </div>

      <Text className="apple-nav-meta">{totalRecords} bản ghi</Text>
    </AntHeader>
  )
}
