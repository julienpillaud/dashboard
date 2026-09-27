import axios, { type AxiosInstance } from 'axios'

const api: AxiosInstance = axios.create({
  baseURL: '/api',
})

export default api
