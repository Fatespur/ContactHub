<script setup>
import AppIcon from '@/components/common/AppIcon.vue'

defineProps({
  active: { type: Boolean, default: false },
  size: { type: Number, default: 16 }
})

const emit = defineEmits(['toggle'])
</script>

<template>
  <button
    type="button"
    class="star-button"
    :class="{ 'is-on': active }"
    :aria-pressed="active ? 'true' : 'false'"
    :aria-label="active ? '取消收藏' : '收藏'"
    @click.stop="emit('toggle')"
  >
    <AppIcon name="star" :size="size" />
  </button>
</template>

<style scoped>
.star-button {
  border: 0;
  background: transparent;
  padding: 2px;
  display: grid;
  place-items: center;
  color: var(--color-star-idle);
  transition: color 0.16s, transform 0.16s;
}

.star-button :deep(.app-icon) {
  fill: none;
}

.star-button:hover {
  transform: scale(1.12);
}

.star-button.is-on {
  color: var(--color-star);
}

.star-button.is-on :deep(.app-icon) {
  fill: var(--color-star);
}
</style>
