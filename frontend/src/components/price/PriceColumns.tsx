import type { ReactNode } from 'react'
import { Typography, Tag, Space, Tooltip, Popover } from 'antd'
import { PhoneOutlined, EnvironmentOutlined, LinkOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { PriceItem } from '../../types'
import { POST_TYPE_CONFIG, getRecordTypeLabel, isCommentRecord } from '../../constants/postType'

const { Text } = Typography

function renderType(type: string, record: PriceItem) {
  const cfg = POST_TYPE_CONFIG[type] || { label: type, icon: null }
  const isComment = isCommentRecord(record.source)
  return (
    <Space direction="vertical" size={4} className="apple-column-stack">
      <Tag className="apple-source-pill">{getRecordTypeLabel(record.source)}</Tag>
      <Tag className="apple-type-pill" icon={cfg.icon}>
        {isComment ? `Bài cha: ${cfg.label}` : cfg.label}
      </Tag>
    </Space>
  )
}

function renderPhones(val: string) {
  if (!val) return <Text type="secondary">—</Text>
  return (
    <Space direction="vertical" size={0}>
      {val.split(' | ').map((p) => (
        <a key={p} href={`tel:${p}`} className="apple-subtle-link" style={{ whiteSpace: 'nowrap' }}>
          <PhoneOutlined /> {p}
        </a>
      ))}
    </Space>
  )
}

function renderPrice(record: PriceItem): ReactNode {
  const parts: ReactNode[] = []
  if (record.price_ty)
    parts.push(
      <Text strong className="apple-price-emphasis" style={{ fontSize: 14 }} key="ty">
        {record.price_ty}
      </Text>,
    )
  if (record.price_tr_m2)
    parts.push(<Text type="secondary" key="m2">{record.price_tr_m2}</Text>)
  if (record.price_trieu && !record.price_ty)
    parts.push(<Text key="tr">{record.price_trieu}</Text>)
  if (record.estimated_price_ty != null)
    parts.push(
      <Text type="secondary" style={{ fontSize: 11 }} key="est">
        ≈ {record.estimated_price_ty.toFixed(2)} tỷ
      </Text>,
    )
  return parts.length
    ? <Space direction="vertical" size={0}>{parts}</Space>
    : <Text type="secondary">—</Text>
}

export function getPriceColumns(): ColumnsType<PriceItem> {
  return [
    {
      title: '#',
      width: 54,
      render: (_: unknown, __: unknown, i: number) => <Text type="secondary">{i + 1}</Text>,
    },
    {
      title: 'Loại',
      dataIndex: 'post_type',
      width: 132,
      render: renderType,
    },
    {
      title: 'Nhóm',
      dataIndex: 'group_name',
      width: 120,
      ellipsis: { showTitle: false },
      render: (val: string) => (
        <Tooltip title={val}>
          <Text style={{ fontSize: 12 }}>{val || '—'}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'Tác giả',
      dataIndex: 'author',
      width: 124,
      ellipsis: true,
      render: (val: string) => <Text strong style={{ fontSize: 13 }}>{val || '—'}</Text>,
    },
    {
      title: 'SĐT',
      dataIndex: 'phone',
      width: 132,
      render: renderPhones,
    },
    {
      title: 'Giá',
      width: 132,
      render: (_: unknown, record: PriceItem) => renderPrice(record),
    },
    {
      title: 'DT',
      dataIndex: 'area',
      width: 72,
      render: (val: string) => val || '—',
    },
    {
      title: 'Vị trí',
      dataIndex: 'location',
      width: 112,
      render: (val: string) =>
        val ? (
          <Tag className="apple-location-pill" icon={<EnvironmentOutlined />}>{val}</Tag>
        ) : (
          <Text type="secondary">—</Text>
        ),
    },
    {
      title: 'Nội dung',
      dataIndex: 'text_snippet',
      width: 320,
      ellipsis: { showTitle: false },
      render: (val: string) => (
        <Popover
          content={<div style={{ maxWidth: 500, whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto' }}>{val}</div>}
          title="Nội dung đầy đủ"
          trigger="click"
        >
          <Text
            className="apple-content-preview"
            style={{ cursor: 'pointer', fontSize: 12, lineHeight: 1.45 }}
            ellipsis={{ tooltip: false }}
          >
            {val}
          </Text>
        </Popover>
      ),
    },
    {
      title: 'Link',
      dataIndex: 'link',
      width: 84,
      render: (val: string) =>
        val ? (
          <a href={val} target="_blank" rel="noopener noreferrer" className="apple-subtle-link">
            <LinkOutlined /> Xem
          </a>
        ) : (
          '—'
        ),
    },
  ]
}
