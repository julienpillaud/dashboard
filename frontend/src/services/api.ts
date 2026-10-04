// services/api.ts
import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

const api: AxiosInstance = axios.create({
  baseURL: '/api',
})

// Axios request config + a custom flag to remember "already replayed once"
type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean }

// The refresh call currently in progress, or null if there is none.
// Shared so that only ONE /auth/refresh is sent at a time
// (required by refresh token rotation).
let refreshPromise: Promise<unknown> | null = null

function refreshSession() {
  // Start a refresh only if none is already running
  if (!refreshPromise) {
    refreshPromise = api.post('/auth/refresh').finally(() => {
      // Runs on success AND failure: allow a new refresh next time
      refreshPromise = null
    })
  }
  // Everyone gets the same promise, so everyone waits for the same refresh
  return refreshPromise
}

api.interceptors.response.use(
  // Success: pass the response through untouched
  (response) => response,

  // Error: runs for every failed request
  async (error) => {
    const original = error.config as RetriableConfig | undefined

    // Nothing to replay
    if (!original) {
      return Promise.reject(error)
    }

    // error.response is undefined when the network is down, hence the "?."
    const isUnauthorized = error.response?.status === 401
    // Never refresh for /auth/* routes, otherwise we could loop forever
    const isAuthRoute = original.url?.startsWith('/auth/')

    // Not an expired session, or already replayed once: give up
    if (!isUnauthorized || isAuthRoute || original._retry) {
      return Promise.reject(error)
    }

    original._retry = true

    try {
      // Wait for new cookies (starts a refresh or joins the running one)
      await refreshSession()
    } catch (error) {
      console.error(error)
      // Refresh failed: the session is really dead
      useAuthStore().clear()
      router.push({ name: 'login' })
      return Promise.reject(error)
    }

    // Replay the original request with the new cookies.
    // It is outside the try/catch on purpose: if it fails (e.g. 500),
    // that must NOT log the user out.
    return api(original)
  },
)

export default api
