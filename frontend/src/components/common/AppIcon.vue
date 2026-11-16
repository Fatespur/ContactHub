<script setup>
defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 16 }
})
</script>

<template>
  <svg class="app-icon" :width="size" :height="size" aria-hidden="true" focusable="false">
    <use :href="`#icon-${name}`" />
  </svg>
</template>
