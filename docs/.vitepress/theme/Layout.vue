<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'
import { useData, withBase } from 'vitepress'
import { nextTick, onMounted, provide } from 'vue'
import { redirectFor } from './redirects'

const { isDark, page, site } = useData()

// Forward addresses from the old site to their new pages.
onMounted(() => {
  if (!page.value.isNotFound) return
  const base = site.value.base
  const path = location.pathname.startsWith(base) ? location.pathname.slice(base.length) : location.pathname
  const target = redirectFor('/' + path)
  if (target && target !== '/' + path) {
    location.replace(withBase(target) + location.hash)
  }
})

// Circular reveal when switching light/dark, using the View Transitions API.
const canTransition = () =>
  typeof document !== 'undefined' &&
  'startViewTransition' in document &&
  !window.matchMedia('(prefers-reduced-motion: reduce)').matches

provide('toggle-appearance', async ({ clientX: x, clientY: y }: MouseEvent) => {
  if (!canTransition()) {
    isDark.value = !isDark.value
    return
  }
  const radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y))
  const clipPath = [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`]
  await (document as Document & { startViewTransition: (cb: () => Promise<void>) => { ready: Promise<void> } })
    .startViewTransition(async () => {
      isDark.value = !isDark.value
      await nextTick()
    }).ready
  document.documentElement.animate(
    { clipPath: isDark.value ? clipPath.reverse() : clipPath },
    {
      duration: 420,
      easing: 'cubic-bezier(.2,.7,.2,1)',
      fill: 'forwards',
      pseudoElement: `::view-transition-${isDark.value ? 'old' : 'new'}(root)`,
    },
  )
})
</script>

<template>
  <DefaultTheme.Layout />
</template>

<style>
::view-transition-old(root),
::view-transition-new(root) {
  animation: none;
  mix-blend-mode: normal;
}
::view-transition-old(root),
.dark::view-transition-new(root) {
  z-index: 1;
}
::view-transition-new(root),
.dark::view-transition-old(root) {
  z-index: 9999;
}
</style>
