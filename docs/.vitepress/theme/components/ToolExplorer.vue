<script setup lang="ts">
import { withBase } from 'vitepress'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { data } from '../tools.data'

const query = ref('')
const category = ref('All')
const open = ref<string | null>(null)
const input = ref<HTMLInputElement>()

const categories = computed(() => {
  const counts = new Map<string, number>()
  for (const t of data.tools) counts.set(t.category, (counts.get(t.category) ?? 0) + 1)
  return [['All', data.tools.length] as const, ...counts.entries()]
})

const results = computed(() => {
  const q = query.value.trim().toLowerCase()
  return data.tools.filter((t) => {
    if (category.value !== 'All' && t.category !== category.value) return false
    if (!q) return true
    const haystack = [t.name, t.summary, t.details, t.category, ...t.params.map((p) => p.name)]
      .join(' ')
      .toLowerCase()
    return q.split(/\s+/).every((word) => haystack.includes(word))
  })
})

function fmtDefault(value: unknown): string {
  if (value === null || value === undefined) return 'None'
  if (typeof value === 'string') return `"${value}"`
  if (typeof value === 'boolean') return value ? 'True' : 'False'
  return String(value)
}

function onKey(e: KeyboardEvent) {
  const target = e.target as HTMLElement
  if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(target.tagName)) {
    e.preventDefault()
    input.value?.focus()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
  const q = new URLSearchParams(location.search).get('q')
  if (q) query.value = q
})
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <div class="explorer vp-raw">
    <div class="explorer-search">
      <svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M20 20l-3.5-3.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
      <input
        ref="input"
        v-model="query"
        type="search"
        placeholder="Search 69 tools: “upload”, “dialog”, “mock”…"
        aria-label="Search tools"
      />
      <kbd aria-hidden="true">/</kbd>
    </div>

    <div class="explorer-chips" role="group" aria-label="Filter by category">
      <button
        v-for="[name, count] in categories"
        :key="name"
        :class="{ active: category === name }"
        :aria-pressed="category === name"
        @click="category = name"
      >
        {{ name }} <span>{{ count }}</span>
      </button>
    </div>

    <p class="explorer-count" aria-live="polite">
      {{ results.length }} {{ results.length === 1 ? 'tool' : 'tools' }}
    </p>

    <TransitionGroup name="row" tag="ul" class="explorer-list">
      <li v-for="t in results" :key="t.name" :class="{ open: open === t.name }">
        <button
          class="row-head"
          :aria-expanded="open === t.name"
          :aria-controls="`tool-${t.name}`"
          @click="open = open === t.name ? null : t.name"
        >
          <code class="row-name">{{ t.name }}</code>
          <span class="row-summary">{{ t.summary }}</span>
          <span class="row-tags">
            <span class="tag">{{ t.category }}</span>
            <span class="tag" :class="t.returns === 'text' ? 'tag-text' : 'tag-shot'">{{
              t.returns === 'text' ? 'text' : 'screenshot'
            }}</span>
          </span>
          <svg class="row-chevron" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
        <!-- inert keeps the collapsed body (and its link) out of the tab order -->
        <div :id="`tool-${t.name}`" class="row-body-wrap" :inert="open !== t.name">
          <div class="row-body">
            <pre class="row-sig"><code>{{ t.signature }}</code></pre>
            <p v-if="t.details" class="row-details">{{ t.details }}</p>
            <div v-if="t.params.length" class="row-params-scroll">
              <table class="row-params">
                <thead>
                  <tr><th>Parameter</th><th>Type</th><th>Default</th><th>Description</th></tr>
                </thead>
                <tbody>
                  <tr v-for="p in t.params" :key="p.name">
                    <td><code>{{ p.name }}</code></td>
                    <td><code>{{ p.type }}</code></td>
                    <td><code v-if="!p.required">{{ fmtDefault(p.default) }}</code><span v-else class="req">required</span></td>
                    <td>{{ p.description }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="row-details">No parameters.</p>
            <a class="row-link" :href="withBase(t.url)">Full reference →</a>
          </div>
        </div>
      </li>
    </TransitionGroup>
    <p v-if="!results.length" class="explorer-empty">
      No tool matches “{{ query }}”. Try a verb like <em>click</em>, <em>wait</em>, or <em>extract</em>.
    </p>
  </div>
</template>

<style scoped>
.explorer {
  margin: 28px 0 8px;
}
.explorer-search {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  height: 48px;
  border: 1px solid var(--bc-line-strong);
  border-radius: var(--bc-radius);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-3);
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}
.explorer-search:focus-within {
  border-color: var(--bc-mark);
  box-shadow: 0 0 0 4px var(--bc-mark-soft);
}
.explorer-search input {
  flex: 1;
  font-size: 15px;
  color: var(--vp-c-text-1);
  background: none;
}
.explorer-search kbd {
  font-family: var(--vp-font-family-mono);
  font-size: 12px;
  padding: 1px 7px;
  border: 1px solid var(--bc-line-strong);
  border-radius: 5px;
}
.explorer-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 14px 0 6px;
}
.explorer-chips button {
  font-size: 13px;
  font-weight: 500;
  padding: 4px 10px;
  border: 1px solid var(--bc-line);
  border-radius: 999px;
  color: var(--vp-c-text-2);
  transition: all 0.2s;
}
.explorer-chips button span {
  font-family: var(--vp-font-family-mono);
  font-size: 11px;
  color: var(--vp-c-text-3);
  margin-left: 2px;
}
.explorer-chips button:hover {
  border-color: var(--bc-line-strong);
  color: var(--vp-c-text-1);
}
.explorer-chips button.active {
  background: var(--vp-c-text-1);
  border-color: var(--vp-c-text-1);
  color: var(--vp-c-bg);
}
.explorer-chips button.active span {
  color: color-mix(in srgb, var(--vp-c-bg) 70%, transparent);
}
.explorer-count {
  font-size: 12.5px;
  color: var(--vp-c-text-3);
  margin: 10px 2px;
  font-family: var(--vp-font-family-mono);
}
.explorer-list {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid var(--bc-line);
  border-radius: var(--bc-radius);
  overflow: hidden;
}
.explorer-list li {
  border-bottom: 1px solid var(--bc-line);
  background: var(--vp-c-bg);
}
.explorer-list li:last-child {
  border-bottom: 0;
}
.row-head {
  width: 100%;
  display: grid;
  grid-template-columns: minmax(150px, 190px) 1fr auto 16px;
  align-items: center;
  gap: 14px;
  padding: 11px 14px;
  text-align: left;
  transition: background-color 0.15s;
}
.row-head:hover {
  background: var(--bc-surface);
}
.row-name,
.row-params code,
.row-sig code {
  background: none !important;
  border: 0 !important;
  padding: 0 !important;
  border-radius: 0 !important;
}
.row-name {
  justify-self: start;
  font-family: var(--vp-font-family-mono);
  font-size: 13.5px;
  font-weight: 600;
  color: var(--vp-c-text-1);
}
.row-summary {
  font-size: 14px;
  color: var(--vp-c-text-2);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.row-tags {
  display: flex;
  gap: 5px;
}
.tag {
  font-size: 11px;
  font-weight: 600;
  padding: 1px 7px;
  border-radius: 5px;
  color: var(--vp-c-text-2);
  background: var(--vp-c-bg-alt);
  white-space: nowrap;
}
.tag-shot {
  color: var(--bc-mark);
  background: var(--bc-mark-soft);
}
.tag-text {
  color: var(--bc-teal);
  background: color-mix(in srgb, var(--bc-teal) 12%, transparent);
}
.row-chevron {
  color: var(--vp-c-text-3);
  transition: transform 0.3s var(--bc-ease);
}
li.open .row-chevron {
  transform: rotate(90deg);
}
.row-body-wrap {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.35s var(--bc-ease);
}
li.open .row-body-wrap {
  grid-template-rows: 1fr;
}
.row-body {
  overflow: hidden;
  padding: 0 14px;
}
li.open .row-body {
  padding-bottom: 16px;
}
.row-sig {
  margin: 4px 0 12px;
  padding: 12px 14px;
  border-radius: var(--bc-radius-sm);
  background: var(--bc-surface);
  border: 1px solid var(--bc-line);
  overflow-x: auto;
}
.row-sig code {
  font-family: var(--vp-font-family-mono);
  font-size: 13px;
  color: var(--vp-c-text-1);
}
.row-details {
  font-size: 14px;
  line-height: 1.65;
  color: var(--vp-c-text-2);
  margin: 0 0 12px;
  white-space: pre-line;
}
.row-params-scroll {
  overflow-x: auto;
  margin-bottom: 12px;
}
.row-params {
  display: table !important;
  border: 0 !important;
  border-radius: 0 !important;
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
  margin: 0 !important;
}
.row-params td:last-child {
  min-width: 200px;
}
.row-params th {
  text-align: left;
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--vp-c-text-3);
  font-weight: 600;
  padding: 6px 8px;
  border-bottom: 1px solid var(--bc-line);
}
.row-params td {
  padding: 7px 8px;
  border-bottom: 1px solid var(--bc-line);
  vertical-align: top;
  color: var(--vp-c-text-2);
}
.row-params code {
  font-family: var(--vp-font-family-mono);
  font-size: 12.5px;
  color: var(--vp-c-text-1);
  white-space: nowrap;
}
.req {
  font-size: 12px;
  color: var(--bc-peach);
  font-weight: 600;
}
.row-link {
  font-size: 14px;
  font-weight: 550;
  color: var(--vp-c-brand-1);
}
.explorer-empty {
  text-align: center;
  padding: 24px;
  color: var(--vp-c-text-2);
}
.row-enter-active,
.row-leave-active {
  transition:
    opacity 0.25s,
    transform 0.25s var(--bc-ease);
}
.row-enter-from,
.row-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
.row-leave-active {
  position: absolute;
  width: 100%;
}
.row-move {
  transition: transform 0.3s var(--bc-ease);
}
@media (max-width: 640px) {
  .row-head {
    grid-template-columns: 1fr 16px;
  }
  .row-summary {
    grid-column: 1;
    white-space: normal;
  }
  .row-tags {
    display: none;
  }
}
</style>
