import { computed, ref } from 'vue'

const width = ref(typeof window === 'undefined' ? 1280 : window.innerWidth)
let initialized = false

function init() {
  if (initialized || typeof window === 'undefined') return
  initialized = true
  window.addEventListener('resize', () => {
    width.value = window.innerWidth
  })
}

/**
 * 断点：xl ≥1280（三栏）| lg 1024–1279（抽屉）| md 768–1023（图标侧栏）| sm <768（预留）
 */
export function useBreakpoint() {
  init()

  const breakpoint = computed(() => {
    if (width.value >= 1280) return 'xl'
    if (width.value >= 1024) return 'lg'
    if (width.value >= 768) return 'md'
    return 'sm'
  })

  const isDesktop = computed(() => breakpoint.value === 'xl')
  const isDrawerMode = computed(() => breakpoint.value !== 'xl')
  const isRail = computed(() => breakpoint.value === 'md' || breakpoint.value === 'sm')
  const isCompact = computed(() => breakpoint.value !== 'xl')

  return { width, breakpoint, isDesktop, isDrawerMode, isRail, isCompact }
}
