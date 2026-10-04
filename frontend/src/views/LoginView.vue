<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import InputText from 'openvue/inputtext'
import Password from 'openvue/password'
import Button from 'openvue/button'
import Message from 'openvue/message'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push({ name: 'articles' })
  } catch (e) {
    console.error(e)
    error.value = 'Identifiants invalides'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex justify-center items-center min-h-screen">
    <form class="flex flex-col gap-4 w-sm" @submit.prevent="submit">
      <InputText
        v-model="email"
        type="email"
        placeholder="Email"
        autocomplete="username"
        required
      />
      <Password
        v-model="password"
        placeholder="Mot de passe"
        :feedback="false"
        toggleMask
        fluid
        autocomplete="current-password"
        required
      />
      <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>
      <Button type="submit" label="Se connecter" :loading="loading" />
    </form>
  </div>
</template>
