<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AppIcon from '@/components/common/AppIcon.vue'
import ContactAvatar from './ContactAvatar.vue'
import GroupTag from './GroupTag.vue'
import StarToggle from './StarToggle.vue'
import ListSkeleton from './ListSkeleton.vue'
import { primaryOf, otherContact } from '@/utils/contact'
import { useBreakpoint } from '@/composables/useBreakpoint'

const props = defineProps({
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  skeleton: { type: Boolean, default: false },
  selectedId: { type: [Number, String], default: null },
  checkedIds: { type: Array, default: () => [] },
  error: { type: String, default: '' },
  hasFilter: { type: Boolean, default: false }
})

const emit = defineEmits([
  'select',
  'toggle-favorite',
  'edit',
  'remove',
  'check',
  'check-all',
  'retry'
])

const allChecked = computed(
  () => props.items.length > 0 && props.items.every((item) => props.checkedIds.includes(item.id))
)
const indeterminate = computed(() => {
  const count = props.items.filter((item) => props.checkedIds.includes(item.id)).length
  return count > 0 && count < props.items.length
})

function phoneOf(row) {
  return primaryOf(row.phones)
}

function otherOf(row) {
  return otherContact(row)
}

function rowClassName({ row }) {
  return row.id === props.selectedId ? 'is-preview' : ''
}

function onRowClick(row) {
  emit('select', row.id)
}

function onCheck(row) {
  emit('check', row.id)
}

function onCheckAll(checked) {
  emit('check-all', checked)
}

const regionRef = ref(null)
const tableRef = ref(null)
const sortOrder = ref('none')
let resizeObserver = null
let lastWidth = 0

const { isRail } = useBreakpoint()

watch(isRail, () => {
  nextTick(() => tableRef.value?.doLayout())
  applyRowA11y()
})

watch(
  () => [props.items, props.selectedId],
  () => applyRowA11y(),
  { flush: 'post' }
)

function syncSortAria() {
  nextTick(() => {
    setTimeout(() => {
      regionRef.value
        ?.querySelector('th.col-name')
        ?.setAttribute('aria-sort', sortOrder.value)
    }, 80)
  })
}

function applyRowA11y() {
  nextTick(() => {
    const rows = regionRef.value?.querySelectorAll('.el-table__row')
    if (!rows) return
    rows.forEach((row, index) => {
      const item = props.items[index]
      if (!item) return
      row.setAttribute('tabindex', '0')
      row.setAttribute('aria-label', `查看 ${item.name} 的详情`)
      if (item.id === props.selectedId) row.setAttribute('aria-current', 'true')
      else row.removeAttribute('aria-current')
    })
    regionRef.value
      ?.querySelector('th.col-name')
      ?.setAttribute('aria-sort', sortOrder.value)
    syncSortAria()
  })
}

function onRegionKeydown(event) {
  if (event.key !== 'Enter' && event.key !== ' ') return
  if (event.target.closest('input, textarea, button, a, .el-checkbox')) return
  const row = event.target.closest('.el-table__row')
  if (!row) return
  const rows = [...regionRef.value.querySelectorAll('.el-table__row')]
  const item = props.items[rows.indexOf(row)]
  if (!item) return
  event.preventDefault()
  emit('select', item.id)
}

function onSortChange({ order }) {
  sortOrder.value = order || 'none'
  syncSortAria()
}

onMounted(() => {
  applyRowA11y()
  if (typeof ResizeObserver === 'undefined') return
  resizeObserver = new ResizeObserver((entries) => {
    const width = Math.round(entries[0].contentRect.width)
    if (width === lastWidth) return
    lastWidth = width
    tableRef.value?.doLayout()
  })
  resizeObserver.observe(regionRef.value)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  resizeObserver = null
})
</script>

