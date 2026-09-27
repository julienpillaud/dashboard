<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import api from '@/services/api'
import { useStores } from '@/composables/useStores'
import { useCategories } from '@/composables/useCategories'
import { useTaxes } from '@/composables/useTaxes'
import { useOrigins } from '@/composables/useOrigins'
import Dialog from 'openvue/dialog'
import Button from 'openvue/button'
import FloatLabel from 'openvue/floatlabel'
import InputText from 'openvue/inputtext'
import Select from 'openvue/select'
import InputNumber from 'openvue/inputnumber'
import Divider from 'openvue/divider'
import type { CategoryFields } from '@/types/categories'
import type { ArticleForm } from '../types/forms'
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
  price: null,
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
const recommendedPrice = ref(null)
const submitAttempted = ref<boolean>(false)
// =============================================================================
// Computed
const selectedCategory = computed(() =>
  categories.value.find((c) => c.id === selectedCategoryId.value),
)

const taxOptions = computed(() => taxes.value.map((t) => ({ ...t, label: `${t.rate} %` })))

const pvcSourcesFilledCount = computed(
  () =>
    [selectedCategoryId.value, form.value.total_cost, form.value.tax_rate].filter((v) => v != null)
      .length,
)

const pvcSourcesIncomplete = computed(
  () => pvcSourcesFilledCount.value > 0 && pvcSourcesFilledCount.value < 3,
)

const priceDiff = computed(() => {
  if (!form.value.price || !recommendedPrice.value) return 0
  return form.value.price - recommendedPrice.value
})

const priceColorClass = computed(() => {
  if (priceDiff.value < 0) return 'text-red-700!'
  if (priceDiff.value > 0) return 'text-green-700!'
  return ''
})

const taxFactor = computed(() => {
  const { tax_rate } = form.value
  if (tax_rate == null) return null
  return 1 + tax_rate / 100
})

const marginAmount = computed(() => {
  const { total_cost, price } = form.value
  if (total_cost == null || price == null || taxFactor.value == null) return null
  return price / taxFactor.value - total_cost
})

const marginRate = computed(() => {
  const { price } = form.value
  if (marginAmount.value == null || !price || taxFactor.value == null) return null
  return (marginAmount.value / (price / taxFactor.value)) * 100
})

const isFormValid = computed(() => {
  return (
    !!form.value.name &&
    !!selectedCategoryId.value &&
    !!form.value.total_cost &&
    !!form.value.tax_rate &&
    !!form.value.price
  )
})
// =============================================================================
// Functions
const show = (field: keyof CategoryFields) => selectedCategory.value?.fields?.[field] === true

const resetPrices = () => {
  recommendedPrice.value = null
  form.value.price = null
}

const fetchRecommendedPrice = async () => {
  const response = await api.post('/pricing/recommended-price', {
    store_id: stores.value[0]!.id,
    category_id: selectedCategoryId.value,
    total_cost: form.value.total_cost,
    tax_rate: form.value.tax_rate,
  })
  recommendedPrice.value = response.data.recommended_price
  form.value.price = response.data.recommended_price
}

const closeDialog = () => {
  emit('update:visible', false)
}

const resetForm = () => {
  form.value = structuredClone(INITIAL_FORM)
  selectedCategoryId.value = null
  submitAttempted.value = false
  recommendedPrice.value = null
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

  await api.post('/articles', {
    ...form.value,
    category: selectedCategory.value?.name,
    details: buildDetails(),
  })

  emit('created')
}
// =============================================================================
// Watchers
watch([selectedCategoryId, () => form.value.total_cost, () => form.value.tax_rate], () => {
  if (pvcSourcesFilledCount.value < 3) {
    resetPrices()
    return
  }
  fetchRecommendedPrice()
})
// =============================================================================
</script>

<template>
  <Dialog
    :visible="props.visible"
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
              <InputNumber id="volume-value" v-model="form.details.volume.value" fluid />
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
              id="alcohol_by_volume"
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
            <FloatLabel variant="on">
              <InputNumber
                id="recommended_price"
                v-model="recommendedPrice"
                mode="currency"
                currency="EUR"
                locale="fr-FR"
                :invalid="pvcSourcesIncomplete"
                disabled
                fluid
              />
              <label for="recommended_price">PVC</label>
            </FloatLabel>
            <FloatLabel variant="on">
              <InputNumber
                id="price"
                v-model="form.price"
                :inputClass="priceColorClass"
                :invalid="submitAttempted && !form.price"
                mode="currency"
                currency="EUR"
                locale="fr-FR"
                :min="0.01"
                :step="0.1"
                fluid
              />
              <label for="price">Prix TTC</label>
            </FloatLabel>
            <FloatLabel variant="on">
              <InputNumber
                id="margin-amount"
                v-model="marginAmount"
                mode="currency"
                currency="EUR"
                locale="fr-FR"
                fluid
                disabled
              />
              <label for="margin-amount">Marge</label>
            </FloatLabel>
            <FloatLabel variant="on">
              <InputNumber
                id="margin-rate"
                v-model="marginRate"
                :maxFractionDigits="1"
                suffix=" %"
                fluid
                disabled
              />
              <label for="margin-rate">Taux</label>
            </FloatLabel>
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
      <Button label="Annuler" severity="secondary" @click="closeDialog" />
      <Button label="Créer" @click="submitArticle" />
    </template>
  </Dialog>
</template>
