<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppIcon from '@/components/common/AppIcon.vue'
import MultiValueEditor from './MultiValueEditor.vue'
import { useContactStore } from '@/stores/contactStore'
import {
  ADDRESS_LABELS,
  EMAIL_LABELS,
  GROUP_PRESETS,
  PHONE_LABELS,
  SOCIAL_PLATFORMS
} from '@/constants/contact'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  contact: { type: Object, default: null },
  saving: { type: Boolean, default: false },
  serverErrors: { type: Object, default: null }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const { state } = useContactStore()

const PHONE_RE = /^[\d+\-() ]+$/
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const formRef = ref(null)
const form = reactive(emptyForm())
const initialSnapshot = ref('')
const fieldErrors = reactive({
  name: [],
  group: [],
  notes: [],
  phones: [],
  emails: [],
  social_accounts: [],
  addresses: []
})

const isDirty = computed(() => JSON.stringify(form) !== initialSnapshot.value)

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isEdit = computed(() => Boolean(props.contact?.id))

const groupOptions = computed(() =>
  [...new Set([...GROUP_PRESETS, ...state.groups.map((item) => item.name)])].filter(Boolean)
)

const rules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { max: 50, message: '姓名长度不能超过 50 字符', trigger: 'blur' }
  ]
}

function emptyForm() {
  return {
    name: '',
    group: '',
    is_favorite: false,
    notes: '',
    phones: [{ label: '手机', number: '', is_primary: true }],
    emails: [{ label: '个人', email: '', is_primary: true }],
    social_accounts: [{ platform: '微信', account: '' }],
    addresses: [{ label: '家庭', address: '', is_primary: true }]
  }
}

function cloneList(list, factory) {
  if (!Array.isArray(list) || list.length === 0) return [factory()]
  return list.map((item) => ({ ...item }))
}

function fillForm(contact) {
  if (!contact) {
    Object.assign(form, emptyForm())
  } else {
    Object.assign(form, {
      name: contact.name || '',
      group: contact.group || '',
      is_favorite: Boolean(contact.is_favorite),
      notes: contact.notes || '',
      phones: cloneList(contact.phones, () => ({ label: '手机', number: '', is_primary: false })),
      emails: cloneList(contact.emails, () => ({ label: '个人', email: '', is_primary: false })),
      social_accounts: cloneList(contact.social_accounts, () => ({ platform: '微信', account: '' })),
      addresses: cloneList(contact.addresses, () => ({ label: '家庭', address: '', is_primary: false }))
    })
  }
  initialSnapshot.value = JSON.stringify(form)
}

function cleanRows(list, key) {
  return list
    .map((row) => ({ ...row, [key]: String(row[key] ?? '').trim() }))
    .filter((row) => row[key])
}

function normalizePrimary(list) {
  if (!list.length) return list
  const primaryIndex = Math.max(
    0,
    list.findIndex((item) => item.is_primary)
  )
  return list.map((item, index) => ({ ...item, is_primary: index === primaryIndex }))
}

function buildPayload() {
  const issues = []

  const phones = cleanRows(form.phones, 'number')
  phones.forEach((item, index) => {
    if (!PHONE_RE.test(item.number)) issues.push(`第 ${index + 1} 项电话号码格式不合法`)
  })

  const emails = cleanRows(form.emails, 'email')
  emails.forEach((item, index) => {
    if (!EMAIL_RE.test(item.email)) issues.push(`第 ${index + 1} 项邮箱格式不合法`)
  })

  const socialAccounts = cleanRows(form.social_accounts, 'account')
  const addresses = cleanRows(form.addresses, 'address')
  addresses.forEach((item, index) => {
    if (item.address.length > 200) issues.push(`第 ${index + 1} 项地址长度不能超过 200 字符`)
  })

  if (issues.length) {
    ElMessage.warning(issues[0])
    return null
  }

  return {
    name: form.name.trim(),
    group: form.group?.trim() || null,
    is_favorite: Boolean(form.is_favorite),
    notes: form.notes.trim() || null,
    phones: normalizePrimary(
      phones.map((item) => ({
        label: item.label?.trim() || '手机',
        number: item.number,
        is_primary: Boolean(item.is_primary)
      }))
    ),
    emails: normalizePrimary(
      emails.map((item) => ({
        label: item.label?.trim() || '个人',
        email: item.email,
        is_primary: Boolean(item.is_primary)
      }))
    ),
    social_accounts: socialAccounts.map((item) => ({
      platform: item.platform?.trim() || '其他',
      account: item.account
    })),
    addresses: normalizePrimary(
      addresses.map((item) => ({
        label: item.label?.trim() || '其他',
        address: item.address,
        is_primary: Boolean(item.is_primary)
      }))
    )
  }
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  const payload = buildPayload()
  if (!payload) return
  emit('submit', payload)
}

function extractMessages(value) {
  if (Array.isArray(value)) return value.map((item) => String(item)).filter(Boolean)
  return value ? [String(value)] : []
}

