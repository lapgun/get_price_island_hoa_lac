import { Row, Col, Card, Statistic } from 'antd'
import { POST_TYPE_CONFIG } from '../../constants/postType'

interface StatsBarProps {
  total: number
  rawCount: number
  withPhone: number
  byType: Record<string, number>
}

export default function StatsBar({ total, rawCount, withPhone, byType }: StatsBarProps) {
  if (total === 0) return null

  return (
    <div style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch', marginBottom: 12 }}>
      <Row gutter={8} wrap={false} style={{ minWidth: 'max-content' }}>
        <Col>
          <Card size="small" style={{ minWidth: 90 }}>
            <Statistic title="Kết quả" value={total} valueStyle={{ color: '#1677ff', fontSize: 20 }} />
          </Card>
        </Col>
        <Col>
          <Card size="small" style={{ minWidth: 90 }}>
            <Statistic title="Trước lọc" value={rawCount} valueStyle={{ fontSize: 20 }} />
          </Card>
        </Col>
        <Col>
          <Card size="small" style={{ minWidth: 90 }}>
            <Statistic title="Có SĐT" value={withPhone} valueStyle={{ color: '#389e0d', fontSize: 20 }} />
          </Card>
        </Col>
        {Object.entries(byType).map(([type, count]) => (
          <Col key={type}>
            <Card size="small" style={{ minWidth: 90 }}>
              <Statistic
                title={POST_TYPE_CONFIG[type]?.label || type}
                value={count}
                valueStyle={{
                  color: POST_TYPE_CONFIG[type]?.color === 'green' ? '#389e0d' : '#d48806',
                  fontSize: 20,
                }}
              />
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  )
}
