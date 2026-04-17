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

const { Text } = Typography

export default function GroupsPanel() {
  const [groups, setGroups] = useState<GroupItem[]>([])
  const [loading, setLoading] = useState(false)
  const [newUrl, setNewUrl] = useState('')
  const [adding, setAdding] = useState(false)
  const [messageApi, contextHolder] = message.useMessage()

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

  const getGroupLabel = (item: GroupItem) => {
    if (item.name?.trim()) return item.name.trim()

    try {
      const parsed = new URL(item.url)
      return parsed.pathname.replace(/^\/+/, '') || parsed.hostname
    } catch {
      return item.url
    }
  }

  return (
    <>
      {contextHolder}
      <Card
        className="apple-panel apple-groups-panel"
        size="small"
        title={
          <Space>
            <TeamOutlined />
            <span>Facebook Groups ({groups.length})</span>
          </Space>
        }
      >
        <Space.Compact style={{ width: '100%', marginBottom: 12 }}>
          <Input
            className="apple-control-input"
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
            className="apple-primary-btn"
          >
            Thêm
          </Button>
        </Space.Compact>

        <List
          className="apple-group-list"
          size="small"
          loading={loading}
          dataSource={groups}
          locale={{ emptyText: 'Chưa có group nào' }}
          renderItem={(item: GroupItem, index: number) => (
            <List.Item
              className="apple-group-item"
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
                    className="apple-group-delete"
                  />
                </Popconfirm>,
              ]}
            >
              <div className="apple-group-row">
                <div className="apple-group-main">
                  <Tag color="blue" className="apple-group-index">{index + 1}</Tag>
                  <div className="apple-group-copy">
                    <Text strong className="apple-group-name">
                      {getGroupLabel(item)}
                    </Text>
                    <Text className="apple-group-url" ellipsis>
                      {item.url}
                    </Text>
                  </div>
                </div>
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="apple-subtle-link apple-group-open"
                >
                  <LinkOutlined /> Mở
                </a>
              </div>
            </List.Item>
          )}
        />
      </Card>
    </>
  )
}
