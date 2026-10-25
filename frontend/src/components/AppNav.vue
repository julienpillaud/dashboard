<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()

const links = [
  { name: 'articles', label: 'Articles' },
  { name: 'inventories', label: 'Inventaires' },
]
</script>

<template>
  <nav class="grid grid-cols-[1fr_auto_1fr] items-center bg-slate-100 shadow-sm px-6 h-16">
    <div class="flex gap-1">
      <RouterLink
        v-for="link in links"
        :key="link.name"
        :to="{ name: link.name }"
        class="px-3 py-1.5 rounded-md text-sm font-medium"
        :class="
          route.name === link.name
            ? 'bg-white text-violet-700 shadow-sm'
            : 'text-slate-600 hover:bg-slate-200'
        "
      >
        {{ link.label }}
      </RouterLink>
    </div>
    <div>
      <slot name="center" />
    </div>
    <div class="flex justify-end gap-2">
      <slot name="actions" />
    </div>
  </nav>
</template>
