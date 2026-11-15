<script setup>
defineProps({
  drawer: { type: Boolean, default: false }
})
</script>

<template>
  <div class="detail-skeleton" :class="{ 'is-drawer': drawer }" aria-busy="true" aria-label="正在加载详情">
    <div class="ds-head">
      <span class="ds-avatar" />
      <div class="ds-head-main">
        <span class="ds-bar w90 h14" />
        <span class="ds-bar w46 h18 mt8" />
      </div>
    </div>

    <div class="ds-section">
      <span class="ds-bar w64 h12" />
      <div class="ds-row"><span class="ds-bar w34 h10" /><span class="ds-bar w120 h10" /></div>
      <div class="ds-row"><span class="ds-bar w34 h10" /><span class="ds-bar w80 h10" /></div>
    </div>

    <div class="ds-divider" />

    <div class="ds-section">
      <span class="ds-bar w72 h12" />
      <div class="ds-row"><span class="ds-dot" /><span class="ds-bar w120 h10" /></div>
      <div class="ds-row"><span class="ds-dot" /><span class="ds-bar w96 h10" /></div>
    </div>

    <div class="ds-section">
      <span class="ds-bar w64 h12" />
      <div class="ds-row"><span class="ds-bar w16 h16" /><span class="ds-bar w130 h10" /></div>
    </div>

    <div class="ds-section">
      <span class="ds-bar w72 h12" />
      <div class="ds-row"><span class="ds-bar w16 h16" /><span class="ds-bar w110 h10" /></div>
    </div>
  </div>
</template>

<style scoped>
.detail-skeleton {
  padding: 4px 2px;
}

.ds-head {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ds-avatar {
  width: 56px;
  height: 56px;
  flex: none;
  border-radius: 50%;
  background: var(--skeleton-base, #eef2f7);
  animation: ds-pulse 1.4s ease-in-out infinite;
}

.ds-head-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ds-section {
  margin-top: 26px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ds-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ds-divider {
  height: 1px;
  background: var(--color-line);
  margin-top: 24px;
}

.ds-bar,
.ds-dot {
  display: block;
  height: 10px;
  background: var(--skeleton-base, #eef2f7);
  border-radius: 4px;
  animation: ds-pulse 1.4s ease-in-out infinite;
}

.ds-bar.w34 {
  width: 34px;
}

.ds-bar.w46 {
  width: 46px;
}

.ds-bar.w64 {
  width: 64px;
}

.ds-bar.w72 {
  width: 72px;
}

.ds-bar.w80 {
  width: 80px;
}

.ds-bar.w90 {
  width: 90px;
}

.ds-bar.w96 {
  width: 96px;
}

.ds-bar.w110 {
  width: 110px;
}

.ds-bar.w120 {
  width: 120px;
}

.ds-bar.w130 {
  width: 130px;
}

.ds-bar.h12 {
  height: 12px;
}

.ds-bar.h14 {
  height: 14px;
}

.ds-bar.h18 {
  height: 18px;
  border-radius: 5px;
}

.ds-bar.w16 {
  width: 16px;
  height: 16px;
}

.ds-bar.mt8 {
  margin-top: 2px;
}

.ds-dot {
  width: 6px;
  height: 6px;
  flex: none;
  border-radius: 50%;
}

@keyframes ds-pulse {
  0%,
  100% {
    opacity: 0.55;
  }
  50% {
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .ds-avatar,
  .ds-bar,
  .ds-dot {
    animation: none;
  }
}
</style>
