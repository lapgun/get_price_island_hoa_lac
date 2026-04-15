import { useState, useEffect, useCallback } from 'react'
import { Card, List, Input, Button, Space, Typography, Popconfirm, Tag, message } from 'antd'
import {
  PlusOutlined,
  DeleteOutlined,
  LinkOutlined,
  TeamOutlined,
} from '@ant-design/icons'
import { fetchGroups, addGroup, removeGroup } from '../../api/groups'
import type { GroupItem } from '../../api/groups'
import { useIsMobile } from '../../hooks/useIsMobile'

const { Text } = Typography

export default function GroupsPanel() {
  const [groups, setGroups] = useState<GroupItem[]>([])
  const [loading, setLoading] = useState(false)
  const [newUrl, setNewUrl] = useState('')
  const [adding, setAdding] = useState(false)
  const [messageApi, contextHolder] = message.useMessage()
  const isMobile = useIsMobile()

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetchGroups()
      setGroups(res.groups)
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleAdd = async () => {
    if (!newUrl.trim()) return
    setAdding(true)
    try {
      const res = await addGroup(newUrl.trim())
      setGroups(res.groups)
      setNewUrl('')
      messageApi.success('Đã thêm group')
    } catch (e: unknown) {
      messageApi.error(e instanceof Error ? e.message : 'Lỗi thêm group')
    } finally {
      setAdding(false)
    }
  }

  const handleRemove = async (url: string) => {
    try {
      const res = await removeGroup(url)
      setGroups(res.groups)
      messageApi.success('Đã xoá group')
    } catch (e: unknown) {
      messageApi.error(e instanceof Error ? e.message : 'Lỗi xoá group')
    }
  }

  return (
    <>
      {contextHolder}
      <Card
        size="small"
        title={
          <Space>
            <TeamOutlined />
            <span>Facebook Groups ({groups.length})</span>
          </Space>
        }
        style={{ marginBottom: isMobile ? 8 : 12 }}
      >
        <Space.Compact style={{ width: '100%', marginBottom: 12 }}>
          <Input
            placeholder="Dán URL Facebook Group..."
            value={newUrl}
            onChange={(e) => setNewUrl(e.target.value)}
            onPressEnter={handleAdd}
            allowClear
          />
          <Button
            type="primary"
            icon={<PlusOutlined />}
            loading={adding}
            onClick={handleAdd}
          >
            Thêm
          </Button>
        </Space.Compact>

        <List
          size="small"
          loading={loading}
          dataSource={groups}
          locale={{ emptyText: 'Chưa có group nào' }}
          renderItem={(item: GroupItem, index: number) => (
            <List.Item
              style={{ padding: '6px 0' }}
              actions={[
                <Popconfirm
                  key="del"
                  title="Xoá group này?"
                  onConfirm={() => handleRemove(item.url)}
                  okText="Xoá"
                  cancelText="Huỷ"
                >
                  <Button
                    type="text"
                    danger
                    size="small"
                    icon={<DeleteOutlined />}
                  />
                </Popconfirm>,
              ]}
            >
              <Space size={isMobile ? 4 : 8} wrap>
                <Tag color="blue">{index + 1}</Tag>
                <Text strong style={{ fontSize: 13 }}>
                  {item.name || 'Unknown'}
                </Text>
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ fontSize: 12 }}
                >
                  <LinkOutlined /> Mở
                </a>
              </Space>
            </List.Item>
          )}
        />
      </Card>
    </>
  )
}
