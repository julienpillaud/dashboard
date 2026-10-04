export interface PosArticle {
  store_name: string
  price: number
}

export interface Article {
  id: string
  total_cost: number
  tax_rate: number
  store_mapping: Record<string, PosArticle>
}
