// Keyboard handling for role="tablist" (WAI-ARIA tabs pattern, automatic activation):
// Left/Right move between tabs and wrap, Home/End jump to the ends.
// Steps from the focused tab, not the selected one: an autoplaying tablist can
// change the selection while focus stays put.
// Returns the index to select, or null for keys the tablist doesn't handle.
export function tabKeyTarget(e: KeyboardEvent): number | null {
  const tab = e.currentTarget as HTMLElement
  const tabs = [...(tab.parentElement?.querySelectorAll<HTMLElement>('[role="tab"]') ?? [])]
  const current = tabs.indexOf(tab)
  const last = tabs.length - 1
  const next: Record<string, number> = {
    ArrowRight: current === last ? 0 : current + 1,
    ArrowLeft: current === 0 ? last : current - 1,
    Home: 0,
    End: last,
  }
  if (current < 0 || !(e.key in next)) return null
  e.preventDefault()
  tabs[next[e.key]].focus()
  return next[e.key]
}
