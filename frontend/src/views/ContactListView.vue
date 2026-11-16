<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppIcon from '@/components/common/AppIcon.vue'
import ContactTable from '@/components/contact/ContactTable.vue'
import ContactDetail from '@/components/contact/ContactDetail.vue'
import ContactFormDialog from '@/components/contact/ContactFormDialog.vue'
import ImportDialog from '@/components/contact/ImportDialog.vue'
import { useContactStore } from '@/stores/contactStore'
import { useBreakpoint } from '@/composables/useBreakpoint'
import { PAGE_SIZE_OPTIONS, SEARCH_DEBOUNCE } from '@/constants/contact'
import { buildPageList } from '@/utils/contact'
import { exportContacts, isMockMode, listContacts } from '@/api/contacts'
import { downloadBlob, filenameFromDisposition } from '@/utils/download'
import { buildContactsCsv, formatStamp } from '@/utils/excel'

const {
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
} = useContactStore()

const searchText = ref('')
const dialogVisible = ref(false)
const editingContact = ref(null)
const importVisible = ref(false)
const exportLoading = ref(false)
const searchInputRef = ref(null)
const formErrors = ref(null)
let searchTimer = null

const { isDesktop, isRail } = useBreakpoint()

const initialLoading = computed(() => !state.initialized && state.loading)
const isMac = computed(() => /Mac|iPhone|iPad/i.test(navigator.platform || ''))
const shortcutLabel = computed(() => (isMac.value ? '⌘K' : 'Ctrl K'))

// On narrower viewports, open detail drawer on demand rather than automatically on first load
if (!isDesktop.value) state.detailOpen = false

watch(isDesktop, (desktop) => {
  state.detailOpen = desktop
})

function focusSelectedRow() {
  nextTick(() => {
    const rows = document.querySelectorAll('.contact-table .el-table__row')
    const index = state.items.findIndex((item) => item.id === state.selectedId)
    rows[index]?.focus({ preventScroll: true })
  })
}

function closeDetailDrawer(restoreFocus = true) {
  state.detailOpen = false
  if (restoreFocus !== false) focusSelectedRow()
}

function closeDesktopDetail() {
  closeDetail()
  focusSelectedRow()
}

function trapDrawerFocus(event) {
  const card = document.querySelector('.detail-layer .detail-card')
  if (!card) return
  const focusables = [
    ...card.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
  ].filter((element) => !element.disabled && element.offsetParent !== null)
  if (!focusables.length) return
  const first = focusables[0]
  const last = focusables[focusables.length - 1]
  if (!card.contains(document.activeElement)) {
    event.preventDefault()
    first.focus()
    return
  }
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

function hasVisibleOverlay() {
  return [...document.querySelectorAll('.el-overlay')].some(
    (element) => getComputedStyle(element).display !== 'none'
  )
}

function handleKeydown(event) {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    if (hasVisibleOverlay() || (!isDesktop.value && state.detailOpen)) return
    event.preventDefault()
    searchInputRef.value?.focus()
    return
  }
  if (event.key === 'Escape') {
    if (hasVisibleOverlay()) return
    if (!isDesktop.value && state.detailOpen) closeDetailDrawer()
    return
  }
  if (event.key === 'Tab' && !isDesktop.value && state.detailOpen) {
    trapDrawerFocus(event)
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  clearTimeout(searchTimer)
})

watch(
  () => [state.page, state.keyword, state.group, state.favoriteOnly],
  () => {
    if (!isDesktop.value && state.detailOpen) closeDetailDrawer(false)
  }
)

watch(
  () => state.detailOpen,
  (open) => {
    if (!open || isDesktop.value) return
    nextTick(() => {
      document
        .querySelector('.detail-layer .detail-card')
        ?.focus({ preventScroll: true })
    })
  }
)

const canExport = computed(() => state.total > 0)

const groupValue = computed({
  get: () => state.group,
  set: (value) => setGroup(value || '')
})

const pageList = computed(() => buildPageList(state.page, pageCount.value))

watch(searchText, (value) => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => setKeyword(value), SEARCH_DEBOUNCE)
})

onMounted(async () => {
  searchText.value = state.keyword
  await init()
  if (state.selectedId && isDesktop.value) selectContact(state.selectedId)
})

function handleCheck(id) {
  toggleCheck(id)
}

function handleCheckAll(checked) {
  setChecksFor(
    state.items.map((item) => item.id),
    checked
  )
}

