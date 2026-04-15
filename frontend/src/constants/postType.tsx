import React from 'react'
import {
  ShopOutlined,
  ShoppingCartOutlined,
  CommentOutlined,
} from '@ant-design/icons'

export interface PostTypeConfig {
  color: string
  label: string
  icon: React.ReactNode
}

export interface PostTypeOption {
  value: string
  label: string
}

export const POST_TYPE_CONFIG: Record<string, PostTypeConfig> = {
  'bán': { color: 'green', label: 'Bán', icon: <ShopOutlined /> },
  'mua': { color: 'orange', label: 'Mua', icon: <ShoppingCartOutlined /> },
  'cmt_bài_mua': { color: 'red', label: 'Comment dưới bài mua', icon: <CommentOutlined /> },
  'cmt_bài_bán': { color: 'blue', label: 'Comment dưới bài bán', icon: <CommentOutlined /> },
}

export const POST_TYPE_OPTIONS: PostTypeOption[] = [
  { value: 'bán', label: '🏷️ Bài bán' },
  { value: 'mua', label: '🛒 Bài mua' },
  { value: 'cmt_bài_mua', label: '💬 Comment dưới bài mua' },
  { value: 'cmt_bài_bán', label: '💬 Comment dưới bài bán' },
]


export function isCommentRecord(source: string): boolean {
  const s = (source || '').toLowerCase()
  return s.includes('comment')
}


export function getRecordTypeLabel(source: string): string {
  return isCommentRecord(source) ? 'Comment' : 'Bài viết'
}