<template>
  <div
    ref="regionRef"
    class="table-region"
    :aria-busy="loading ? 'true' : 'false'"
    @keydown="onRegionKeydown"
  >
    <ListSkeleton v-if="skeleton" :compact="isRail" />
    <el-table
      v-else
      ref="tableRef"
      v-loading="loading"
      class="contact-table"
      :data="items"
      height="100%"
      row-key="id"
      :row-class-name="rowClassName"
      :show-overflow-tooltip="false"
      @row-click="onRowClick"
      @sort-change="onSortChange"
    >
      <el-table-column
        :width="isRail ? 30 : 32"
        class-name="col-check"
        header-class-name="col-check"
      >
        <template #header>
          <span class="check-wrap" @click.stop>
            <el-checkbox
              :model-value="allChecked"
              :indeterminate="indeterminate"
              :disabled="!items.length"
              aria-label="全选当前页"
              @change="onCheckAll"
            />
          </span>
        </template>
        <template #default="{ row }">
          <span class="check-wrap" @click.stop>
            <el-checkbox
              :model-value="checkedIds.includes(row.id)"
              :aria-label="`选择 ${row.name}`"
              @change="onCheck(row)"
            />
          </span>
        </template>
      </el-table-column>

      <el-table-column
        prop="name"
        :width="isRail ? 116 : 120"
        sortable
        class-name="col-name"
        header-class-name="col-name"
      >
        <template #header>
          <el-tooltip content="仅对当前页排序" placement="top" :show-after="300">
            <span class="th-label">姓名</span>
          </el-tooltip>
        </template>
        <template #default="{ row }">
          <div class="name-cell">
            <ContactAvatar :name="row.name" :size="isRail ? 28 : 30" />
            <span class="name-text">{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="分组" :width="isRail ? 60 : 66">
        <template #default="{ row }">
          <GroupTag v-if="row.group" :text="row.group" />
          <span v-else class="dash">-</span>
        </template>
      </el-table-column>

      <el-table-column
        label="主要联系方式"
        :width="isRail ? undefined : 134"
        :min-width="isRail ? 148 : undefined"
      >
        <template #default="{ row }">
          <div v-if="phoneOf(row)" class="contact-cell" :title="phoneOf(row).number">
            <AppIcon name="phone" :size="15" />
            <span>{{ phoneOf(row).number }}</span>
          </div>
          <span v-else class="dash">-</span>
        </template>
      </el-table-column>

      <el-table-column v-if="!isRail" label="其他联系方式" min-width="168">
        <template #default="{ row }">
          <div v-if="otherOf(row)" class="contact-cell" :title="otherOf(row).text">
            <AppIcon :name="otherOf(row).icon" :size="15" />
            <span>{{ otherOf(row).text }}</span>
          </div>
          <span v-else class="dash">-</span>
        </template>
      </el-table-column>

      <el-table-column v-if="!isRail" label="备注" width="70">
        <template #default="{ row }">
          <span v-if="row.notes" class="notes-cell" :title="row.notes">{{ row.notes }}</span>
          <span v-else class="dash">-</span>
        </template>
      </el-table-column>

      <el-table-column label="收藏" :width="isRail ? 38 : 44">
        <template #default="{ row }">
          <span class="star-cell" @click.stop>
            <StarToggle
              :active="row.is_favorite"
              :size="16"
              @toggle="emit('toggle-favorite', row)"
            />
          </span>
        </template>
      </el-table-column>

      <el-table-column label="操作" :width="isRail ? 54 : 58">
        <template #default="{ row }">
          <div class="op-cell" @click.stop>
            <button class="icon-btn" type="button" title="编辑" @click="emit('edit', row)">
              <AppIcon name="edit" :size="15" />
            </button>
            <button
              class="icon-btn is-danger"
              type="button"
              title="删除"
              @click="emit('remove', row)"
            >
              <AppIcon name="trash" :size="15" />
            </button>
          </div>
        </template>
      </el-table-column>

      <template #empty>
        <div class="table-empty">
          <AppIcon :name="error ? 'alert' : 'inbox'" :size="34" />
          <strong>{{ error ? '联系人加载失败' : hasFilter ? '没有找到匹配的联系人' : '还没有联系人' }}</strong>
          <p>
            {{
              error
                ? error
                : hasFilter
                  ? '试试更换关键词、分组或收藏筛选'
                  : '点击右上角「新增联系人」开始录入'
            }}
          </p>
          <el-button v-if="error" size="small" @click="emit('retry')">
            <AppIcon name="refresh" :size="14" />重试
          </el-button>
        </div>
      </template>
    </el-table>
  </div>
</template>

<style scoped>
.table-region {
  flex: 1;
  min-height: 0;
}

.check-wrap {
  display: inline-flex;
  align-items: center;
}

.th-label {
  cursor: pointer;
  user-select: none;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.name-text {
  font-size: 14px;
  color: #2b3440;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.contact-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  font-size: 13px;
  color: #59687a;
}

.contact-cell :deep(.app-icon) {
  color: #8b98a8;
}

.contact-cell span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-variant-numeric: tabular-nums;
}

.notes-cell {
  display: block;
  font-size: 13px;
  color: #6b7785;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dash {
  color: #aab4c0;
  font-size: 13px;
}

.star-cell {
  display: inline-flex;
}

.op-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.icon-btn {
  width: 24px;
  height: 24px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  display: grid;
  place-items: center;
  color: #a3aeb9;
  transition: color 0.16s, background 0.16s;
}

.icon-btn:hover {
  color: var(--color-primary);
  background: #eef3f8;
}

.icon-btn.is-danger:hover {
  color: #c25f5b;
  background: #fcf0ef;
}

.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 64px 0;
  color: var(--color-ink-4);
  font-size: 13px;
}