function openCreate() {
  editingContact.value = null
  formErrors.value = null
  dialogVisible.value = true
}

function openEdit(contact) {
  if (!contact) return
  editingContact.value = contact
  formErrors.value = null
  dialogVisible.value = true
}

async function handleSubmit(payload) {
  const result = await saveContact(payload, editingContact.value?.id)
  if (result?.ok) {
    dialogVisible.value = false
    formErrors.value = null
  } else {
    formErrors.value = result?.error?.details || null
  }
}

async function handleRemove(contact) {
  if (!contact) return
  try {
    await ElMessageBox.confirm(
      `确定删除「${contact.name}」吗？该联系人的全部联系方式将一并移除，且不可恢复。`,
      '删除联系人',
      {
        type: 'warning',
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--danger'
      }
    )
  } catch {
    return
  }
  await removeContact(contact.id)
}

async function handleBatchRemove() {
  if (!checkedCount.value) return
  const ids = [...state.checkedIds]
  try {
    await ElMessageBox.confirm(
      `已选择 ${ids.length} 位联系人。按现行接口契约将逐条调用删除接口，删除后不可恢复，是否继续？`,
      '批量删除',
      {
        type: 'warning',
        confirmButtonText: `删除 ${ids.length} 项`,
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--danger'
      }
    )
  } catch {
    return
  }
  await removeContacts(ids)
}

function handleImport() {
  importVisible.value = true
}

async function handleImported(result) {
  const hadFilter = hasActiveFilter.value
  await refresh()
  if (!result?.success_count || hadFilter) return
  await setPage(pageCount.value)
  const lastItem = state.items[state.items.length - 1]
  if (!lastItem) return
  if (isDesktop.value) selectContact(lastItem.id)
  else state.selectedId = lastItem.id
}

async function handleMoreCommand(command) {
  if (command === 'import') handleImport()
  else if (command === 'export') await handleExport()
}

async function handleExport() {
  if (!canExport.value || exportLoading.value) return
  const params = {
    keyword: state.keyword.trim() || undefined,
    group: state.group || undefined,
    is_favorite: state.favoriteOnly ? 'true' : undefined
  }

  if (isMockMode) {
    try {
      const data = await listContacts({ ...params, page: 1, page_size: 100 })
      const csv = buildContactsCsv(data.items)
      downloadBlob(
        new Blob([csv], { type: 'text/csv;charset=utf-8' }),
        `contacts_export_mock_${formatStamp()}.csv`
      )
      ElMessage.info('Mock 演示：已导出 CSV；连接后端后将导出 .xlsx')
    } catch (error) {
      if (!error?._notified) ElMessage.error(error?.message || '导出失败')
    }
    return
  }

  exportLoading.value = true
  try {
    const response = await exportContacts(params)
    const filename =
      filenameFromDisposition(response.headers['content-disposition']) ||
      `contacts_export_${formatStamp()}.xlsx`
    downloadBlob(response.data, filename)
  } catch {
    /* Error notifications are handled globally by Axios response interceptor */
  } finally {
    exportLoading.value = false
  }
}
</script>

