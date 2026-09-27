import { onMounted, ref } from 'vue'
import api from '@/services/api'
import type { Category } from '@/types/categories'

export function useCategories() {
  const categories = ref<Category[]>([])

  const fetchCategories = async () => {
    const response = await api.get('/categories')
    categories.value = response.data
  }

  onMounted(fetchCategories)

  return { categories, fetchCategories }
}
