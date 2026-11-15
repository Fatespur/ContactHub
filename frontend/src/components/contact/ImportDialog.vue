<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import AppIcon from '@/components/common/AppIcon.vue'
import FileDropzone from '@/components/common/FileDropzone.vue'
import { importContacts } from '@/api/contacts'
import {
  IMPORT_TEMPLATE_NAME,
  IMPORT_TEMPLATE_URL,
  buildFailureCsv,
  formatFileSize,
  formatStamp,
  validateExcelFile
} from '@/utils/excel'
import { downloadBlob } from '@/utils/download'

const props = defineProps({
  modelValue: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'finished'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const stage = ref('select')
const file = ref(null)
const error = ref('')
const progress = ref(0)
const result = ref(null)
let controller = null
let closing = false

const title = computed(() => (stage.value === 'result' ? '导入结果' : '导入联系人'))
const dialogWidth = computed(() => (stage.value === 'result' ? '640px' : '600px'))
const uploading = computed(() => stage.value === 'uploading')
const canStart = computed(() => Boolean(file.value) && !error.value)
const progressText = computed(() =>
  progress.value >= 100 ? '正在解析文件…' : '正在上传并解析文件…'
)

const banner = computed(() => {
  const data = result.value
  if (!data) return null
  if (!data.failed_count) {
    return {
      tone: 'success',
      icon: 'check-circle',
      text: `导入完成，${data.success_count} 条记录已添加到通讯录末尾`
    }
  }
  if (data.success_count > 0) {
    return {
      tone: 'warning',
      icon: 'alert',
      text: `${data.success_count} 条导入成功，${data.failed_count} 条失败，请查看失败明细`
    }
  }
  return {
    tone: 'danger',
    icon: 'alert',
    text: '导入失败，请根据失败原因修改文件后重试'
  }
})

function reset() {
  controller?.abort()
  controller = null
  stage.value = 'select'
  file.value = null
  error.value = ''
  progress.value = 0
  result.value = null
  closing = false
}

watch(
  () => props.modelValue,
  (open) => {
    if (open) reset()
  }
)

function onSelect(selected) {
  const check = validateExcelFile(selected)
  if (!check.valid) {
    file.value = null
    error.value = check.message
    return
  }
  error.value = ''
  file.value = selected
}

function removeFile() {
  file.value = null
  error.value = ''
}

async function startImport() {
  if (!canStart.value) return
  stage.value = 'uploading'
  progress.value = 0
  error.value = ''
  controller = new AbortController()
  try {
    const data = await importContacts(file.value, {
      signal: controller.signal,
      onUploadProgress: (value) => {
        progress.value = value
      }
    })
    result.value = data
    stage.value = 'result'
    emit('finished', data)
  } catch (err) {
    stage.value = 'select'
    if (err?.name === 'AbortError') {
      if (!closing) ElMessage.info('已取消导入')
    } else {
      error.value = err?.message || '导入失败，请稍后重试'
      if (!err?._notified) ElMessage.error(error.value)
    }
  } finally {
    controller = null
  }
}

function cancelUpload() {
  controller?.abort()
}

function handleBeforeClose(done) {
  if (uploading.value) {
    closing = true
    controller?.abort()
  }
  done()
}

function close() {
  visible.value = false
}

function downloadFailures() {
  const data = result.value
  if (!data?.errors?.length) return
  const csv = buildFailureCsv(data.errors)
  downloadBlob(
    new Blob([csv], { type: 'text/csv;charset=utf-8' }),
    `导入失败明细_${formatStamp()}.csv`
  )
}
</script>

<template>
  <el-dialog
    v-model="visible"
    :width="dialogWidth"
    class="import-dialog"
    :close-on-click-modal="false"
    :before-close="handleBeforeClose"
    append-to-body
    @closed="reset"
  >
    <template #header>
      <div class="dlg-head">
        <h2>{{ title }}</h2>
        <p v-if="stage === 'result'" class="dlg-meta">
          {{ file?.name }} · 共 {{ result?.total_rows }} 行
        </p>
      </div>
    </template>

    <!-- 选择文件 -->
    <div v-if="stage === 'select'" class="dlg-body">
      <div class="dlg-note">
        <AppIcon name="info" :size="15" />
        <div>
          仅支持 <b>.xlsx</b> 格式，单个文件不超过 <b>10MB</b>；每行对应一位联系人。重复导入同一文件会全部新增，<b>系统不会自动去重</b>。
        </div>
      </div>

      <FileDropzone v-if="!file" :disabled="uploading" @select="onSelect" />

      <div v-else class="file-card">
        <div class="file-icon">
          <AppIcon name="file" :size="17" />
        </div>
        <div class="file-main">
          <div class="file-name">{{ file.name }}</div>
          <div class="file-size">{{ formatFileSize(file.size) }}</div>
        </div>
        <button class="file-remove" type="button" aria-label="移除文件" @click="removeFile">
          <AppIcon name="close" :size="13" />
        </button>
      </div>

      <p v-if="error" class="inline-error">
        <AppIcon name="alert" :size="13" />
        {{ error }}
      </p>

      <div class="template-row">
        <span>首次导入？建议先使用 8 列模板填写</span>
        <a
          class="template-link"
          :href="IMPORT_TEMPLATE_URL"
          :download="IMPORT_TEMPLATE_NAME"
        >
          <AppIcon name="download" :size="13" />下载导入模板
        </a>
      </div>
    </div>

    <!-- 上传 / 解析 -->
    <div v-else-if="stage === 'uploading'" class="dlg-body">
      <div class="file-card">
        <div class="file-icon">
          <AppIcon name="file" :size="17" />
        </div>
        <div class="file-main">
          <div class="file-name">{{ file?.name }}</div>
          <div class="file-size">{{ formatFileSize(file?.size || 0) }}</div>
        </div>
      </div>

      <div class="progress-row">
        <span>{{ progressText }}</span>
        <span class="pct">{{ progress }}%</span>
      </div>
      <div class="progress-track">
        <div class="progress-bar" :style="{ width: `${progress}%` }" />
      </div>
      <p class="result-note">解析期间请勿关闭窗口。完成后将显示成功与失败明细。</p>
    </div>

    <!-- 结果 -->
    <div v-else class="dlg-body" aria-live="polite">
      <div v-if="banner" class="result-banner" :class="`is-${banner.tone}`">
        <AppIcon :name="banner.icon" :size="17" />
        <span>{{ banner.text }}</span>
      </div>

      <div class="stats">
        <div class="stat">
          <div class="label">总行数</div>
          <div class="value">{{ result?.total_rows }}</div>
        </div>
        <div class="stat is-success">
          <div class="label">成功</div>
          <div class="value">{{ result?.success_count }}</div>
        </div>
        <div class="stat is-danger">
          <div class="label">失败</div>
          <div class="value">{{ result?.failed_count }}</div>
        </div>
      </div>

      <template v-if="result?.failed_count">
        <div class="fail-head">
          <h3>失败明细 <span>({{ result.failed_count }})</span></h3>
        </div>
        <div class="fail-table" role="table" aria-label="失败明细">
          <div class="fail-row is-head" role="row">
            <span>行号</span><span>姓名</span><span>原因</span>
          </div>
          <div
            v-for="(item, index) in result.errors || []"
            :key="`${item.row}-${index}`"
            class="fail-row"
            role="row"
          >
            <span class="row-no">{{ item.row }}</span>
            <span>{{ item.name || '—' }}</span>
            <span class="reason">{{ item.reason }}</span>
          </div>
        </div>
        <p class="result-note">
          重复导入同一文件仍会全部新增，系统不会自动去重；如需调整，请在列表中编辑或删除。
        </p>
      </template>
      <p v-else class="result-note">全部记录导入成功，可到通讯录末尾查看新增联系人。</p>
    </div>

    <template #footer>
      <div class="dialog-foot">
        <span class="foot-hint">
          {{ stage === 'result' ? '成功导入的记录追加到列表末尾' : '支持 .xlsx / 10MB 以内' }}
        </span>
        <div class="foot-actions">
          <template v-if="stage === 'select'">
            <el-button @click="close">取消</el-button>
            <el-button type="primary" :disabled="!canStart" @click="startImport">开始导入</el-button>
          </template>
          <template v-else-if="stage === 'uploading'">
            <el-button @click="cancelUpload">取消上传</el-button>
            <el-button type="primary" loading disabled>导入中…</el-button>
          </template>
          <template v-else>
            <el-button v-if="result?.failed_count" @click="downloadFailures">下载失败明细</el-button>
            <el-button type="primary" @click="close">完成</el-button>
          </template>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.dlg-head h2 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: var(--color-ink);
  letter-spacing: 0.2px;
  line-height: 24px;
}

.dlg-meta {
  margin: 6px 0 0;
  font-size: 12px;
  color: var(--color-ink-4);
}

.dlg-body {
  padding-top: 2px;
}

.dlg-note {
  display: flex;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid #e8eef6;
  border-radius: 8px;
  background: #f6f9fc;
  color: #5f6f80;
  font-size: 12.5px;
  line-height: 19px;
}

.dlg-note :deep(.app-icon) {
  margin-top: 2px;
  color: #7c93ac;
}

.dlg-note b {
  color: #4a5b6e;
  font-weight: 600;
}

.file-card {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid var(--color-line-strong);
  border-radius: 10px;
  background: #fcfdfe;
}

.file-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: #eef4fa;
  color: #6f8ba8;
  display: grid;
  place-items: center;
  flex: none;
}