<template>
  <div class="contact-page">
    <main class="card list-card">
      <div class="page-head">
        <div class="page-title">
          <h2>{{ pageTitle }}</h2>
          <p>共 {{ initialLoading ? '—' : state.total }} 位联系人，管理你的联系人信息</p>
        </div>
        <div class="page-actions">
          <el-button type="primary" @click="openCreate">
            <AppIcon name="plus" :size="15" />新增联系人
          </el-button>
          <el-button v-if="!isRail" @click="handleImport">
            <AppIcon name="upload" :size="15" />导入 Excel
          </el-button>
          <el-tooltip
            v-if="!isRail"
            :content="canExport ? `按当前筛选导出 ${state.total} 条` : '当前筛选无数据可导出'"
            placement="top"
            :show-after="300"
          >
            <span class="export-wrap">
              <el-button :loading="exportLoading" :disabled="!canExport" @click="handleExport">
                <AppIcon name="download" :size="15" />导出 Excel
              </el-button>
            </span>
          </el-tooltip>
          <el-dropdown
            v-if="isRail"
            trigger="click"
            placement="bottom-end"
            @command="handleMoreCommand"
          >
            <el-button class="more-button" aria-label="更多操作">
              <AppIcon name="more" :size="16" />
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="import">导入 Excel</el-dropdown-item>
                <el-dropdown-item command="export" :disabled="!canExport">
                  导出 Excel
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <div class="toolbar">
        <el-input
          ref="searchInputRef"
          v-model="searchText"
          class="search-input"
          placeholder="搜索姓名、电话号码、邮箱或备注..."
          clearable
        >
          <template #prefix>
            <AppIcon name="search" :size="15" />
          </template>
          <template #suffix>
            <span class="kbd-hint">{{ shortcutLabel }}</span>
          </template>
        </el-input>

        <div class="toolbar-spacer" />

        <span class="field-label">分组</span>
        <el-select v-model="groupValue" class="group-select" placeholder="全部">
          <el-option label="全部" value="" />
          <el-option
            v-for="group in state.groups"
            :key="group.name"
            :label="group.name"
            :value="group.name"
          />
        </el-select>

        <div class="favorite-filter">
          <el-switch
            :model-value="state.favoriteOnly"
            :width="36"
            @update:model-value="setFavoriteOnly"
          />
          <span class="switch-label" @click="setFavoriteOnly(!state.favoriteOnly)">
            仅显示收藏
          </span>
        </div>
      </div>

      <ContactTable
        :items="state.items"
        :loading="state.loading"
        :skeleton="initialLoading"
        :selected-id="state.selectedId"
        :checked-ids="state.checkedIds"
        :error="state.error"
        :has-filter="hasActiveFilter"
        @select="selectContact"
        @toggle-favorite="toggleFavorite"
        @edit="openEdit"
        @remove="handleRemove"
        @check="handleCheck"
        @check-all="handleCheckAll"
        @retry="fetchList"
      />

      <div class="table-foot">
        <span class="selected-count">已选择 <b>{{ checkedCount }}</b> 项</span>
        <el-button size="small" :disabled="!checkedCount" @click="handleBatchRemove">
          <AppIcon name="trash" :size="14" />批量删除
        </el-button>

        <div class="foot-spacer" />

        <span class="total">共 <b>{{ initialLoading ? '—' : state.total }}</b> 条</span>
        <el-select
          :model-value="state.pageSize"
          class="page-size"
          size="small"
          :disabled="initialLoading"
          @update:model-value="setPageSize"
        >
          <el-option
            v-for="size in PAGE_SIZE_OPTIONS"
            :key="size"
            :label="`${size} 条/页`"
            :value="size"
          />
        </el-select>

        <div class="pager">
          <button
            class="page-btn"
            type="button"
            :disabled="state.page <= 1 || initialLoading"
            aria-label="上一页"
            @click="setPage(state.page - 1)"
          >
            <AppIcon name="chevron-left" :size="13" />
          </button>
          <template v-for="(item, index) in pageList" :key="`${item}-${index}`">
            <span v-if="item === '...'" class="page-ellipsis">…</span>
            <button
              v-else
              class="page-btn"
              :class="{ 'is-active': item === state.page }"
              type="button"
              @click="setPage(item)"
            >
              {{ item }}
            </button>
          </template>
          <button
            class="page-btn"
            type="button"
            :disabled="state.page >= pageCount || initialLoading"
            aria-label="下一页"
            @click="setPage(state.page + 1)"
          >
            <AppIcon name="chevron-right" :size="13" />
          </button>
        </div>
      </div>
    </main>

    <ContactDetail
      v-if="state.detailOpen && isDesktop"
      :contact="selectedContact"
      :loading="initialLoading"
      @close="closeDesktopDetail"
      @edit="openEdit"
      @remove="handleRemove"
      @toggle-favorite="toggleFavorite"
    />

    <div v-if="state.detailOpen && !isDesktop" class="detail-layer">
      <div class="detail-scrim" @click="closeDetailDrawer" />
      <ContactDetail
        drawer
        :contact="selectedContact"
        :loading="initialLoading"
        @close="closeDetailDrawer"
        @edit="openEdit"
        @remove="handleRemove"
        @toggle-favorite="toggleFavorite"
      />
    </div>

    <ContactFormDialog
      v-model="dialogVisible"
      :contact="editingContact"
      :saving="state.saving"
      :server-errors="formErrors"
      @submit="handleSubmit"
    />

    <ImportDialog v-model="importVisible" @finished="handleImported" />
  </div>
</template>

<style scoped>
.contact-page {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  gap: 10px;
}

.list-card {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  padding: 22px 24px 0;
}

.page-head {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  flex: none;
}

.page-title h2 {
  margin: 0;
  font-size: 25px;
  font-weight: 600;
  line-height: 32px;
  letter-spacing: 0.4px;
  color: var(--color-ink);
}

