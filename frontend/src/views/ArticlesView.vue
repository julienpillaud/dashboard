<script setup lang="ts">
// Imports
import { onMounted, ref } from 'vue'
import api from '@/services/api'
import DataTable from 'openvue/datatable'
import Column from 'openvue/column'
import Button from 'openvue/button'
import ArticleFormDialog from '@/components/ArticleFormDialog.vue'
import type { Volume } from '@/types/volumes'
import type { DataTablePageEvent } from 'openvue/datatable'
import type { Article } from '@/types/articles'
import IconField from 'openvue/iconfield'
import InputIcon from 'openvue/inputicon'
import InputText from 'openvue/inputtext'

// State
const articles = ref<Article[]>([])
const loading = ref(true)
const pageSize = ref(50)
const total = ref()
const dialogVisible = ref(false)
const search = ref('')
const first = ref(0)

// Functions
const fetchArticles = async (page = 0) => {
  const response = await api.get('/articles', {
    params: {
      page: page + 1,
      size: pageSize.value,
      search: search.value.trim() || undefined,
    },
  })
  articles.value = response.data.items
  total.value = response.data.total
}

let searchTimeout: ReturnType<typeof setTimeout>

const onSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    first.value = 0
    fetchArticles(0)
  }, 200)
}

const clearSearch = () => {
  search.value = ''
  clearTimeout(searchTimeout)
  first.value = 0
  fetchArticles(0)
}

const onPageChange = async (event: DataTablePageEvent): Promise<void> => {
  first.value = event.first
  fetchArticles(event.page)
}

const formatVolume = (volume: Volume | null): string => {
  if (!volume) return ''
  return `${volume.value} ${volume.unit}`
}

const onArticleCreated = () => {
  dialogVisible.value = false
  fetchArticles()
}

// Lifecycle
onMounted(async () => {
  try {
    fetchArticles()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <nav
    class="grid grid-cols-[1fr_auto_1fr] items-center bg-slate-100 shadow-sm sticky top-0 z-10 px-6 py-3"
  >
    <div></div>
    <IconField>
      <InputIcon class="oi oi-search" />
      <InputText v-model="search" placeholder="Rechercher…" @input="onSearch" />
      <InputIcon v-show="search" class="oi oi-times cursor-pointer" @click="clearSearch" />
    </IconField>
    <div class="flex justify-end">
      <Button label="Nouveau" @click="dialogVisible = true" />
    </div>
  </nav>

  <main class="px-6 py-6">
    <DataTable
      :value="articles"
      size="small"
      paginator
      paginatorPosition="both"
      lazy
      :loading="loading"
      :rows="pageSize"
      :first="first"
      :totalRecords="total"
      @page="onPageChange"
    >
      <Column field="name" header="Nom"></Column>
      <Column field="category" header="Catégorie"></Column>
      <Column field="details.alcohol_by_volume" header="Alcool"></Column>
      <Column header="Volume">
        <template #body="slotProps">
          {{ formatVolume(slotProps.data.details.volume) }}
        </template>
      </Column>
      <Column field="details.origin.name" header="Région">
        <template #body="{ data }">
          <div class="flex items-center gap-2">
            <img
              v-if="data.details.origin?.code"
              :src="`https://flagcdn.com/${data.details.origin.code.toLowerCase()}.svg`"
              :alt="data.details.origin.name"
              width="24"
            />
            <div v-else class="w-6 h-4 shrink-0"></div>
            <span>{{ data.details.origin?.name }}</span>
          </div>
        </template>
      </Column>
      <Column field="details.color" header="Couleur"></Column>
      <Column field="details.taste" header="Saveur"></Column>
      <Column field="distributor" header="Fournisseur"></Column>
      <Column field="total_cost" header="Prix HT"></Column>
      <Column field="tax_rate" header="TVA (%)"></Column>
    </DataTable>
  </main>

  <ArticleFormDialog v-model:visible="dialogVisible" @created="onArticleCreated" />
</template>