.file-main {
  min-width: 0;
  flex: 1;
}

.file-name {
  font-size: 13.5px;
  color: #2b3440;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  margin-top: 3px;
  font-size: 12px;
  color: var(--color-ink-4);
}

.file-remove {
  width: 26px;
  height: 26px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  display: grid;
  place-items: center;
  color: #aab4c0;
}

.file-remove:hover {
  background: #f2f5f8;
  color: var(--color-ink-3);
}

.inline-error {
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 10px 0 0;
  font-size: 12.5px;
  color: var(--color-danger);
}

.template-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 14px;
  font-size: 12.5px;
  color: #8a97a6;
}

.template-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--color-primary-strong);
  font-weight: 500;
  text-decoration: none;
}

.template-link:hover {
  text-decoration: underline;
}

.progress-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 14px;
  font-size: 12px;
  color: var(--color-ink-3);
}

.progress-row .pct {
  color: var(--color-primary-strong);
  font-weight: 600;
}

.progress-track {
  margin-top: 7px;
  height: 6px;
  border-radius: 999px;
  background: #eef2f7;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 999px;
  background: var(--color-primary);
  transition: width 0.25s;
}

.result-banner {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 12px 14px;
  border-radius: 9px;
  font-size: 13px;
  line-height: 20px;
}

