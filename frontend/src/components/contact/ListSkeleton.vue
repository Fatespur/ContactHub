<script setup>
defineProps({
  compact: { type: Boolean, default: false }
})
</script>

<template>
  <div class="list-skeleton" aria-busy="true" aria-label="正在加载联系人">
    <div class="sk-head" :class="{ 'is-compact': compact }">
      <span />
      <span>姓名</span>
      <span>分组</span>
      <span>主要联系方式</span>
      <span v-if="!compact">其他联系方式</span>
      <span v-if="!compact">备注</span>
      <span>收藏</span>
      <span>操作</span>
    </div>

    <div v-for="index in 8" :key="index" class="sk-row" :class="{ 'is-compact': compact }">
      <span class="sk-cell"><span class="sk-box" /></span>
      <span class="sk-cell"><span class="sk-avatar" /><span class="sk-bar w56" /></span>
      <span class="sk-cell"><span class="sk-bar w40" /></span>
      <span class="sk-cell"><span class="sk-bar w90" /></span>
      <span v-if="!compact" class="sk-cell"><span class="sk-bar w120" /></span>
      <span v-if="!compact" class="sk-cell"><span class="sk-bar w36" /></span>
      <span class="sk-cell"><span class="sk-dot" /></span>
      <span class="sk-cell"><span class="sk-bar w18" /><span class="sk-bar w18" /></span>
    </div>
  </div>
</template>

<style scoped>
.list-skeleton {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding-right: 2px;
}

.sk-head,
.sk-row {
  display: grid;
  align-items: center;
  grid-template-columns: 32px 120px 66px 134px minmax(0, 1fr) 70px 44px 58px;
}

.sk-head.is-compact,
.sk-row.is-compact {
  grid-template-columns: 30px 116px minmax(0, 1fr) 60px 38px 54px;
}

.sk-head {
  height: 32px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--color-line);
  font-size: 13px;
  font-weight: 600;
  color: #37455a;
}

.sk-head.is-compact {
  height: 30px;
  font-size: 12.5px;
}

.sk-head span {
  padding-right: 10px;
}

.sk-row {
  height: 58px;
  border-bottom: 1px solid #f3f5f8;
}

.sk-row.is-compact {
  height: 54px;
}

.sk-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  padding-right: 10px;
}

.sk-box,
.sk-avatar,
.sk-bar,
.sk-dot {
  position: relative;
  display: block;
  flex: none;
  overflow: hidden;
  background: var(--skeleton-base, #eef2f7);
  border-radius: 4px;
  animation: skeleton-pulse 1.4s ease-in-out infinite;
}

.sk-box {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.sk-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
}

.sk-bar {
  height: 10px;
}

.sk-bar.w36 {
  width: 36px;
}

.sk-bar.w40 {
  width: 40px;
}

.sk-bar.w56 {
  width: 56px;
}

.sk-bar.w90 {
  width: 90px;
}

.sk-bar.w120 {
  width: 120px;
}

.sk-bar.w18 {
  width: 18px;
  height: 18px;
  border-radius: 5px;
}

.sk-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
}

@keyframes skeleton-pulse {
  0%,
  100% {
    opacity: 0.55;
  }
  50% {
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .sk-box,
  .sk-avatar,
  .sk-bar,
  .sk-dot {
    animation: none;
  }
}
</style>
