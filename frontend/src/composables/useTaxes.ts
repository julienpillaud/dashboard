import { onMounted, ref } from 'vue'
import api from '@/services/api'
import type { Tax } from '@/types/taxes'

export function useTaxes() {
  const taxes = ref<Tax[]>([])

  const fetchTaxes = async () => {
    const response = await api.get('/taxes')
    taxes.value = response.data
  }

  onMounted(fetchTaxes)

  return { taxes, fetchTaxes }
}
