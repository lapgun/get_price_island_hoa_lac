import { Card, Statistic } from 'antd'
import { POST_TYPE_CONFIG } from '../../constants/postType'

interface StatsBarProps {
  total: number
  rawCount: number
  withPhone: number
  byType: Record<string, number>
}

export default function StatsBar({ total, rawCount, withPhone, byType }: StatsBarProps) {
  if (total === 0) return null

  const stats = [
    { key: 'total', title: 'Kết quả', value: total, accent: 'primary' },
    { key: 'raw', title: 'Trước lọc', value: rawCount, accent: 'neutral' },
    { key: 'phone', title: 'Có SĐT', value: withPhone, accent: 'primary' },
    ...Object.entries(byType).map(([type, count]) => ({
      key: type,
      title: POST_TYPE_CONFIG[type]?.label || type,
      value: count,
      accent: 'neutral',
    })),
  ]

  return (
    <section className="apple-stats-grid" aria-label="Thống kê dữ liệu">
      {stats.map((item) => (
        <Card key={item.key} className={`apple-panel apple-stat-card apple-stat-card-${item.accent}`} size="small">
          <Statistic
            title={item.title}
            value={item.value}
            valueStyle={{
              color: item.accent === 'primary' ? '#0071e3' : '#1d1d1f',
              fontSize: 28,
            }}
          />
        </Card>
      ))}
    </section>
  )
}
