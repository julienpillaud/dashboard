<script setup lang="ts">
import {
  getMarginAmount,
  getMarginRate,
  getMarginAmountSeverity,
  getMarginRateSeverity,
} from '@/utils/margins'
import { onMounted, ref } from 'vue'
import api from '@/services/api'
import DataTable from 'openvue/datatable'
import Column from 'openvue/column'
import Button from 'openvue/button'
import ArticleFormDialog from '@/components/ArticleFormDialog.vue'
import type { DataTablePageEvent } from 'openvue/datatable'
import type { Article } from '@/types/articles'
import IconField from 'openvue/iconfield'
import InputIcon from 'openvue/inputicon'
import InputText from 'openvue/inputtext'
import Tag from 'openvue/tag'
import { formatNumber, formatPercent, formatCurrency, formatVolume } from '@/utils/format'
import { getColorStyle } from '@/utils/colors'
// =============================================================================
// State
const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]
const articles = ref<Article[]>([])
const expandedRows = ref({})
const loading = ref(true)
const pageSize = ref(20)
const total = ref()
const dialogVisible = ref(false)
const search = ref('')
const first = ref(0)
// =============================================================================
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
  pageSize.value = event.rows
  first.value = event.first
  fetchArticles(event.page)
}

const onArticleCreated = () => {
  dialogVisible.value = false
  fetchArticles()
}

const mappingToRows = (parent: Article) =>
  Object.entries(parent.store_mapping ?? {}).map(([key, article]) => {
    const input = {
      price: article.price,
      totalCost: parent.total_cost != null ? parent.total_cost : null,
      taxRate: parent.tax_rate != null ? parent.tax_rate : null,
    }
    return {
      key,
      ...article,
      marginAmount: getMarginAmount(input),
      marginRate: getMarginRate(input),
    }
  })
// =============================================================================
// Lifecycle
onMounted(async () => {
  try {
    fetchArticles()
  } finally {
    loading.value = false
  }
})
// =============================================================================
</script>

<template>
  <div class="h-screen flex flex-col">
    <nav class="grid grid-cols-[1fr_auto_1fr] items-center bg-slate-100 shadow-sm px-6 py-3">
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

    <main class="flex-1 min-h-0 px-6 py-6">
      <DataTable
        v-model:expandedRows="expandedRows"
        :value="articles"
        dataKey="id"
        size="small"
        paginator
        paginatorPosition="top"
        :rowsPerPageOptions="PAGE_SIZE_OPTIONS"
        lazy
        :loading="loading"
        :rows="pageSize"
        :first="first"
        :totalRecords="total"
        @page="onPageChange"
        scrollable
        scrollHeight="flex"
        class="h-full"
      >
        <Column expander style="width: 3rem" />
        <Column field="name" header="Nom"></Column>
        <Column field="category" header="Catégorie"></Column>
        <!-- Alcool -->
        <Column field="details.alcohol_by_volume" header="Alcool">
          <template #body="slotProps">
            {{
              slotProps.data.details.alcohol_by_volume
                ? formatNumber(slotProps.data.details.alcohol_by_volume)
                : ''
            }}
          </template>
        </Column>
        <!-- Volume -->
        <Column header="Volume">
          <template #body="slotProps">
            {{ formatVolume(slotProps.data.details.volume) }}
          </template>
        </Column>
        <!-- Région -->
        <Column field="details.origin.name" header="Région">
          <template #body="slotProps">
            <Tag
              v-if="slotProps.data.details.origin"
              style="border: 1px solid #d1d5db; background: transparent; color: #4b5563"
            >
              <div class="flex items-center gap-2">
                <img
                  v-if="slotProps.data.details.origin?.code"
                  :src="`https://flagcdn.com/${slotProps.data.details.origin.code.toLowerCase()}.svg`"
                  width="18"
                />
                <span class="text-base">{{ slotProps.data.details.origin?.name }}</span>
              </div>
            </Tag>
          </template>
        </Column>
        <!-- Couleur -->
        <Column field="details.color" header="Couleur">
          <template #body="slotProps">
            <Tag
              v-if="slotProps.data.details.color"
              :value="slotProps.data.details.color"
              :style="getColorStyle(slotProps.data.details.color)"
            />
          </template>
        </Column>
        <!-- Saveur -->
        <Column field="details.taste" header="Saveur"></Column>
        <!-- Fournisseur -->
        <Column field="distributor" header="Fournisseur"></Column>
        <!-- Prix HT -->
        <Column field="total_cost" header="Prix HT">
          <template #body="slotProps">
            {{ formatCurrency(slotProps.data.total_cost, 4) }}
          </template>
        </Column>
        <!-- TVA -->
        <Column field="tax_rate" header="TVA">
          <template #body="slotProps">
            {{ formatPercent(slotProps.data.tax_rate) }}
          </template>
        </Column>
        <!-- ------------------------------------------------------------------ -->
        <!-- Expansion -->
        <template #expansion="slotProps">
          <div class="p-2">
            <DataTable
              :value="mappingToRows(slotProps.data)"
              size="small"
              class="max-w-4xl mx-auto"
            >
              <Column field="store_name" header="Magasin" bodyClass="font-bold"></Column>
              <Column field="price" header="Prix">
                <template #body="slotProps">
                  <Tag :value="formatCurrency(slotProps.data.price)" rounded></Tag>
                </template>
              </Column>
              <Column field="marginAmount" header="Marge (€)">
                <template #body="slotProps">
                  <Tag
                    :value="formatCurrency(slotProps.data.marginAmount)"
                    :severity="getMarginAmountSeverity(slotProps.data.marginAmount)"
                  />
                </template>
              </Column>
              <Column field="marginRate" header="Marge (%)">
                <template #body="slotProps">
                  <Tag
                    :value="formatPercent(slotProps.data.marginRate)"
                    :severity="getMarginRateSeverity(slotProps.data.marginRate)"
                  />
                </template>
              </Column>
              <Column header="Stock">
                <template #body="slotProps">
                  <Tag
                    :value="slotProps.data.raw.stock_quantity"
                    :severity="slotProps.data.raw.stock_quantity > 0 ? 'success' : 'danger'"
                    rounded
                  />
                </template>
              </Column>
            </DataTable>
          </div>
        </template>
        <!-- ------------------------------------------------------------------ -->
      </DataTable>
    </main>

    <ArticleFormDialog v-model:visible="dialogVisible" @created="onArticleCreated" />
  </div>
</template>