function applyServerErrors(details) {
  Object.keys(fieldErrors).forEach((key) => {
    fieldErrors[key] = extractMessages(details?.[key])
  })
}

function clearFieldErrors() {
  if (Object.values(fieldErrors).some((messages) => messages.length > 0)) {
    Object.keys(fieldErrors).forEach((key) => {
      fieldErrors[key] = []
    })
  }
}

function confirmDiscard() {
  return ElMessageBox.confirm(
    `「${form.name.trim() || '新联系人'}」的修改尚未保存，关闭后这些修改将丢失。`,
    '放弃未保存的修改？',
    {
      type: 'warning',
      confirmButtonText: '放弃修改',
      cancelButtonText: '继续编辑',
      confirmButtonClass: 'el-button--danger'
    }
  )
    .then(() => true)
    .catch(() => false)
}

function requestClose() {
  if (props.saving) return
  if (!isDirty.value) {
    visible.value = false
    return
  }
  confirmDiscard().then((discard) => {
    if (discard) visible.value = false
  })
}

function handleBeforeClose(done) {
  if (props.saving) return
  if (!isDirty.value) {
    done()
    return
  }
  confirmDiscard().then((discard) => {
    if (discard) done()
  })
}

watch(
  () => props.serverErrors,
  (details) => applyServerErrors(details),
  { immediate: true }
)

watch(
  () => JSON.stringify(form),
  () => clearFieldErrors()
)

watch(
  () => props.modelValue,
  (open) => {
    if (!open) return
    fillForm(props.contact)
    applyServerErrors(props.serverErrors)
    nextTick(() => formRef.value?.clearValidate())
  }
)
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑联系人' : '新增联系人'"
    width="660px"
    top="5vh"
    class="contact-dialog"
    :close-on-click-modal="false"
    :before-close="handleBeforeClose"
    append-to-body
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent>
      <div class="form-row">
        <el-form-item
          label="姓名"
          prop="name"
          class="form-item-name"
          :error="fieldErrors.name.join('；')"
        >
          <el-input v-model="form.name" maxlength="50" show-word-limit placeholder="请输入姓名" />
        </el-form-item>

        <el-form-item
          label="分组"
          class="form-item-group"
          :error="fieldErrors.group.join('；')"
        >
          <el-select
            v-model="form.group"
            filterable
            allow-create
            default-first-option
            clearable
            placeholder="选择或输入分组"
          >
            <el-option v-for="group in groupOptions" :key="group" :label="group" :value="group" />
          </el-select>
        </el-form-item>

        <el-form-item label="收藏" class="form-item-favorite">
          <el-switch v-model="form.is_favorite" :width="36" />
        </el-form-item>
      </div>

      <el-form-item label="备注" :error="fieldErrors.notes.join('；')">
        <el-input
          v-model="form.notes"
          type="textarea"
          :rows="2"
          maxlength="500"
          show-word-limit
          placeholder="补充说明，最多 500 字"
        />
      </el-form-item>

      <div class="editors">
        <MultiValueEditor
          v-model="form.phones"
          title="电话号码"
          icon="phone"
          type="phone"
          :label-options="PHONE_LABELS"
          placeholder="请输入电话号码"
          :errors="fieldErrors.phones"
        />
        <MultiValueEditor
          v-model="form.emails"
          title="邮箱地址"
          icon="mail"
          type="email"
          :label-options="EMAIL_LABELS"
          placeholder="请输入邮箱地址"
          :errors="fieldErrors.emails"
        />
        <MultiValueEditor
          v-model="form.social_accounts"
          title="社交账号"
          icon="chat"
          type="social"
          :label-options="SOCIAL_PLATFORMS"
          placeholder="账号名 / ID / 主页链接"
          :errors="fieldErrors.social_accounts"
        />
        <MultiValueEditor
          v-model="form.addresses"
          title="联系地址"
          icon="pin"
          type="address"
          :label-options="ADDRESS_LABELS"
          placeholder="请输入详细地址"
          :errors="fieldErrors.addresses"
        />
      </div>
    </el-form>

    <template #footer>
      <el-button @click="requestClose">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSubmit">
        <AppIcon v-if="!saving" name="check" :size="14" />保存
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.form-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 168px 82px;
  gap: 14px;
  align-items: start;
}

.form-item-favorite :deep(.el-form-item__content) {
  height: 36px;
  display: flex;
  align-items: center;
}

.editors {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 4px;
}

:global(.contact-dialog) {
  max-width: calc(100vw - 40px);
}

:global(.contact-dialog .el-dialog__body) {
  max-height: calc(100vh - 230px);
  overflow-y: auto;
  padding-right: 4px;
  padding-bottom: 4px;
}

:global(.contact-dialog .el-dialog__body::-webkit-scrollbar) {
  width: 5px;
}

:global(.contact-dialog .el-dialog__body::-webkit-scrollbar-thumb) {
  background: #e6ebf1;
  border-radius: 3px;
}
</style>