.page-title p {
  margin: 6px 0 0;
  font-size: 13px;
  line-height: 18px;
  color: var(--color-ink-3);
}

.page-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
  padding-top: 4px;
  flex: none;
}

.page-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.more-button {
  width: 36px;
  padding: 0;
  justify-content: center;
}

.more-button :deep(.app-icon) {
  margin-right: 0;
}

.detail-layer {
  position: fixed;
  inset: 0;
  z-index: 40;
}

.detail-scrim {
  position: absolute;
  inset: 0;
  background: rgba(32, 44, 58, 0.3);
  backdrop-filter: blur(1px);
}

.export-wrap {
  display: inline-flex;
}

.toolbar {
  flex: none;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 30px;
  margin-bottom: 16px;
}

.search-input {
  width: 358px;
  flex: none;
}

.search-input :deep(.el-input__wrapper) {
  height: 36px;
  padding: 0 12px;
}

.search-input :deep(.el-input__prefix) {
  margin-right: 6px;
}

.kbd-hint {
  padding: 1px 5px;
  border: 1px solid #e6eaf0;
  border-radius: 4px;
  background: #fafbfd;
  color: #a4afbd;
  font-size: 11px;
  line-height: 14px;
  white-space: nowrap;
}

.toolbar-spacer {
  flex: 1;
}

.field-label {
  font-size: 13px;
  color: var(--color-ink-2);
  white-space: nowrap;
}

.group-select {
  width: 150px;
  flex: none;
}

.group-select :deep(.el-select__wrapper) {
  height: 36px;
  min-height: 36px;
}

.favorite-filter {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-left: 12px;
  white-space: nowrap;
}

.switch-label {
  font-size: 13px;
  color: var(--color-ink-2);
  cursor: pointer;
  user-select: none;
}

.table-foot {
  flex: none;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: var(--color-ink-3);
}

.selected-count b {
  color: var(--color-primary-strong);
  font-weight: 600;
}

.foot-spacer {
  flex: 1;
}

.total {
  color: var(--color-ink-3);
  white-space: nowrap;
}

.total b {
  color: var(--color-ink-2);
  font-weight: 600;
}

.table-foot :deep(.el-button) {
  margin-left: 0;
}

.page-size {
  width: 92px;
  flex: none;
}

.page-size :deep(.el-select__wrapper) {
  height: 32px;
  min-height: 32px;
  padding: 0 8px;
}

.pager {
  display: flex;
  align-items: center;
  gap: 6px;
}

.page-btn {
  min-width: 30px;
  height: 30px;
  padding: 0 6px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: var(--color-ink-3);
  font-size: 13px;
  display: grid;
  place-items: center;
  transition: background 0.16s, color 0.16s;
}

.page-btn :deep(.app-icon) {
  color: #9aa7b6;
}

.page-btn:hover:not(:disabled):not(.is-active) {
  background: #f0f3f7;
}

.page-btn.is-active {
  background: var(--color-primary);
  color: #fff;
}

.page-btn.is-active :deep(.app-icon) {
  color: #fff;
}

.page-btn:disabled {
  color: #c8d0da;
  cursor: not-allowed;
}

.page-btn:disabled :deep(.app-icon) {
  color: #c8d0da;
}

.page-ellipsis {
  color: var(--color-ink-4);
}

@media (max-width: 1279px) {
  .list-card {
    padding: 20px 20px 0;
  }
}

@media (max-width: 1023px) {
  .list-card {
    padding: 16px 16px 0;
  }

  .page-title h2 {
    font-size: 20px;
    line-height: 26px;
  }

  .page-title p {
    font-size: 12.5px;
  }

  .page-actions {
    gap: 8px;
    padding-top: 1px;
  }

  .page-actions :deep(.el-button) {
    height: 34px;
    padding: 0 12px;
    font-size: 13px;
  }

  .more-button {
    width: 34px;
  }

  .toolbar {
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 14px;
    margin-bottom: 14px;
  }

  .search-input {
    width: 100%;
  }

  .toolbar-spacer,
  .field-label {
    display: none;
  }

  .kbd-hint {
    display: none;
  }

  .group-select {
    width: 132px;
  }

  .favorite-filter {
    margin-left: auto;
    padding-left: 0;
    gap: 8px;
  }

  .table-foot {
    height: 52px;
  }

  .page-size {
    display: none;
  }
}
</style>
