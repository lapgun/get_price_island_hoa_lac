export interface GroupItem {
  url: string
  name: string | null
}

export interface GroupListResponse {
  groups: GroupItem[]
  count: number
}

export async function fetchGroups(): Promise<GroupListResponse> {
  const res = await fetch('/api/groups')
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function addGroup(url: string): Promise<GroupListResponse> {
  const res = await fetch('/api/groups', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function removeGroup(url: string): Promise<GroupListResponse> {
  const res = await fetch('/api/groups', {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}
