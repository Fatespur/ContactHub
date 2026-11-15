<script setup>
import { computed } from 'vue'
import { initials } from '@/utils/contact'

const props = defineProps({
  name: { type: String, default: '' },
  size: { type: Number, default: 30 },
  tone: { type: String, default: 'list' }
})

const letter = computed(() => initials(props.name))
const style = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  fontSize: `${Math.round(props.size * 0.44)}px`
}))
</script>

<template>
  <span class="contact-avatar" :class="`contact-avatar--${tone}`" :style="style">
    {{ letter }}
  </span>
</template>

<style scoped>
.contact-avatar {
  display: grid;
  place-items: center;
  flex: none;
  border-radius: 50%;
  color: #fff;
  font-weight: 500;
  line-height: 1;
  user-select: none;
}

.contact-avatar--list {
  background: var(--color-avatar);
}

.contact-avatar--detail {
  background: var(--color-avatar-detail);
  box-shadow: 0 2px 8px rgba(92, 118, 145, 0.22);
}
</style>
