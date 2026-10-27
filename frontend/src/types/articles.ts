export interface ArticleOrigin {
  name: string
  code: string | null
}

export interface ArticleVolume {
  value: number
  unit: string
}

export interface ArticleDeposit {
  unit: number
  crate: number | null
  packaging: number | null
}

export interface ArticleDetails {
  origin: ArticleOrigin | null
  color: string | null
  taste: string | null
  volume: ArticleVolume | null
  alcohol_by_volume: number | null
  deposit: ArticleDeposit | null
}

export type PosStatus = 'synced' | 'out_of_sync' | 'not_created'

export interface PosArticle {
  store_name: string
  price: number
  status: PosStatus
}

export interface Article {
  id: string
  name: string
  category: string
  total_cost: number
  tax_rate: number
  distributor: string | null
  details: ArticleDetails
  store_mapping: Record<string, PosArticle>
}
