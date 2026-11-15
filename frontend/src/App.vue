<script setup>
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import IconSprite from '@/components/common/IconSprite.vue'
</script>

<template>
  <div class="app-shell">
    <IconSprite />
    <AppHeader />
    <div class="app-body">
      <AppSidebar />
      <router-view />
    </div>
  </div>
</template>
