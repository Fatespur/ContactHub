import { computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import * as api from '@/api/contacts'
import { buildGroupStats, resolveSelectedId } from '@/utils/contact'
import { DEFAULT_PAGE_SIZE } from '@/constants/contact'

const state = reactive({
  items: [],
  total: 0,
  loading: false,
  initialized: false,
  error: '',
  page: 1,
  pageSize: DEFAULT_PAGE_SIZE,
  keyword: '',
  group: '',
  favoriteOnly: false,
  selectedId: null,
  detailOpen: true,
  checkedIds: [],
  groups: [],
  groupTotal: 0,
  statsLoading: false,
  saving: false,
  removing: false
})

const pageCount = computed(() => Math.max(1, Math.ceil(state.total / state.pageSize)))
const checkedCount = computed(() => state.checkedIds.length)
const selectedContact = computed(
  () => state.items.find((item) => item.id === state.selectedId) || null
)
const hasActiveFilter = computed(
  () => Boolean(state.keyword || state.group || state.favoriteOnly)
)
const pageTitle = computed(() => {
  if (state.favoriteOnly) return '我的收藏'
  if (state.group) return `分组：${state.group}`
  return '全部联系人'
})

function buildQuery() {
  return {
    page: state.page,
    page_size: state.pageSize,
    keyword: state.keyword.trim() || undefined,
    group: state.group || undefined,
    is_favorite: state.favoriteOnly ? 'true' : undefined
  }
}

function notifyError(error, fallback) {
  if (!error?._notified) {
    ElMessage.error(error?.message || fallback)
  }
}

async function fetchList() {
  state.loading = true
  state.error = ''
  try {
    const data = await api.listContacts(buildQuery())
    state.items = data.items
    state.total = data.total

    const maxPage = Math.max(1, Math.ceil(state.total / state.pageSize))
    if (state.page > maxPage) {
      state.page = maxPage
      state.loading = false
      return fetchList()
    }

    state.selectedId = resolveSelectedId(state.items, state.selectedId)
  } catch (error) {
    state.error = error?.message || '联系人加载失败'
    state.items = []
    state.total = 0
    notifyError(error, '联系人加载失败')
  } finally {
    state.loading = false
    state.initialized = true
  }
}

async function loadStats() {
  state.statsLoading = true
  try {
    const data = await api.listContacts({ page: 1, page_size: 100 })
    state.groups = buildGroupStats(data.items)
    state.groupTotal = data.total
  } catch (error) {
    notifyError(error, '分组统计加载失败')
  } finally {
    state.statsLoading = false
  }
}

async function init() {
  await Promise.all([fetchList(), loadStats()])
}

async function refresh() {
  await Promise.all([fetchList(), loadStats()])
}

function setKeyword(value) {
  if (state.keyword === value) return Promise.resolve()
  state.keyword = value
  state.page = 1
  state.checkedIds = []
  return fetchList()
}

function setGroup(group) {
  state.group = group
  state.page = 1
  state.checkedIds = []
  return fetchList()
}

function setFavoriteOnly(value) {
  state.favoriteOnly = value
  state.page = 1
  state.checkedIds = []
  return fetchList()
}

function showAll() {
  state.keyword = ''
  state.group = ''
  state.favoriteOnly = false
  state.page = 1
  state.checkedIds = []
  return fetchList()
}

function showFavorites() {
  state.keyword = ''
  state.group = ''
  state.favoriteOnly = true
  state.page = 1
  state.checkedIds = []
  return fetchList()
}

function setPage(page) {
  const target = Math.min(Math.max(1, page), pageCount.value)
  if (target === state.page) return Promise.resolve()
  state.page = target
  return fetchList()
}

function setPageSize(size) {
  state.pageSize = size
  state.page = 1
  return fetchList()
}

function selectContact(id) {
  state.selectedId = id
  state.detailOpen = true
}

function closeDetail() {
  state.detailOpen = false
}

function toggleCheck(id) {
  state.checkedIds = state.checkedIds.includes(id)
    ? state.checkedIds.filter((value) => value !== id)
    : [...state.checkedIds, id]
}

function setChecksFor(ids, checked) {
  const next = new Set(state.checkedIds)
  ids.forEach((id) => {
    if (checked) next.add(id)
    else next.delete(id)
  })
  state.checkedIds = [...next]
}

function clearChecks() {
  state.checkedIds = []
}

async function toggleFavorite(contact) {
  const target = state.items.find((item) => item.id === contact.id)
  if (!target) return
  const previous = target.is_favorite
  target.is_favorite = !previous
  try {
    const result = await api.updateFavorite(contact.id, target.is_favorite)
    target.is_favorite = result.is_favorite
    if (state.favoriteOnly) await fetchList()
  } catch (error) {
    target.is_favorite = previous
    notifyError(error, '收藏状态更新失败')
  }
}

async function saveContact(payload, id) {
  state.saving = true
  try {
    if (id) {
      await api.updateContact(id, payload)
      await refresh()
      if (state.items.some((item) => item.id === id)) {
        state.selectedId = id
        state.detailOpen = true
      }
      ElMessage.success('联系人已更新')
    } else {
      const { id: newId } = await api.createContact(payload)
      state.keyword = ''
      state.group = ''
      state.favoriteOnly = false
      await loadStats()
      state.page = Math.max(1, Math.ceil(state.groupTotal / state.pageSize))
      await fetchList()
      if (state.items.some((item) => item.id === newId)) {
        state.selectedId = newId
        state.detailOpen = true
      }
      ElMessage.success('联系人已创建')
    }
    return { ok: true }
  } catch (error) {
    notifyError(error, '保存失败')
    return { ok: false, error }
  } finally {
    state.saving = false
  }
}

async function removeContact(id) {
  state.removing = true
  try {
    await api.deleteContact(id)
    state.checkedIds = state.checkedIds.filter((value) => value !== id)
    if (state.selectedId === id) state.selectedId = null
    await refresh()
    ElMessage.success('联系人已删除')
    return true
  } catch (error) {
    notifyError(error, '删除失败')
    return false
  } finally {
    state.removing = false
  }
}

async function removeContacts(ids) {
  if (!ids.length) return { success: 0, failed: 0 }
  state.removing = true
  let success = 0
  let failed = 0
  let firstError = null
  try {
    for (const id of ids) {
      try {
        await api.deleteContact(id)
        success += 1
        state.checkedIds = state.checkedIds.filter((value) => value !== id)
        if (state.selectedId === id) state.selectedId = null
      } catch (error) {
        failed += 1
        firstError = firstError || error
      }
    }
    await refresh()
    if (success > 0) ElMessage.success(`已删除 ${success} 位联系人`)
    if (failed > 0) {
      ElMessage.warning(`${failed} 位联系人删除失败：${firstError?.message || '请稍后重试'}`)
    }
    return { success, failed }
  } finally {
    state.removing = false
  }
}

export function useContactStore() {
  return {
    state,
    pageCount,
    checkedCount,
    selectedContact,
    hasActiveFilter,
    pageTitle,
    init,
    refresh,
    fetchList,
    setKeyword,
    setGroup,
    setFavoriteOnly,
    showAll,
    showFavorites,
    setPage,
    setPageSize,
    selectContact,
    closeDetail,
    toggleCheck,
    setChecksFor,
    clearChecks,
    toggleFavorite,
    saveContact,
    removeContact,
    removeContacts
  }
}
