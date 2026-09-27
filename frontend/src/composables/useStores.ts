import { onMounted, ref } from 'vue'
import api from '@/services/api'
import type { Store } from '@/types/stores'

export function useStores() {
  const stores = ref<Store[]>([])

  const fetchStores = async () => {
    const response = await api.get('/stores')
    stores.value = response.data
  }

  onMounted(fetchStores)

  return { stores, fetchStores }
}
