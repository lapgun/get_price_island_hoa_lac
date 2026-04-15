import React from 'react'
import { Typography, Tag, Space, Tooltip, Popover } from 'antd'
import {
  PhoneOutlined,
  EnvironmentOutlined,
  LinkOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { PriceItem } from '../../types'
import { POST_TYPE_CONFIG, getRecordTypeLabel, isCommentRecord } from '../../constants/postType'

const { Text } = Typography

export function getPriceColumns(): ColumnsType<PriceItem> {
  return [
    {
      title: '#',
      width: 50,
      render: (_: unknown, __: unknown, i: number) => i + 1,
    },
    {
      title: 'Loại',
      dataIndex: 'post_type',
      width: 140,
      render: (type: string, record: PriceItem) => {
        const cfg = POST_TYPE_CONFIG[type] || { color: 'default', label: type, icon: null }
        const isComment = isCommentRecord(record.source)
        return (
          <Space direction="vertical" size={0}>
            <Tag color={isComment ? 'cyan' : 'purple'} style={{ fontSize: 11 }}>
              {getRecordTypeLabel(record.source)}
            </Tag>
            <Tag color={cfg.color} icon={cfg.icon}>
              {isComment ? `Bài cha: ${cfg.label}` : cfg.label}
            </Tag>
          </Space>
        )
      },
    },
    {
      title: 'Nhóm',
      dataIndex: 'group_name',
      width: 150,
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
      width: 130,
      ellipsis: true,
      render: (val: string) => <Text strong style={{ fontSize: 13 }}>{val || '—'}</Text>,
    },
    {
      title: 'SĐT',
      dataIndex: 'phone',
      width: 140,
      render: (val: string) => {
        if (!val) return <Text type="secondary">—</Text>
        return (
          <Space direction="vertical" size={0}>
            {val.split(' | ').map((p, i) => (
              <a key={i} href={`tel:${p}`} style={{ whiteSpace: 'nowrap' }}>
                <PhoneOutlined /> {p}
              </a>
            ))}
          </Space>
        )
      },
    },
    {
      title: 'Giá',
      width: 150,
      render: (_: unknown, record: PriceItem) => {
        const parts: React.ReactNode[] = []
        if (record.price_ty)
          parts.push(<Text strong style={{ color: '#cf1322', fontSize: 14 }} key="ty">{record.price_ty}</Text>)
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
        if (!parts.length) return <Text type="secondary">—</Text>
        return <Space direction="vertical" size={0}>{parts}</Space>
      },
    },
    {
      title: 'DT',
      dataIndex: 'area',
      width: 80,
      render: (val: string) => val || '—',
    },
    {
      title: 'Vị trí',
      dataIndex: 'location',
      width: 120,
      render: (val: string) =>
        val ? (
          <Tag color="green" icon={<EnvironmentOutlined />}>{val}</Tag>
        ) : (
          <Text type="secondary">—</Text>
        ),
    },
    {
      title: 'Nội dung',
      dataIndex: 'text_snippet',
      ellipsis: { showTitle: false },
      render: (val: string) => (
        <Popover
          content={<div style={{ maxWidth: 500, whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto' }}>{val}</div>}
          title="Nội dung đầy đủ"
          trigger="click"
        >
          <Text
            style={{ cursor: 'pointer', fontSize: 12, lineHeight: 1.4 }}
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
      width: 70,
      render: (val: string) =>
        val ? (
          <a href={val} target="_blank" rel="noopener noreferrer">
            <LinkOutlined /> Xem
          </a>
        ) : (
          '—'
        ),
    },
  ]
}
