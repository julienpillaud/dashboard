import './assets/main.css'
import '@openvue/openicons/openicons.css'
import { definePreset } from '@openvue/themes'
import Aura from '@openvue/themes/aura'
import OpenVue from 'openvue/config'
import ToastService from 'openvue/toastservice'
import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ToastService)

const MyPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '{violet.50}',
      100: '{violet.100}',
      200: '{violet.200}',
      300: '{violet.300}',
      400: '{violet.400}',
      500: '{violet.500}',
      600: '{violet.600}',
      700: '{violet.700}',
      800: '{violet.800}',
      900: '{violet.900}',
      950: '{violet.950}',
    },
    // Compact form fields (Aura default: 0.5rem)
    formField: {
      paddingY: '0.375rem',
    },
  },
})

app.use(OpenVue, {
  theme: {
    preset: MyPreset,
    options: {
      darkModeSelector: false,
    },
  },
})

app.mount('#app')
