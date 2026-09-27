import { onMounted, ref } from 'vue'
import api from '@/services/api'

export function useOrigins() {
  const origins = ref([])

  const fetchOrigins = async () => {
    const response = await api.get('/origins')
    origins.value = response.data
  }

  onMounted(fetchOrigins)

  return { origins, fetchOrigins }
}
