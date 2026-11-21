<script setup lang="ts">
import { withBase } from 'vitepress'
import { computed } from 'vue'

const props = defineProps<{ title: string; link: string; icon?: string }>()
const href = computed(() => (/^https?:/.test(props.link) ? props.link : withBase(props.link)))
</script>

<template>
  <a class="bc-card" :href="href">
    <span v-if="icon" class="bc-card-icon" aria-hidden="true">{{ icon }}</span>
    <span class="bc-card-title">{{ title }} <span class="bc-card-arrow" aria-hidden="true">→</span></span>
    <span class="bc-card-body"><slot /></span>
  </a>
</template>

<style scoped>
.bc-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px 18px;
  border: 1px solid var(--bc-line);
  border-radius: var(--bc-radius);
  background: var(--vp-c-bg);
  text-decoration: none !important;
  transition:
    border-color 0.2s,
    transform 0.25s var(--bc-ease),
    box-shadow 0.25s;
}
.bc-card:hover {
  border-color: var(--bc-mark);
  transform: translateY(-2px);
  box-shadow: var(--bc-shadow);
}
.bc-card-icon {
  font-family: var(--vp-font-family-mono);
  font-size: 12px;
  font-weight: 700;
  color: var(--bc-mark);
  margin-bottom: 4px;
}
.bc-card-title {
  font-weight: 620;
  color: var(--vp-c-text-1);
  letter-spacing: -0.01em;
}
.bc-card-arrow {
  display: inline-block;
  color: var(--vp-c-text-3);
  transition: transform 0.25s var(--bc-ease), color 0.2s;
}
.bc-card:hover .bc-card-arrow {
  transform: translateX(3px);
  color: var(--bc-mark);
}
.bc-card-body {
  font-size: 14px;
  line-height: 1.55;
  color: var(--vp-c-text-2);
  font-weight: 400;
}
</style>
