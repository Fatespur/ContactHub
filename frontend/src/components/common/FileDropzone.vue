<script setup>
import { ref } from 'vue'
import AppIcon from '@/components/common/AppIcon.vue'

const props = defineProps({
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['select'])

const inputRef = ref(null)
const dragover = ref(false)

function openPicker() {
  if (props.disabled) return
  inputRef.value?.click()
}

function onChange(event) {
  const file = event.target.files?.[0]
  if (file) emit('select', file)
  event.target.value = ''
}

function onDragOver() {
  if (props.disabled) return
  dragover.value = true
}

function onDrop(event) {
  if (props.disabled) return
  dragover.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) emit('select', file)
}
</script>

<template>
  <div
    class="file-dropzone"
    :class="{ 'is-dragover': dragover, 'is-disabled': disabled }"
    role="button"
    :tabindex="disabled ? -1 : 0"
    aria-label="选择或拖入 Excel 文件"
    @click="openPicker"
    @keydown.enter.prevent="openPicker"
    @keydown.space.prevent="openPicker"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="dragover = false"
    @drop.prevent="onDrop"
  >
    <div class="dz-icon">
      <AppIcon name="upload" :size="22" />
    </div>
    <p class="dz-title">拖动文件到此处，或 <span class="link">点击选择</span></p>
    <p class="dz-sub">选择后点击「开始导入」，支持 .xlsx</p>
    <input ref="inputRef" class="dz-input" type="file" accept=".xlsx" @change="onChange" />
  </div>
</template>

<style scoped>
.file-dropzone {
  margin-top: 16px;
  padding: 30px 20px 26px;
  border: 1.5px dashed #d5dfea;
  border-radius: 10px;
  background: #fcfdff;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.16s, background 0.16s;
}

.file-dropzone:hover,
.file-dropzone:focus-visible,
.file-dropzone.is-dragover {
  border-color: #b9cadd;
  background: #f8fbfe;
  outline: none;
}

.file-dropzone.is-disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.dz-icon {
  width: 46px;
  height: 46px;
  margin: 0 auto;
  border-radius: 50%;
  background: var(--color-primary-tint);
  display: grid;
  place-items: center;
  color: #7c93ac;
}

.dz-title {
  margin: 12px 0 0;
  font-size: 14px;
  line-height: 22px;
  color: #3b4a5c;
}

.dz-title .link {
  color: var(--color-primary-strong);
  font-weight: 600;
}

.dz-sub {
  margin: 6px 0 0;
  font-size: 12px;
  color: var(--color-ink-4);
}

.dz-input {
  display: none;
}
</style>
