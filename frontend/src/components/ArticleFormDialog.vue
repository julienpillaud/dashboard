<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import api from '@/services/api'
import { useStores } from '@/composables/useStores'
import { useCategories } from '@/composables/useCategories'
import { useTaxes } from '@/composables/useTaxes'
import { useOrigins } from '@/composables/useOrigins'
import { useToast } from 'openvue/usetoast'
import Dialog from 'openvue/dialog'
import Button from 'openvue/button'
import FloatLabel from 'openvue/floatlabel'
import InputText from 'openvue/inputtext'
import Select from 'openvue/select'
import InputNumber from 'openvue/inputnumber'
import Divider from 'openvue/divider'
import type { CategoryFields } from '@/types/categories'
import type { ArticleForm } from '@/types/forms'
import { getMarginAmount, getMarginRate } from '@/utils/margins'
// =============================================================================
// Props - Emits
const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  created: []
}>()
// =============================================================================
// Composables
const toast = useToast()

const { stores } = useStores()
const { categories } = useCategories()
const { taxes } = useTaxes()
const { origins } = useOrigins()
// =============================================================================
// Constants
const INITIAL_FORM: ArticleForm = {
  name: null,
  total_cost: null,
  tax_rate: null,
  prices: {},
  distributor: null,
  details: {
    origin: null,
    color: null,
    taste: null,
    volume: { value: null, unit: null },
    alcohol_by_volume: null,
    deposit: { unit: null, crate: null, packaging: null },
  },
}
// =============================================================================
// State
const form = ref<ArticleForm>(structuredClone(INITIAL_FORM))
const selectedCategoryId = ref<string | null>(null)
const recommendedPrices = ref<Record<string, number | null>>({})
const submitAttempted = ref<boolean>(false)
const saving = ref<boolean>(false)
// =============================================================================
// Computed
const selectedCategory = computed(() =>
  categories.value.find((c) => c.id === selectedCategoryId.value),
)

const taxOptions = computed(() => taxes.value.map((t) => ({ ...t, label: `${t.rate} %` })))

const canComputePvc = computed(() =>
  [selectedCategoryId.value, form.value.total_cost, form.value.tax_rate].every((v) => v != null),
)

const isFormValid = computed(() => {
  const allPricesSet = stores.value.every((store) => form.value.prices[store.id])
  return (
    !!form.value.name &&
    !!selectedCategoryId.value &&
    !!form.value.total_cost &&
    !!form.value.tax_rate &&
    allPricesSet
  )
})
// =============================================================================
// Functions
const show = (field: keyof CategoryFields) => selectedCategory.value?.fields?.[field] === true

const resetPrices = () => {
  recommendedPrices.value = {}
  form.value.prices = {}
}

const fetchRecommendedPrices = async () => {
  const responses = await Promise.all(
    stores.value.map(async (store) => {
      const response = await api.post('/pricing/recommended-price', {
        store_id: store.id,
        category_id: selectedCategoryId.value,
        total_cost: form.value.total_cost,
        tax_rate: form.value.tax_rate,
      })
      return [store.id, response.data.recommended_price]
    }),
  )

  const prices = Object.fromEntries(responses)
  recommendedPrices.value = { ...prices }
  form.value.prices = { ...prices }
}

const marginAmount = (storeId: string) => {
  return getMarginAmount({
    price: form.value.prices[storeId] ?? null,
    totalCost: form.value.total_cost,
    taxRate: form.value.tax_rate,
  })
}

const marginRate = (storeId: string) => {
  return getMarginRate({
    price: form.value.prices[storeId] ?? null,
    totalCost: form.value.total_cost,
    taxRate: form.value.tax_rate,
  })
}

const getPriceDiff = (storeId: string) => {
  const recommendedPrice = recommendedPrices.value[storeId]
  const price = form.value.prices[storeId]

  if (!price || !recommendedPrice) return 0
  return price - recommendedPrice
}

const priceColorClass = (storeId: string) => {
  const priceDiff = getPriceDiff(storeId)
  if (priceDiff < 0) return 'text-red-700!'
  if (priceDiff > 0) return 'text-green-700!'
  return ''
}

const closeDialog = () => {
  emit('update:visible', false)
}

const resetForm = () => {
  form.value = structuredClone(INITIAL_FORM)
  selectedCategoryId.value = null
  submitAttempted.value = false
  recommendedPrices.value = {}
}

