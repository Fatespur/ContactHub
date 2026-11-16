<script setup>
import AppIcon from '@/components/common/AppIcon.vue'
</script>

<template>
  <header class="topbar">
    <div class="brand">
      <div class="brand-logo">
        <AppIcon name="users" :size="22" />
      </div>
      <div class="brand-text">
        <h1>通讯录管理系统</h1>
        <p>AddressBook</p>
      </div>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  height: var(--header-height);
  flex: none;
  display: flex;
  align-items: center;
  padding: 0 22px 0 32px;
  background: var(--color-surface);
  border-bottom: 1px solid #e9eaed;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(150deg, #8ba1ba 0%, #6d88a6 100%);
  display: grid;
  place-items: center;
  color: #fff;
  box-shadow: 0 2px 6px rgba(104, 131, 160, 0.35);
}

.brand-logo :deep(.app-icon) {
  color: #fff;
}

.brand-text h1 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  line-height: 20px;
  letter-spacing: 0.3px;
  color: var(--color-ink);
}

.brand-text p {
  margin: 2px 0 0;
  font-size: 11px;
  line-height: 14px;
  letter-spacing: 0.6px;
  color: var(--color-ink-4);
}

@media (max-width: 1023px) {
  .topbar {
    height: 64px;
    padding: 0 14px 0 16px;
  }

  .brand {
    gap: 10px;
  }

  .brand-logo {
    width: 32px;
    height: 32px;
    border-radius: 8px;
  }

  .brand-text h1 {
    font-size: 15px;
    line-height: 18px;
  }

  .brand-text p {
    display: none;
  }
}
</style>
