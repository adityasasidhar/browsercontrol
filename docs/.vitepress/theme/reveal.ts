import type { Directive } from 'vue'

/**
 * v-reveal: fade an element up into place the first time it scrolls into view.
 * v-reveal="120" delays it by 120 ms, for staggering siblings.
 * Respects prefers-reduced-motion (the element is simply shown).
 */
export const reveal: Directive<HTMLElement, number | undefined> = {
  mounted(el, binding) {
    el.classList.add('reveal')
    if (binding.value) el.style.setProperty('--reveal-delay', `${binding.value}ms`)
    if (
      typeof IntersectionObserver === 'undefined' ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ) {
      el.classList.add('is-visible')
      return
    }
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            el.classList.add('is-visible')
            observer.disconnect()
          }
        }
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.08 },
    )
    observer.observe(el)
  },
}

/** Run `cb(true)` while `el` is on screen and `cb(false)` when it leaves. */
export function onVisible(el: Element, cb: (visible: boolean) => void): () => void {
  if (typeof IntersectionObserver === 'undefined') {
    cb(true)
    return () => {}
  }
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) cb(entry.isIntersecting)
  })
  observer.observe(el)
  return () => observer.disconnect()
}

export function prefersReducedMotion(): boolean {
  return typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}