const buildDetails = () => {
  const { volume, deposit, ...simple } = form.value.details

  return {
    ...Object.fromEntries(
      Object.entries(simple).map(([key, value]) => [
        key,
        show(key as keyof CategoryFields) ? value : null,
      ]),
    ),
    volume: show('volume') && volume.value != null ? volume : null,
    deposit:
      show('deposit_unit') && deposit.unit != null
        ? {
            unit: deposit.unit,
            crate: show('deposit_crate') ? deposit.crate : null,
            packaging: show('deposit_packaging') ? deposit.packaging : null,
          }
        : null,
  }
}

const submitArticle = async () => {
  submitAttempted.value = true
  if (!isFormValid.value) return

  saving.value = true
  try {
    await api.post('/articles', {
      ...form.value,
      category: selectedCategory.value?.name,
      details: buildDetails(),
    })
    toast.add({ severity: 'success', summary: 'Article créé', detail: form.value.name, life: 5000 })
    emit('created')
  } catch (e) {
    console.error(e)
    toast.add({ severity: 'error', summary: 'Erreur', detail: 'La création a échoué', life: 5000 })
  } finally {
    saving.value = false
  }
}
// =============================================================================
// Watchers
watch([selectedCategoryId, () => form.value.total_cost, () => form.value.tax_rate], () => {
  if (!canComputePvc.value) {
    resetPrices()
    return
  }
  fetchRecommendedPrices()
})
// =============================================================================
</script>

