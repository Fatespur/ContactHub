<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '@/components/common/AppIcon.vue'
import { useContactStore } from '@/stores/contactStore'
import { useBreakpoint } from '@/composables/useBreakpoint'

const route = useRoute()
const router = useRouter()
const { state, showAll, showFavorites, setGroup } = useContactStore()
const { isRail } = useBreakpoint()

const groupOpen = ref(true)
const groupPopover = ref(false)

const onContactPage = computed(() => route.name === 'contacts')
const isAllActive = computed(
  () => onContactPage.value && !state.favoriteOnly && !state.group
)
const isFavoriteActive = computed(
  () => onContactPage.value && state.favoriteOnly && !state.group
)
const isSettingsActive = computed(() => route.name === 'settings')

function ensureContactPage() {
  if (!onContactPage.value) router.push('/')
}

function handleAll() {
  ensureContactPage()
  showAll()
}

function handleFavorites() {
  ensureContactPage()
  showFavorites()
}

function handleGroup(name) {
  ensureContactPage()
  setGroup(state.group === name ? '' : name)
}

function toggleGroups() {
  if (isRail.value) return
  groupOpen.value = !groupOpen.value
}

function pickGroup(name) {
  handleGroup(name)
  groupPopover.value = false
}

function handleSettings() {
  router.push('/settings')
}
</script>

<template>
  <aside class="sidebar">
    <nav class="nav">
      <el-tooltip content="全部联系人" placement="right" :disabled="!isRail" :show-after="200">
        <button
          class="nav-item"
          :class="{ 'is-active': isAllActive }"
          type="button"
          @click="handleAll"
        >
          <AppIcon name="users" :size="17" />
          <span class="label">全部联系人</span>
        </button>
      </el-tooltip>

      <el-tooltip content="我的收藏" placement="right" :disabled="!isRail" :show-after="200">
        <button
          class="nav-item"
          :class="{ 'is-active': isFavoriteActive }"
          type="button"
          @click="handleFavorites"
        >
          <AppIcon name="star" :size="17" />
          <span class="label">我的收藏</span>
        </button>
      </el-tooltip>

      <el-popover
        v-model:visible="groupPopover"
        :disabled="!isRail"
        placement="right-start"
        :width="190"
        trigger="click"
        popper-class="rail-groups-popover"
      >
        <template #reference>
          <button
            class="nav-item nav-group-head"
            :class="{ 'is-open': groupOpen }"
            type="button"
            @click="toggleGroups"
          >
            <AppIcon name="tag" :size="17" />
            <span class="label">分组管理</span>
            <AppIcon
              :name="groupOpen ? 'chevron-up' : 'chevron-down'"
              :size="14"
              class="chevron"
            />
          </button>
        </template>

        <div class="rail-groups">
          <div class="rail-title">分组筛选</div>
          <button
            v-for="group in state.groups"
            :key="group.name"
            class="rail-group-item"
            :class="{ 'is-active': state.group === group.name }"
            type="button"
            @click="pickGroup(group.name)"
          >
            <span>{{ group.name }}</span>
            <span class="count">{{ group.count }}</span>
          </button>
        </div>
      </el-popover>

      <div v-show="groupOpen" class="nav-sub">
        <button
          v-for="group in state.groups"
          :key="group.name"
          class="nav-item"
          :class="{ 'is-active': onContactPage && state.group === group.name }"
          type="button"
          @click="handleGroup(group.name)"
        >
          <span class="label">{{ group.name }}</span>
          <span class="nav-count">{{ group.count }}</span>
        </button>
      </div>
    </nav>

    <div class="nav-divider" />

    <nav class="nav">
      <el-tooltip content="系统设置" placement="right" :disabled="!isRail" :show-after="200">
        <button
          class="nav-item"
          :class="{ 'is-active': isSettingsActive }"
          type="button"
          @click="handleSettings"
        >
          <AppIcon name="settings" :size="17" />
          <span class="label">系统设置</span>
        </button>
      </el-tooltip>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  flex: none;
  padding: 10px 0 0 14px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 42px;
  padding: 0 12px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: var(--color-ink-2);
  font-size: 14px;
  text-align: left;
  transition: background 0.16s, color 0.16s;
}

.nav-item :deep(.app-icon) {
  color: #7d8a99;
}

.nav-item .label {
  flex: 1;
  white-space: nowrap;
}

.nav-item:hover {
  background: #f1f4f8;
}

.nav-item.is-active {
  background: var(--color-primary-soft);
  color: #4f6f8f;
  font-weight: 600;
}

.nav-item.is-active :deep(.app-icon) {
  color: #5b7a99;
}

.nav-group-head {
  width: 100%;
}

.nav-group-head .chevron {
  color: var(--color-ink-4);
  transition: transform 0.2s;
}

.nav-sub {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-sub .nav-item {
  height: 38px;
  padding-left: 41px;
  padding-right: 12px;
  font-size: 13.5px;
}

.nav-count {
  font-size: 12.5px;
  color: var(--color-ink-4);
  font-variant-numeric: tabular-nums;
}

.nav-item.is-active .nav-count {
  color: #7d97b2;
}

.nav-divider {
  height: 1px;
  background: var(--color-line);
  margin: 12px 4px 10px;
}

@media (max-width: 1023px) {
  .sidebar {
    width: 64px;
    padding: 0;
    align-items: center;
  }

  .nav {
    width: 100%;
    align-items: center;
  }

  .nav-item {
    width: 44px;
    height: 40px;
    padding: 0;
    justify-content: center;
    border-radius: 9px;
  }

  .nav-item .label,
  .nav-item .nav-count,
  .nav-item .chevron {
    display: none;
  }

  .nav-sub {
    display: none;
  }

  .nav-divider {
    width: 32px;
    margin: 10px auto;
  }
}
</style>

<style>
.rail-groups-popover {
  padding: 8px !important;
}

.rail-groups {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rail-groups .rail-title {
  padding: 4px 8px 6px;
  font-size: 12px;
  color: #8b97a5;
}

.rail-groups .rail-group-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 32px;
  padding: 0 8px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--color-ink-2);
  font-size: 13px;
  cursor: pointer;
}

.rail-groups .rail-group-item:hover {
  background: #f2f5f9;
}

.rail-groups .rail-group-item.is-active {
  background: var(--color-primary-soft);
  color: #4f6f8f;
  font-weight: 600;
}

.rail-groups .count {
  font-size: 12px;
  color: var(--color-ink-4);
}
</style>
