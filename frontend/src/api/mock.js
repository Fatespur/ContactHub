import { createInitialContacts } from '@/mock/contacts'

export class MockApiError extends Error {
  constructor(message, { code = 400, errorCode = 'VALIDATION_ERROR', details = null } = {}) {
    super(message)
    this.name = 'MockApiError'
    this.code = code
    this.errorCode = errorCode
    this.details = details
    this._notified = false
  }
}

const PHONE_RE = /^[\d+\-() ]+$/
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

let contacts = createInitialContacts()
let nextId = contacts.reduce((max, item) => Math.max(max, item.id), 0) + 1

const wait = (ms = 240) => new Promise((resolve) => setTimeout(resolve, ms))
const clone = (value) => JSON.parse(JSON.stringify(value))
const nowIso = () => new Date().toISOString().replace(/\.\d{3}Z$/, 'Z')

function pushError(errors, key, message) {
  if (!errors[key]) errors[key] = []
  errors[key].push(message)
}

function ensureSinglePrimary(list) {
  if (!Array.isArray(list) || list.length === 0) return list
  let found = false
  list.forEach((item) => {
    if (item.is_primary && !found) {
      found = true
    } else {
      item.is_primary = false
    }
  })
  if (!found) list[0].is_primary = true
  return list
}

function normalizePhones(input, errors) {
  const list = Array.isArray(input) ? input : []
  const result = list.map((item, index) => {
    const number = String(item?.number ?? '').trim()
    if (!number) pushError(errors, 'phones', `第 ${index + 1} 项电话号码不能为空`)
    else if (!PHONE_RE.test(number)) pushError(errors, 'phones', `第 ${index + 1} 项电话号码格式不合法`)
    return {
      label: String(item?.label ?? '').trim() || '手机',
      number,
      is_primary: Boolean(item?.is_primary)
    }
  })
  return ensureSinglePrimary(result)
}

function normalizeEmails(input, errors) {
  const list = Array.isArray(input) ? input : []
  const result = list.map((item, index) => {
    const email = String(item?.email ?? '').trim()
    if (!email) pushError(errors, 'emails', `第 ${index + 1} 项邮箱不能为空`)
    else if (!EMAIL_RE.test(email)) pushError(errors, 'emails', `第 ${index + 1} 项邮箱格式不合法`)
    return {
      label: String(item?.label ?? '').trim() || '个人',
      email,
      is_primary: Boolean(item?.is_primary)
    }
  })
  return ensureSinglePrimary(result)
}

function normalizeSocials(input, errors) {
  const list = Array.isArray(input) ? input : []
  return list.map((item, index) => {
    const account = String(item?.account ?? '').trim()
    if (!account) pushError(errors, 'social_accounts', `第 ${index + 1} 项社交账号不能为空`)
    return {
      platform: String(item?.platform ?? '').trim() || '其他',
      account
    }
  })
}

function normalizeAddresses(input, errors) {
  const list = Array.isArray(input) ? input : []
  const result = list.map((item, index) => {
    const address = String(item?.address ?? '').trim()
    if (!address) pushError(errors, 'addresses', `第 ${index + 1} 项地址不能为空`)
    else if (address.length > 200) pushError(errors, 'addresses', `第 ${index + 1} 项地址长度不能超过 200 字符`)
    return {
      label: String(item?.label ?? '').trim() || '其他',
      address,
      is_primary: Boolean(item?.is_primary)
    }
  })
  return ensureSinglePrimary(result)
}

