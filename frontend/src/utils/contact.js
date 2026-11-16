import { GROUP_PRESETS } from '@/constants/contact'

/** Get primary entry: prioritizes is_primary=true, falling back to the first item. */
export function primaryOf(list) {
  if (!Array.isArray(list) || list.length === 0) return null
  return list.find((item) => item.is_primary) || list[0]
}

/**
 * Resolves "other contact info" for table view in priority order: email > social > address.
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

/** First character of name, used to generate placeholder avatar. */
export function initials(name) {
  const text = String(name ?? '').trim()
  return text ? text.charAt(0) : '?'
}

/** Aggregate group statistics from full contacts list (independent of current filters). */
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

/** Pagination window: display all page numbers directly when count is small. */
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

/** Keep selected contact within visible range after deletion or filter change. */
export function resolveSelectedId(items, previousId) {
  if (items.some((item) => item.id === previousId)) return previousId
  return items.length ? items[0].id : null
}