<template>
  <Dialog
    :visible="props.visible"
    :closable="!saving"
    :closeOnEscape="!saving"
    @update:visible="emit('update:visible', $event)"
    @after-hide="resetForm"
    position="top"
    :draggable="false"
    modal
    header="Nouvel article"
    :style="{ width: '50vw' }"
  >
    <div class="pt-2">
      <FloatLabel variant="on">
        <Select
          inputId="category"
          v-model="selectedCategoryId"
          :options="categories"
          optionLabel="name"
          optionValue="id"
          :invalid="submitAttempted && !selectedCategoryId"
          filter
          showClear
          fluid
        />
        <label for="category">Catégorie</label>
      </FloatLabel>
    </div>

    <div class="flex flex-col gap-3 pt-2">
      <template v-if="selectedCategory">
        <!-- --------------------------------------------------------------- -->
        <div class="grid grid-cols-1 gap-3">
          <FloatLabel variant="on">
            <InputText
              id="article-name"
              v-model="form.name"
              :invalid="submitAttempted && !form.name"
              fluid
            />
            <label for="article-name">Nom</label>
          </FloatLabel>
          <FloatLabel variant="on">
            <InputText id="distributor" v-model="form.distributor" fluid />
            <label for="distributor">Fournisseur</label>
          </FloatLabel>
        </div>
        <!-- --------------------------------------------------------------- -->
        <div class="grid grid-cols-2 gap-3">
          <!-- Volume -->
          <div v-if="show('volume')" class="flex gap-1">
            <FloatLabel variant="on" class="flex-1">
              <InputNumber inputId="volume-value" v-model="form.details.volume.value" fluid />
              <label for="volume-value">Volume</label>
            </FloatLabel>
            <Select
              v-model="form.details.volume.unit"
              :options="[
                { label: 'cL', value: 'cL' },
                { label: 'L', value: 'L' },
              ]"
              optionLabel="label"
              optionValue="value"
              class="w-24"
            />
          </div>
          <FloatLabel v-if="show('alcohol_by_volume')" variant="on">
            <InputNumber
              inputId="alcohol_by_volume"
              v-model="form.details.alcohol_by_volume"
              :min="0"
              :max="100"
              :maxFractionDigits="1"
              :step="0.1"
              suffix=" %"
              fluid
            />
            <label for="alcohol_by_volume">Alcool</label>
          </FloatLabel>
          <FloatLabel v-if="show('origin')" variant="on">
            <Select
              inputId="origin"
              v-model="form.details.origin"
              :options="origins"
              optionLabel="name"
              filter
              showClear
              fluid
            />
            <label for="origin">Pays / Région</label>
          </FloatLabel>
          <FloatLabel v-if="show('color')" variant="on">
            <InputText id="color" v-model="form.details.color" fluid />
            <label for="color">Couleur</label>
          </FloatLabel>
          <FloatLabel v-if="show('taste')" variant="on">
            <InputText id="taste" v-model="form.details.taste" fluid />
            <label for="taste">Saveur</label>
          </FloatLabel>
        </div>
        <!-- --------------------------------------------------------------- -->
        <!-- Prices -->
        <div>
          <Divider />
          <div class="grid grid-cols-2 gap-2">
            <FloatLabel variant="on">
              <InputNumber
                inputId="total_cost"
                v-model="form.total_cost"
                @input="(event) => (form.total_cost = (event.value as any) ?? null)"
                :invalid="submitAttempted && !form.total_cost"
                mode="currency"
                currency="EUR"
                locale="fr-FR"
                :maxFractionDigits="4"
                :min="0.01"
                :step="0.1"
                fluid
              />
              <label for="total_cost">Tarif HT</label>
            </FloatLabel>
            <FloatLabel variant="on">
              <Select
                inputId="tax_rate"
                v-model="form.tax_rate"
                :options="taxOptions"
                optionLabel="label"
                optionValue="rate"
                :invalid="submitAttempted && !form.tax_rate"
                showClear
                fluid
              />
              <label for="tax_rate">TVA</label>
            </FloatLabel>
          </div>

          <!-- One row per store: the v-for div is "contents" so its cells sit in the grid -->
          <div class="grid grid-cols-[auto_1fr_1fr_1fr_1fr] items-center gap-x-3 gap-y-2 mt-3">
            <span class="text-sm text-slate-500">Magasin</span>
            <span class="text-sm text-slate-500">PVC</span>
            <span class="text-sm text-slate-500">Prix TTC</span>
            <span class="text-sm text-slate-500">Marge</span>
            <span class="text-sm text-slate-500">Taux</span>

            <div v-for="store in stores" :key="store.id" class="contents">
              <span class="font-medium">{{ store.name }}</span>
              <InputNumber
                :modelValue="recommendedPrices[store.id]"
                :aria-label="`PVC ${store.name}`"
                mode="currency"
                currency="EUR"
                locale="fr-FR"
                disabled
                fluid
              />
              <InputNumber
                v-model="form.prices[store.id]"
                :aria-label="`Prix TTC ${store.name}`"
                :inputClass="priceColorClass(store.id)"
                :invalid="submitAttempted && !form.prices[store.id]"
                mode="currency"
                currency="EUR"
                locale="fr-FR"
                :min="0.01"
                :step="0.1"
                fluid
              />
              <InputNumber
                :modelValue="marginAmount(store.id)"
                :aria-label="`Marge ${store.name}`"
                mode="currency"
                currency="EUR"
                locale="fr-FR"
                disabled
                fluid
              />
              <InputNumber
                :modelValue="marginRate(store.id)"
                :aria-label="`Taux ${store.name}`"
                :maxFractionDigits="1"
                suffix=" %"
                disabled
                fluid
              />
            </div>
          </div>
        </div>
        <!-- --------------------------------------------------------------- -->
        <!-- Deposit -->
        <template v-if="show('deposit_unit')">
          <div>
            <Divider />
            <div class="grid grid-cols-3 gap-3">
              <FloatLabel variant="on">
                <InputNumber
                  v-model="form.details.deposit.unit"
                  inputId="deposit-unit"
                  mode="currency"
                  currency="EUR"
                  locale="fr-FR"
                  :min="0.01"
                  fluid
                />
                <label for="deposit-unit">Consigne unité</label>
              </FloatLabel>
              <FloatLabel v-if="show('deposit_crate')" variant="on">
                <InputNumber
                  v-model="form.details.deposit.crate"
                  inputId="deposit-crate"
                  mode="currency"
                  currency="EUR"
                  locale="fr-FR"
                  :min="0.01"
                  fluid
                />
                <label for="deposit-crate">Consigne caisse</label>
              </FloatLabel>
              <FloatLabel v-if="show('deposit_packaging')" variant="on">
                <Select
                  inputId="deposit-packaging"
                  v-model="form.details.deposit.packaging"
                  :options="[6, 12, 20, 24]"
                  showClear
                  fluid
                />
                <label for="deposit-packaging">Conditionnement</label>
              </FloatLabel>
            </div>
          </div>
        </template>
        <!-- --------------------------------------------------------------- -->
      </template>
    </div>

    <template #footer>
      <Button label="Annuler" severity="secondary" @click="closeDialog" :disabled="saving" />
      <Button label="Créer" @click="submitArticle" :loading="saving" />
    </template>
  </Dialog>
</template>
