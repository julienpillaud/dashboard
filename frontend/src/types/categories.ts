export interface CategoryFields {
  origin: boolean
  color: boolean
  taste: boolean
  volume: boolean
  alcohol_by_volume: boolean
  deposit_unit: boolean
  deposit_crate: boolean
  deposit_packaging: boolean
}

export interface Category {
  id: string
  name: string
  fields: CategoryFields
}
