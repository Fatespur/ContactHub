export const MAX_IMPORT_SIZE = 10 * 1024 * 1024
export const IMPORT_ACCEPT = '.xlsx'
export const IMPORT_TEMPLATE_URL = '/templates/contacts-import-template.xlsx'
export const IMPORT_TEMPLATE_NAME = '联系人导入模板.xlsx'

const XLSX_RE = /\.xlsx$/i

/** Client-side validation before upload, returns { valid, message }. */
export function validateExcelFile(file) {
  if (!file) return { valid: false, message: '请选择要导入的文件' }
  if (!XLSX_RE.test(file.name || '')) {
    return { valid: false, message: '仅支持 .xlsx 格式的 Excel 文件' }
  }
  if (!file.size) {
    return { valid: false, message: '文件内容为空，请检查后重新选择' }
  }
  if (file.size > MAX_IMPORT_SIZE) {
    return { valid: false, message: '文件不得超过 10MB' }
  }
  return { valid: true, message: '' }
}

export function formatFileSize(bytes) {
  if (!bytes) return '0 KB'
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

function csvCell(value) {
  const text = value == null ? '' : String(value)
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text
}

function toCsv(rows) {
  return `\uFEFF${rows.map((row) => row.map(csvCell).join(',')).join('\r\n')}`
}

/** Build CSV data for import failure details (row, name, reason). */
export function buildFailureCsv(errors = []) {
  const rows = [['行号', '姓名', '原因']]
  errors.forEach((item) => {
    rows.push([item?.row ?? '', item?.name ?? '', item?.reason ?? ''])
  })
  return toCsv(rows)
}

function joinItems(list, formatter) {
  if (!Array.isArray(list) || list.length === 0) return ''
  return list.map(formatter).join('\n')
}

/**
 * Mock export demonstration CSV: matches contract's 8 columns and multi-line cell format.
 */
export function buildContactsCsv(items = []) {
  const rows = [['姓名', '分组', '是否收藏', '电话', '邮箱', '社交账号', '地址', '备注']]
  items.forEach((contact) => {
    rows.push([
      contact.name,
      contact.group || '',
      contact.is_favorite ? '是' : '否',
      joinItems(contact.phones, (item) => `${item.label || '手机'}${item.is_primary ? '*' : ''}:${item.number}`),
      joinItems(contact.emails, (item) => `${item.label || '个人'}${item.is_primary ? '*' : ''}:${item.email}`),
      joinItems(contact.social_accounts, (item) => `${item.platform || '其他'}:${item.account}`),
      joinItems(contact.addresses, (item) => `${item.label || '其他'}${item.is_primary ? '*' : ''}:${item.address}`),
      contact.notes || ''
    ])
  })
  return toCsv(rows)
}

export function formatStamp(date = new Date()) {
  const pad = (value) => String(value).padStart(2, '0')
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
    '_',
    pad(date.getHours()),
    pad(date.getMinutes()),
    pad(date.getSeconds())
  ].join('')
}
