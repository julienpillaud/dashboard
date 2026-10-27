<script setup lang="ts">
import axios from 'axios'
import Button from 'openvue/button'
import Column from 'openvue/column'
import DataTable from 'openvue/datatable'
import Message from 'openvue/message'
import ProgressSpinner from 'openvue/progressspinner'
import Select from 'openvue/select'
import { ref, watch } from 'vue'

import AppNav from '@/components/AppNav.vue'
import { useStores } from '@/composables/useStores'
import api from '@/services/api'
import type { Inventory } from '@/types/inventories'
import { formatCurrency, formatDateTime } from '@/utils/format'
// =============================================================================
// State
// The spinner cycles through 4 colors by default: use the theme color for all of them
const SPINNER_TOKENS = {
  root: {
    colorOne: '{primary.color}',
    colorTwo: '{primary.color}',
    colorThree: '{primary.color}',
    colorFour: '{primary.color}',
  },
}
const { stores } = useStores()
const storeId = ref<string>()
const inventories = ref<Inventory[]>([])
// True once the list of the selected store has been received, so the empty message never flashes
const loaded = ref(false)
const loading = ref(false)
const creating = ref(false)
const error = ref('')
// =============================================================================
// Functions
const fetchInventories = async () => {
  if (!storeId.value) return

  // Only show the spinner for slow requests to avoid a flash on fast ones
  const loadingTimeout = setTimeout(() => (loading.value = true), 300)
  try {
    const response = await api.get('/inventories', { params: { store_id: storeId.value } })
    inventories.value = response.data
    loaded.value = true
  } catch (e) {
    console.error(e)
    error.value = 'Impossible de charger les inventaires'
  } finally {
    clearTimeout(loadingTimeout)
    loading.value = false
  }
}

const createInventory = async () => {
  if (!storeId.value) return

  creating.value = true
  error.value = ''
  try {
    await api.post('/inventories', null, { params: { store_id: storeId.value } })
    await fetchInventories()
  } catch (e) {
    console.error(e)
    error.value =
      axios.isAxiosError(e) && e.response?.data?.detail
        ? e.response.data.detail
        : "Impossible de créer l'inventaire"
  } finally {
    creating.value = false
  }
}

const printInventory = (inventory: Inventory) => {
  const params = new URLSearchParams({ store_id: storeId.value ?? '' })
  window.open(`/api/inventories/${inventory.id}/preview?${params}`, '_blank')
}
// =============================================================================
// Lifecycle
watch(stores, (value) => {
  if (!storeId.value && value.length > 0) {
    storeId.value = value[0]?.id
  }
})

watch(storeId, () => {
  error.value = ''
  inventories.value = []
  loaded.value = false
  fetchInventories()
})
// =============================================================================
</script>

<template>
  <div class="h-screen flex flex-col">
    <AppNav>
      <template #center>
        <Select
          v-model="storeId"
          :options="stores"
          optionLabel="name"
          optionValue="id"
          placeholder="Magasin"
          class="w-64"
        />
      </template>
      <template #actions>
        <Button
          label="Nouvel inventaire"
          :loading="creating"
          :disabled="!storeId"
          @click="createInventory"
        />
      </template>
    </AppNav>

    <main class="flex-1 min-h-0 px-6 py-6 flex flex-col gap-4">
      <Message v-if="error" severity="error" closable @close="error = ''">{{ error }}</Message>

      <DataTable
        :value="inventories"
        dataKey="id"
        size="small"
        :loading="loading"
        scrollable
        scrollHeight="flex"
        class="flex-1 min-h-0"
      >
        <template #empty>
          <span v-if="loaded">Aucun inventaire pour ce magasin</span>
        </template>
        <Column field="created_at" header="Date">
          <template #body="slotProps">
            {{ formatDateTime(slotProps.data.created_at) }}
          </template>
        </Column>
        <Column field="articles_count" header="Articles"></Column>
        <Column field="amounts.amount" header="Stock HT">
          <template #body="slotProps">
            {{ formatCurrency(slotProps.data.amounts.amount) }}
          </template>
        </Column>
        <Column field="amounts.deposit_amount" header="Consignes">
          <template #body="slotProps">
            {{ formatCurrency(slotProps.data.amounts.deposit_amount) }}
          </template>
        </Column>
        <Column header="Total" bodyClass="font-bold">
          <template #body="slotProps">
            {{
              formatCurrency(slotProps.data.amounts.amount + slotProps.data.amounts.deposit_amount)
            }}
          </template>
        </Column>
        <Column style="width: 4rem">
          <template #body="slotProps">
            <Button
              icon="oi oi-print"
              text
              rounded
              aria-label="Imprimer"
              @click="printInventory(slotProps.data)"
            />
          </template>
        </Column>
      </DataTable>
    </main>

    <!-- Blocks every interaction while the inventory is being generated -->
    <div
      v-if="creating"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/30"
    >
      <div class="flex flex-col items-center gap-4 rounded-xl bg-white px-10 py-8 shadow-sm">
        <ProgressSpinner strokeWidth="4" style="width: 3rem; height: 3rem" :dt="SPINNER_TOKENS" />
        <span class="font-medium text-slate-700">Génération de l'inventaire…</span>
      </div>
    </div>
  </div>
</template>