.result-banner.is-success {
  border: 1px solid #e3efe6;
  background: var(--color-success-soft);
  color: #3f5c48;
}

.result-banner.is-success :deep(.app-icon) {
  color: #6f9a7d;
}

.result-banner.is-warning {
  border: 1px solid #f3e8cf;
  background: #fdf9ef;
  color: #7f652f;
}

.result-banner.is-warning :deep(.app-icon) {
  color: #b28a44;
}

.result-banner.is-danger {
  border: 1px solid #f3dedd;
  background: var(--color-danger-soft);
  color: #8f4f4d;
}

.result-banner.is-danger :deep(.app-icon) {
  color: #b96a66;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 14px;
}

.stat {
  padding: 12px 14px;
  border: 1px solid var(--color-line);
  border-radius: 9px;
  background: #fbfcfe;
}

.stat .label {
  font-size: 12px;
  color: var(--color-ink-4);
}

.stat .value {
  margin-top: 4px;
  font-size: 24px;
  font-weight: 600;
  line-height: 30px;
  color: #2b3440;
  font-variant-numeric: tabular-nums;
}

.stat.is-success .value {
  color: #5f8f6f;
}

.stat.is-danger .value {
  color: var(--color-danger);
}

.fail-head {
  margin: 18px 0 8px;
}

.fail-head h3 {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #3a4757;
}

.fail-head h3 span {
  color: var(--color-ink-4);
  font-weight: 400;
}

.fail-table {
  border: 1px solid var(--color-line);
  border-radius: 9px;
  overflow: hidden;
  max-height: 188px;
  overflow-y: auto;
}

.fail-row {
  display: grid;
  grid-template-columns: 64px 110px minmax(0, 1fr);
  align-items: center;
  gap: 8px;
  padding: 0 14px;
  height: 36px;
  font-size: 12.5px;
  color: var(--color-ink-2);
  border-bottom: 1px solid #f3f5f8;
}

.fail-row:last-child {
  border-bottom: 0;
}

.fail-row.is-head {
  height: 34px;
  background: #f7f9fb;
  color: #6b7785;
  font-size: 12px;
  font-weight: 600;
  position: sticky;
  top: 0;
}

.fail-row .row-no {
  color: var(--color-ink-4);
  font-variant-numeric: tabular-nums;
}

.fail-row .reason {
  color: #8a6a68;
}

.result-note {
  margin: 12px 0 0;
  font-size: 12px;
  line-height: 18px;
  color: var(--color-ink-4);
}

.dialog-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-line);
  background: #fdfefe;
}

.foot-hint {
  font-size: 12px;
  color: var(--color-ink-4);
}

.foot-actions {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

:global(.import-dialog) {
  padding: 0;
  max-width: calc(100vw - 40px);
}

:global(.import-dialog .el-dialog__header) {
  padding: 22px 24px 0;
  margin-right: 0;
}

:global(.import-dialog .el-dialog__body) {
  padding: 14px 24px 22px;
}

:global(.import-dialog .el-dialog__footer) {
  padding: 0;
}

:global(.import-dialog .el-dialog__headerbtn) {
  top: 14px;
  right: 14px;
  width: 30px;
  height: 30px;
}
</style>
