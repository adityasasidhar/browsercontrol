// Keyboard handling for role="tablist" (WAI-ARIA tabs pattern, automatic activation):
// Left/Right move between tabs and wrap, Home/End jump to the ends.
// Returns the index to select, or null for keys the tablist doesn't handle.
export function tabKeyTarget(e: KeyboardEvent, current: number, count: number): number | null {
  const last = count - 1
  const next: Record<string, number> = {
    ArrowRight: current === last ? 0 : current + 1,
    ArrowLeft: current === 0 ? last : current - 1,
    Home: 0,
    End: last,
  }
  if (!(e.key in next)) return null
  e.preventDefault()
  const tabs = (e.currentTarget as HTMLElement).parentElement?.querySelectorAll<HTMLElement>('[role="tab"]')
  tabs?.[next[e.key]]?.focus()
  return next[e.key]
}
