import { Layout, Typography } from 'antd'
import { useIsMobile } from '../../hooks/useIsMobile'

const { Header: AntHeader } = Layout
const { Title, Text } = Typography

interface AppHeaderProps {
  scrapedAt: string | null
  totalRecords: number
}

export default function AppHeader({ scrapedAt, totalRecords }: AppHeaderProps) {
  const isMobile = useIsMobile()

  return (
    <AntHeader
      style={{
        background: 'linear-gradient(135deg, #1677ff, #0958d9)',
        padding: isMobile ? '0 12px' : '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: 'auto',
        minHeight: isMobile ? 48 : 64,
      }}
    >
      <div style={{ padding: isMobile ? '6px 0' : '8px 0' }}>
        <Title level={isMobile ? 5 : 4} style={{ color: '#fff', margin: 0, fontSize: isMobile ? 14 : undefined }}>
          Giá đất Hoà Lạc – Thạch Thất – Quốc Oai
        </Title>
        <Text style={{ color: 'rgba(255,255,255,0.75)', fontSize: isMobile ? 11 : 12 }}>
          {scrapedAt
            ? `Cập nhật: ${new Date(scrapedAt).toLocaleString('vi-VN')} | ${totalRecords} bản ghi`
            : 'Chưa có dữ liệu. Nhấn "Đồng bộ" để bắt đầu.'}
        </Text>
      </div>
    </AntHeader>
  )
}
