import { GROUP_PRESETS } from '@/constants/contact'

/** 取主项：优先 is_primary，其次第一项 */
export function primaryOf(list) {
  if (!Array.isArray(list) || list.length === 0) return null
  return list.find((item) => item.is_primary) || list[0]
}

/**
 * 表格「其他联系方式」取值：邮箱 > 社交账号 > 地址
 * @returns {{ icon: string, text: string, type: string } | null}
 */
export function otherContact(contact) {
  const email = primaryOf(contact.emails)
  if (email) return { icon: 'mail', text: email.email, type: 'email' }

  const social = contact.social_accounts?.[0]
  if (social) return { icon: 'chat', text: social.account, type: 'social' }

  const address = primaryOf(contact.addresses)
  if (address) return { icon: 'pin', text: address.address, type: 'address' }

  return null
}

/** 姓名首字，用于生成占位头像 */
export function initials(name) {
  const text = String(name ?? '').trim()
  return text ? text.charAt(0) : '?'
}

/** 由全量联系人聚合分组统计（不受当前筛选影响） */
export function buildGroupStats(items) {
  const counter = new Map()
  items.forEach((item) => {
    if (!item.group) return
    counter.set(item.group, (counter.get(item.group) || 0) + 1)
  })
  return [...counter.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => {
      const ai = GROUP_PRESETS.indexOf(a.name)
      const bi = GROUP_PRESETS.indexOf(b.name)
      if (ai !== -1 || bi !== -1) {
        if (ai === -1) return 1
        if (bi === -1) return -1
        return ai - bi
      }
      return a.name.localeCompare(b.name, 'zh-Hans-CN')
    })
}

/** 页码窗口：数据量较小直接全展示 */
export function buildPageList(page, pageCount) {
  if (pageCount <= 7) {
    return Array.from({ length: pageCount }, (_, index) => index + 1)
  }
  const pages = new Set([1, pageCount, page - 1, page, page + 1])
  const list = [...pages].filter((value) => value >= 1 && value <= pageCount).sort((a, b) => a - b)
  const result = []
  list.forEach((value, index) => {
    if (index > 0 && value - list[index - 1] > 1) result.push('...')
    result.push(value)
  })
  return result
}

/** 删除或筛选后保持选中项落在可见范围内 */
export function resolveSelectedId(items, previousId) {
  if (items.some((item) => item.id === previousId)) return previousId
  return items.length ? items[0].id : null
}
