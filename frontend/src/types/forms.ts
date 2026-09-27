export interface FormDetails {
  origin: string | null
  color: string | null
  taste: string | null
  volume: {
    value: number | null
    unit: string | null
  }
  alcohol_by_volume: number | null
  deposit: {
    unit: number | null
    crate: number | null
    packaging: number | null
  }
}

export interface ArticleForm {
  name: string | null
  total_cost: number | null
  tax_rate: number | null
  price: number | null
  distributor: string | null
  details: FormDetails
}