/** 与契约一致：PUT 为全量替换，缺失字段按默认值重置 */
function normalizePayload(payload = {}) {
  const errors = {}
  const name = String(payload.name ?? '').trim()
  if (!name) pushError(errors, 'name', '姓名不能为空')
  else if (name.length > 50) pushError(errors, 'name', '姓名长度不能超过 50 字符')

  let notes = payload.notes == null ? null : String(payload.notes).trim()
  if (!notes) notes = null
  else if (notes.length > 500) pushError(errors, 'notes', '备注长度不能超过 500 字符')

  const phones = normalizePhones(payload.phones, errors)
  const emails = normalizeEmails(payload.emails, errors)
  const socialAccounts = normalizeSocials(payload.social_accounts, errors)
  const addresses = normalizeAddresses(payload.addresses, errors)

  if (Object.keys(errors).length > 0) {
    throw new MockApiError('输入参数有误，请检查', { details: errors })
  }

  const group = payload.group == null ? null : String(payload.group).trim() || null

  return {
    name,
    group,
    is_favorite: Boolean(payload.is_favorite),
    notes,
    phones,
    emails,
    social_accounts: socialAccounts,
    addresses
  }
}

function findContact(id) {
  const contact = contacts.find((item) => item.id === Number(id))
  if (!contact) {
    throw new MockApiError('联系人不存在', { code: 404, errorCode: 'NOT_FOUND' })
  }
  return contact
}

function readFavorite(value) {
  if (value === undefined || value === null || value === '') return null
  if (value === true || value === 1 || value === '1' || String(value).toLowerCase() === 'true') return true
  if (value === false || value === 0 || value === '0' || String(value).toLowerCase() === 'false') return false
  throw new MockApiError('is_favorite 参数不合法', { details: null })
}

export async function listContacts(params = {}) {
  await wait()
  const page = Number(params.page ?? 1)
  const pageSize = Number(params.page_size ?? 10)

  if (!Number.isInteger(page) || page < 1) {
    throw new MockApiError('page 必须是大于等于 1 的整数', { details: null })
  }
  if (!Number.isInteger(pageSize) || pageSize < 1 || pageSize > 100) {
    throw new MockApiError('page_size 必须在 1 到 100 之间', { details: null })
  }

  const keyword = String(params.keyword ?? '').trim().toLowerCase()
  const favorite = readFavorite(params.is_favorite)
  const group = params.group ? String(params.group) : ''

  const filtered = contacts.filter((contact) => {
    if (favorite !== null && contact.is_favorite !== favorite) return false
    if (group && contact.group !== group) return false
    if (!keyword) return true
    const pool = [
      contact.name,
      contact.notes || '',
      ...contact.phones.map((item) => item.number),
      ...contact.emails.map((item) => item.email)
    ]
      .join(' ')
      .toLowerCase()
    return pool.includes(keyword)
  })

  const start = (page - 1) * pageSize
  return {
    total: filtered.length,
    page,
    page_size: pageSize,
    items: clone(filtered.slice(start, start + pageSize))
  }
}

export async function getContact(id) {
  await wait(160)
  return clone(findContact(id))
}

export async function createContact(payload) {
  await wait(320)
  const data = normalizePayload(payload)
  const timestamp = nowIso()
  const contact = { id: nextId, ...data, created_at: timestamp, updated_at: timestamp }
  nextId += 1
  contacts.push(contact)
  return { id: contact.id }
}

export async function updateContact(id, payload) {
  await wait(320)
  const contact = findContact(id)
  Object.assign(contact, normalizePayload(payload), { updated_at: nowIso() })
  return { id: contact.id }
}

export async function deleteContact(id) {
  await wait(260)
  const contact = findContact(id)
  contacts = contacts.filter((item) => item.id !== contact.id)
  return null
}

export async function updateFavorite(id, isFavorite) {
  await wait(180)
  const contact = findContact(id)
  contact.is_favorite = Boolean(isFavorite)
  contact.updated_at = nowIso()
  return { id: contact.id, is_favorite: contact.is_favorite }
}

/* ---------------- 导入 / 导出（Mock 演示） ---------------- */

