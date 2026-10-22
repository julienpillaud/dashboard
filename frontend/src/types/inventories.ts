export interface InventoryAmounts {
  amount: number
  deposit_amount: number
}

export interface Inventory {
  id: string
  store_name: string
  created_at: string
  amounts: InventoryAmounts
  articles_count: number
}
