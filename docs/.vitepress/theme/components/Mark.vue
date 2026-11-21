<script setup lang="ts">
// An inline Set of Marks label: <Mark n="7">Submit</Mark>
defineProps<{ n: string | number }>()
</script>

<template>
  <span class="bc-mark"><span class="bc-mark-n">{{ n }}</span><slot /></span>
</template>

<style scoped>
.bc-mark {
  position: relative;
  display: inline-block;
  padding: 0 0.3em;
  margin: 0 0.15em 0 0.5em;
  border: 1.5px solid var(--bc-mark);
  border-radius: 4px;
  line-height: 1.35;
  background: var(--bc-mark-soft);
}
.bc-mark-n {
  position: absolute;
  top: -0.55em;
  left: -0.7em;
  min-width: 1.35em;
  padding: 0 0.25em;
  font-family: var(--vp-font-family-mono);
  font-size: 0.65em;
  font-weight: 700;
  line-height: 1.4;
  text-align: center;
  color: var(--vp-c-bg);
  background: var(--bc-mark);
  border-radius: 3px;
}
</style>
