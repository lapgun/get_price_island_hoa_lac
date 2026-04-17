import { Card, Tag, Space, Typography } from 'antd'
import { PhoneOutlined, EnvironmentOutlined, LinkOutlined } from '@ant-design/icons'
import type { PriceItem } from '../../types'
import { POST_TYPE_CONFIG, getRecordTypeLabel, isCommentRecord } from '../../constants/postType'

const { Text } = Typography

interface PriceCardProps {
  item: PriceItem
  index: number
}

export default function PriceCard({ item, index }: PriceCardProps) {
  const cfg = POST_TYPE_CONFIG[item.post_type] || { color: 'default', label: item.post_type, icon: null }
  const isComment = isCommentRecord(item.source)

  return (
    <Card
      className="apple-panel"
      size="small"
      style={{ marginBottom: 8 }}
      title={
        <Space size={4} wrap>
          <Text type="secondary" style={{ fontSize: 11 }}>#{index + 1}</Text>
          <Tag style={{ fontSize: 11, margin: 0 }}>
            {getRecordTypeLabel(item.source)}
          </Tag>
          <Tag color="blue" icon={cfg.icon} style={{ margin: 0 }}>
            {isComment ? `Bài cha: ${cfg.label}` : cfg.label}
          </Tag>
        </Space>
      }
      extra={
        item.link ? (
          <a href={item.link} target="_blank" rel="noopener noreferrer" className="apple-subtle-link">
            <LinkOutlined /> Xem
          </a>
        ) : null
      }
    >
      <div className="apple-card-price-row">
        <Space direction="vertical" size={0}>
          {item.price_ty && (
            <Text strong className="apple-price-emphasis" style={{ fontSize: 16 }}>{item.price_ty}</Text>
          )}
          {item.price_tr_m2 && <Text type="secondary">{item.price_tr_m2}</Text>}
          {!item.price_ty && item.price_trieu && <Text>{item.price_trieu}</Text>}
          {item.estimated_price_ty != null && (
            <Text type="secondary" style={{ fontSize: 11 }}>≈ {item.estimated_price_ty.toFixed(2)} tỷ</Text>
          )}
          {!item.price_ty && !item.price_tr_m2 && !item.price_trieu && (
            <Text type="secondary">—</Text>
          )}
        </Space>
        <Space direction="vertical" size={2} style={{ textAlign: 'right', alignItems: 'flex-end' }}>
          {item.area && <Text style={{ fontSize: 13 }}>{item.area}</Text>}
          {item.location && (
            <Tag icon={<EnvironmentOutlined />} style={{ margin: 0 }}>{item.location}</Tag>
          )}
        </Space>
      </div>

      <div className="apple-card-author">
        <Text strong style={{ fontSize: 13 }}>{item.author || '—'}</Text>
        {item.phone && (
          <div style={{ marginTop: 4 }}>
            <Space wrap size={8}>
              {item.phone.split(' | ').map((p) => (
                <a key={p} href={`tel:${p}`} className="apple-subtle-link" style={{ fontSize: 14 }}>
                  <PhoneOutlined /> {p}
                </a>
              ))}
            </Space>
          </div>
        )}
      </div>

      <Text className="apple-content-preview" style={{ fontSize: 12 }}>
        {item.text_snippet}
      </Text>

      <div className="apple-card-footer">
        <Text type="secondary" style={{ fontSize: 11 }}>{item.group_name}</Text>
      </div>
    </Card>
  )
}
