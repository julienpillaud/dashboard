<script setup lang="ts">
import Button from 'openvue/button'
</script>

<template>
  <div class="flex flex-col justify-center items-center min-h-screen gap-4">
    <h1 class="text-2xl font-semibold">Page introuvable</h1>
    <RouterLink :to="{ name: 'articles' }">
      <Button label="Retour" />
    </RouterLink>
  </div>
</template>
