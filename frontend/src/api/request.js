import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  // Local development uses Vite proxy (/api/v1); specify VITE_API_BASE_URL when deploying to a separate domain.
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000
})

service.interceptors.response.use(
  (response) => {
    const { config, data } = response
    if (config.responseType === 'blob') return response

    if (data && typeof data === 'object' && 'code' in data) {
      if (data.code >= 200 && data.code < 300) return data.data

      const error = new Error(data.message || '请求失败')
      error.code = data.code
      error.errorCode = data.error_code || ''
      error.details = data.details ?? null
      if (!config.silent) {
        ElMessage.error(error.message)
        error._notified = true
      }
      return Promise.reject(error)
    }

    return data
  },
  async (error) => {
    const config = error.config || {}
    if (error.code === 'ERR_CANCELED' || error.name === 'CanceledError' || error.name === 'AbortError') {
      const aborted = new Error('已取消')
      aborted.name = 'AbortError'
      aborted._notified = true
      return Promise.reject(aborted)
    }
    let message = '网络异常，请确认后端服务已启动'

    if (error.response) {
      const body = error.response.data
      if (body instanceof Blob) {
        try {
          const parsed = JSON.parse(await body.text())
          message = parsed.message || message
        } catch {
          message = `请求失败（${error.response.status}）`
        }
      } else if (body?.message) {
        message = body.message
      } else {
        message = `请求失败（${error.response.status}）`
      }
    } else if (error.code === 'ECONNABORTED') {
      message = '请求超时，请稍后重试'
    }

    const normalized = new Error(message)
    normalized.code = error.response?.status ?? 0
    normalized.details = error.response?.data?.details ?? null
    if (!config.silent) {
      ElMessage.error(message)
      normalized._notified = true
    }
    return Promise.reject(normalized)
  }
)

export default service
