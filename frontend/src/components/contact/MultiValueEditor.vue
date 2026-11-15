<script setup>
import { computed } from 'vue'
import AppIcon from '@/components/common/AppIcon.vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  title: { type: String, required: true },
  icon: { type: String, default: 'tag' },
  type: { type: String, required: true },
  labelOptions: { type: Array, default: () => [] },
  placeholder: { type: String, default: '' },
  errors: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue'])

const isSocial = computed(() => props.type === 'social')
const canPrimary = computed(() => !isSocial.value)
const labelKey = computed(() => (isSocial.value ? 'platform' : 'label'))
const valueKey = computed(
  () =>
    ({
      phone: 'number',
      email: 'email',
      address: 'address',
      social: 'account'
    })[props.type]
)

const rows = computed(() => props.modelValue || [])

const invalidIndexes = computed(() => {
  const indexes = new Set()
  props.errors.forEach((message) => {
    const match = /第\s*(\d+)\s*项/.exec(message)
    if (match) indexes.add(Number(match[1]) - 1)
  })
  return indexes
})

function createEmptyRow() {
  const option = props.labelOptions[0] || '其他'
  if (isSocial.value) return { platform: option, account: '' }
  return { label: option, [valueKey.value]: '', is_primary: false }
}

function patch(index, key, value) {
  const next = rows.value.map((row, rowIndex) =>
    rowIndex === index ? { ...row, [key]: value } : row
  )
  emit('update:modelValue', next)
}

function addRow() {
  const next = [...rows.value, createEmptyRow()]
  if (canPrimary.value && !next.some((row) => row.is_primary)) {
    next[next.length - 1].is_primary = true
  }
  emit('update:modelValue', next)
}

function removeRow(index) {
  const next = rows.value.filter((_, rowIndex) => rowIndex !== index)
  if (canPrimary.value && next.length && !next.some((row) => row.is_primary)) {
    next[0].is_primary = true
  }
  emit('update:modelValue', next)
}

function setPrimary(index) {
  const next = rows.value.map((row, rowIndex) => ({
    ...row,
    is_primary: rowIndex === index
  }))
  emit('update:modelValue', next)
}
</script>

<template>
  <div class="value-editor" :class="{ 'has-error': errors.length > 0 }">
    <div class="editor-head">
      <div class="editor-title">
        <AppIcon :name="icon" :size="15" />
        <span>{{ title }}</span>
        <span class="count">({{ rows.length }})</span>
      </div>
      <button class="add-row" type="button" @click="addRow">
        <AppIcon name="plus" :size="13" />添加
      </button>
    </div>

    <div class="editor-rows">
      <div
        v-for="(row, index) in rows"
        :key="`${type}-${index}`"
        class="editor-row"
        :class="{ 'is-invalid': invalidIndexes.has(index) }"
      >
        <el-select
          class="row-label"
          :model-value="row[labelKey]"
          filterable
          allow-create
          default-first-option
          :placeholder="isSocial ? '平台' : '标签'"
          @update:model-value="(value) => patch(index, labelKey, value)"
        >
          <el-option v-for="option in labelOptions" :key="option" :label="option" :value="option" />
        </el-select>

        <el-input
          class="row-value"
          :model-value="row[valueKey]"
          :placeholder="placeholder"
          maxlength="120"
          @update:model-value="(value) => patch(index, valueKey, value)"
        />

        <button
          v-if="canPrimary"
          class="primary-toggle"
          :class="{ 'is-primary': row.is_primary }"
          type="button"
          :aria-pressed="row.is_primary ? 'true' : 'false'"
          @click="setPrimary(index)"
        >
          <span class="dot" />{{ row.is_primary ? '主要' : '设为主要' }}
        </button>
        <span v-else class="primary-spacer" />

        <button
          class="row-remove"
          type="button"
          title="删除此项"
          :disabled="rows.length === 1"
          @click="removeRow(index)"
        >
          <AppIcon name="close" :size="13" />
        </button>
      </div>
    </div>
    <div v-if="errors.length" class="editor-errors">
      <p v-for="(message, index) in errors" :key="index" class="editor-error">{{ message }}</p>
    </div>
  </div>
</template>

<style scoped>
.value-editor {
  border: 1px solid var(--color-line);
  border-radius: 10px;
  padding: 14px;
  background: #fdfefe;
}

.value-editor.has-error {
  border-color: #e8c9c7;
}

.editor-row.is-invalid :deep(.el-input__wrapper),
.editor-row.is-invalid :deep(.el-select__wrapper) {
  box-shadow: 0 0 0 1px var(--color-danger) inset;
}

.editor-errors {
  margin-top: 9px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.editor-error {
  margin: 0;
  font-size: 12px;
  line-height: 17px;
  color: var(--color-danger);
}

.editor-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.editor-title {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  font-weight: 600;
  color: #3a4757;
}

.editor-title :deep(.app-icon) {
  color: #6e8093;
}

.editor-title .count {
  font-size: 12px;
  font-weight: 400;
  color: var(--color-ink-4);
}

.add-row {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 26px;
  padding: 0 9px;
  border: 1px dashed #d3dde8;
  border-radius: 6px;
  background: transparent;
  color: #6f8ba8;
  font-size: 12.5px;
  transition: background 0.16s, border-color 0.16s;
}

.add-row:hover {
  background: var(--color-primary-tint);
  border-color: #b9cadd;
}

.editor-rows {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.editor-row {
  display: grid;
  grid-template-columns: 96px minmax(0, 1fr) 88px 26px;
  align-items: center;
  gap: 8px;
}

.row-label :deep(.el-select__wrapper),
.row-value :deep(.el-input__wrapper) {
  height: 34px;
  min-height: 34px;
}

.row-label :deep(.el-select__placeholder) {
  font-size: 13px;
}

.primary-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  height: 28px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: #9aa6b4;
  font-size: 12px;
  transition: color 0.16s, background 0.16s;
}

.primary-toggle .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c6d0da;
}

.primary-toggle:hover {
  background: #f2f6fa;
  color: #6f8ba8;
}

.primary-toggle.is-primary {
  color: var(--color-primary-strong);
  font-weight: 600;
}

.primary-toggle.is-primary .dot {
  background: var(--color-primary);
}

.primary-spacer {
  display: block;
}

.row-remove {
  width: 26px;
  height: 26px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  display: grid;
  place-items: center;
  color: #b3bdc8;
  transition: color 0.16s, background 0.16s;
}

.row-remove:hover:not(:disabled) {
  color: #c25f5b;
  background: #fcf0ef;
}

.row-remove:disabled {
  color: #d9e0e8;
  cursor: not-allowed;
}
</style>