.table-empty :deep(.app-icon) {
  color: #c3ccd6;
}

.table-empty strong {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-ink-2);
}

.table-empty p {
  margin: 0 0 6px;
  color: var(--color-ink-4);
}

/* Align el-table appearance with design specs */
.contact-table {
  --el-table-border-color: transparent;
  --el-table-header-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-row-hover-bg-color: #f7f9fc;
  --el-table-header-text-color: #37455a;
  --el-table-text-color: var(--color-ink-2);
  font-size: 13px;
}

.contact-table :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.contact-table :deep(th.el-table__cell) {
  height: 32px;
  padding: 0;
  font-size: 13px;
  font-weight: 600;
  border-bottom: 1px solid var(--color-line);
  background: transparent;
}

.contact-table :deep(td.el-table__cell) {
  padding: 0;
  border-bottom: 1px solid #f3f5f8;
}

.contact-table :deep(.el-table__row) {
  height: 58px;
}

.contact-table :deep(.el-table__row:focus-visible) {
  outline: 2px solid rgba(104, 131, 160, 0.45);
  outline-offset: -2px;
}

.contact-table :deep(.cell) {
  padding: 0 10px 0 0;
  line-height: 20px;
}

.contact-table :deep(.col-check .cell) {
  padding: 0;
}

.contact-table :deep(.el-table__row.is-preview > td.el-table__cell) {
  background: var(--color-primary-soft);
}

.contact-table :deep(.el-table__row.is-preview:hover > td.el-table__cell) {
  background: var(--color-primary-soft);
}

.contact-table :deep(.el-table__header-wrapper th:last-child .cell),
.contact-table :deep(.el-table__body td:last-child .cell) {
  padding-right: 0;
}

.contact-table :deep(.caret-wrapper) {
  width: 14px;
  height: 20px;
}

.contact-table :deep(.sort-caret) {
  border-width: 4px;
}

.contact-table :deep(.sort-caret.ascending) {
  top: 3px;
}

.contact-table :deep(.sort-caret.descending) {
  bottom: 3px;
}

.contact-table :deep(.el-table__empty-block) {
  min-height: 320px;
}

.contact-table :deep(.el-table__empty-text) {
  width: 100%;
  line-height: 1.5;
}

.contact-table :deep(.el-loading-mask) {
  background: rgba(255, 255, 255, 0.72);
}

@media (max-width: 1023px) {
  .contact-table :deep(.el-table__row) {
    height: 54px;
  }

  .contact-table :deep(th.el-table__cell) {
    height: 30px;
    font-size: 12.5px;
  }

  .contact-table :deep(.cell) {
    padding-right: 8px;
  }

  .contact-table :deep(.caret-wrapper) {
    width: 12px;
  }
}
</style>