const DEMO_IMPORT_ROWS = [
  {
    name: '周杰',
    group: '同学',
    is_favorite: false,
    notes: null,
    phones: [{ label: '手机', number: '13811112222', is_primary: true }],
    emails: [{ label: '个人', email: 'zhoujie@email.com', is_primary: true }],
    social_accounts: [],
    addresses: []
  },
  {
    name: '吴倩',
    group: '朋友',
    is_favorite: false,
    notes: null,
    phones: [{ label: '手机', number: '13922223334', is_primary: true }],
    emails: [{ label: '个人', email: 'wuqian@email.com', is_primary: true }],
    social_accounts: [{ platform: '微信', account: 'wuqian_friend' }],
    addresses: []
  },
  {
    name: '郑凯',
    group: '同事',
    is_favorite: false,
    notes: '产品组',
    phones: [{ label: '工作', number: '0591-66778899', is_primary: true }],
    emails: [{ label: '工作', email: 'zhengkai@company.com', is_primary: true }],
    social_accounts: [],
    addresses: [{ label: '公司', address: '福州市软件园 B 区 3 号楼', is_primary: true }]
  },
  {
    name: '王芳',
    group: '家人',
    is_favorite: true,
    notes: null,
    phones: [{ label: '手机', number: '13644445556', is_primary: true }],
    emails: [],
    social_accounts: [],
    addresses: []
  },
  {
    name: '冯磊',
    group: '同学',
    is_favorite: false,
    notes: null,
    phones: [{ label: '手机', number: '13555556667', is_primary: true }],
    emails: [{ label: '个人', email: 'fenglei@email.com', is_primary: true }],
    social_accounts: [],
    addresses: []
  },
  {
    name: '蒋雯',
    group: '朋友',
    is_favorite: false,
    notes: null,
    phones: [{ label: '手机', number: '13466667778', is_primary: true }],
    emails: [{ label: '个人', email: 'jiangwen@email.com', is_primary: true }],
    social_accounts: [{ platform: '微博', account: '@jiangwen' }],
    addresses: []
  },
  {
    name: '韩雪',
    group: '同事',
    is_favorite: false,
    notes: null,
    phones: [{ label: '手机', number: '13377778889', is_primary: true }],
    emails: [{ label: '工作', email: 'hanxue@company.com', is_primary: true }],
    social_accounts: [],
    addresses: []
  },
  {
    name: '沈鹏',
    group: '同学',
    is_favorite: false,
    notes: null,
    phones: [{ label: '手机', number: '13288889990', is_primary: true }],
    emails: [{ label: '个人', email: 'shenpeng@email.com', is_primary: true }],
    social_accounts: [],
    addresses: []
  }
]

function abortError() {
  const error = new Error('已取消导入')
  error.name = 'AbortError'
  return error
}

function stepDelay(ms, signal) {
  if (signal?.aborted) return Promise.reject(abortError())
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      signal?.removeEventListener('abort', handleAbort)
      resolve()
    }, ms)
    function handleAbort() {
      clearTimeout(timer)
      reject(abortError())
    }
    signal?.addEventListener('abort', handleAbort, { once: true })
  })
}

export async function importContacts(file, { onProgress, signal } = {}) {
  if (!file) {
    throw new MockApiError('请选择要导入的文件', { details: null })
  }

  await stepDelay(220, signal)
  onProgress?.(12)
  await stepDelay(380, signal)
  onProgress?.(46)
  await stepDelay(420, signal)
  onProgress?.(78)
  await stepDelay(320, signal)
  onProgress?.(100)

  const timestamp = nowIso()
  DEMO_IMPORT_ROWS.forEach((payload) => {
    const data = normalizePayload(payload)
    contacts.push({
      id: nextId,
      ...data,
      created_at: timestamp,
      updated_at: timestamp
    })
    nextId += 1
  })

  return {
    total_rows: DEMO_IMPORT_ROWS.length + 2,
    success_count: DEMO_IMPORT_ROWS.length,
    failed_count: 2,
    errors: [
      { row: 4, name: '王五', reason: '姓名为空或格式无法识别' },
      { row: 9, name: '林小雨', reason: '第 1 项邮箱格式不合法' }
    ]
  }
}
