export type MarginInput = {
  price: number | null
  totalCost: number | null
  taxRate: number | null
}

type Severity = 'danger' | 'warn' | 'success'
type Thresholds = { danger: number; warn: number }

export const MARGIN_AMOUNT_THRESHOLDS: Thresholds = { danger: 0, warn: 1 } // en €
export const MARGIN_RATE_THRESHOLDS: Thresholds = { danger: 0, warn: 5 } // en %

export const getTaxFactor = (taxRate: number | null): number | null => {
  if (taxRate == null) return null
  return 1 + taxRate / 100
}

export const getMarginAmount = ({ price, totalCost, taxRate }: MarginInput): number | null => {
  const factor = getTaxFactor(taxRate)
  if (price == null || totalCost == null || factor == null) return null
  return price / factor - totalCost
}

export const getMarginRate = (input: MarginInput): number | null => {
  const factor = getTaxFactor(input.taxRate)
  const amount = getMarginAmount(input)
  if (amount == null || !input.price || factor == null) return null
  return (amount / (input.price / factor)) * 100
}

const getSeverity = (value: number, { danger, warn }: Thresholds): Severity => {
  if (value <= danger) return 'danger'
  if (value <= warn) return 'warn'
  return 'success'
}

export const getMarginAmountSeverity = (amount: number): Severity =>
  getSeverity(amount, MARGIN_AMOUNT_THRESHOLDS)

export const getMarginRateSeverity = (rate: number): Severity =>
  getSeverity(rate, MARGIN_RATE_THRESHOLDS)
