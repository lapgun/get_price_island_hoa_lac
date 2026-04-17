import { useState, useMemo } from 'react'
import type { PriceItem } from '../types'

export interface FilterState {
  minPrice: number
  maxPrice: number
  filterType: string | undefined
  searchText: string
  filterPrice: boolean
  filterPhone: boolean
}

export interface FilterActions {
  setMinPrice: (v: number) => void
  setMaxPrice: (v: number) => void
  setFilterType: (v: string | undefined) => void
  setSearchText: (v: string) => void
  setFilterPrice: (v: boolean) => void
  setFilterPhone: (v: boolean) => void
}

export function useFilters(data: PriceItem[]): FilterState & FilterActions & { filteredData: PriceItem[] } {
  const [minPrice, setMinPrice] = useState(1.0)
  const [maxPrice, setMaxPrice] = useState(2.0)
  const [filterType, setFilterType] = useState<string | undefined>(undefined)
  const [searchText, setSearchText] = useState('')
  const [filterPrice, setFilterPrice] = useState(false)
  const [filterPhone, setFilterPhone] = useState(false)

  const filteredData = useMemo(() => {
    let result = data
    if (filterType) result = result.filter((d) => d.post_type === filterType)
    if (filterPrice) {
      result = result.filter((d) => {
        const est = d.estimated_price_ty
        return est != null && est >= minPrice && est <= maxPrice
      })
    }
    if (filterPhone) result = result.filter((d) => !!d.phone)
    if (searchText) {
      const s = searchText.toLowerCase()
      result = result.filter((d) =>
        [d.phone, d.author, d.location, d.text_snippet, d.group_name]
          .some((field) => (field || '').toLowerCase().includes(s)),
      )
    }
    return result
  }, [data, filterType, filterPrice, filterPhone, minPrice, maxPrice, searchText])

  return {
    filteredData,
    minPrice, setMinPrice,
    maxPrice, setMaxPrice,
    filterType, setFilterType,
    searchText, setSearchText,
    filterPrice, setFilterPrice,
    filterPhone, setFilterPhone,
  }
}
