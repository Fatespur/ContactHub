<script setup>
defineProps({
  text: { type: String, default: '' }
})
</script>

<template>
  <span class="group-tag">{{ text }}</span>
</template>

<style scoped>
.group-tag {
  display: inline-flex;
  align-items: center;
  height: 22px;
  padding: 0 8px;
  border-radius: 5px;
  background: var(--color-tag-bg);
  color: var(--color-tag-text);
  font-size: 12px;
  white-space: nowrap;
}
</style>
