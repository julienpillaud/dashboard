import type { Volume } from '@/types/volumes'

const LOCALE = 'fr-FR'

export const formatCurrency = (value: number, digits: number = 2) =>
  new Intl.NumberFormat(LOCALE, {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 2,
    maximumFractionDigits: digits,
  }).format(value)

export const formatNumber = (value: number, digits: number = 1) =>
  new Intl.NumberFormat(LOCALE, {
    maximumFractionDigits: digits,
  }).format(value)

export const formatPercent = (value: number, digits: number = 1) =>
  new Intl.NumberFormat(LOCALE, {
    style: 'unit',
    unit: 'percent',
    maximumFractionDigits: digits,
  }).format(value)

export const formatVolume = (volume: Volume | null): string => {
  if (!volume) return ''
  return `${formatNumber(volume.value)} ${volume.unit}`
}
