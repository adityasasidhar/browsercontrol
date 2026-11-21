<script setup lang="ts">
import { computed, nextTick, onMounted, ref, useId, watch } from 'vue'
import { tabKeyTarget } from '../tabs'

interface Option {
  id: string
  label: string
  lines: string[]
  note: string
}

const options: Option[] = [
  {
    id: 'claude',
    label: 'Claude Code',
    lines: [
      '/plugin marketplace add adityasasidhar/browsercontrol',
      '/plugin install browsercontrol@browsercontrol',
    ],
    note: 'Installs the MCP server and the agent skill together.',
  },
  {
    id: 'cli',
    label: 'Claude CLI',
    lines: ['claude mcp add --transport stdio browsercontrol -- uvx browsercontrol'],
    note: 'Adds the MCP server only. Needs uv on your PATH.',
  },
  {
    id: 'codex',
    label: 'Codex',
    lines: [
      'codex plugin marketplace add adityasasidhar/browsercontrol',
      'codex plugin add browsercontrol@browsercontrol',
    ],
    note: 'Installs the MCP server and the agent skill together. Needs uv on your PATH.',
  },
  {
    id: 'opencode',
    label: 'OpenCode',
    lines: ['opencode plugin add github:adityasasidhar/browsercontrol'],
    note: 'Needs OpenCode 2.3.2 or later. Loads the MCP server and the agent skill.',
  },
  {
    id: 'hermes',
    label: 'Hermes',
    lines: ['hermes mcp add browsercontrol --command uvx --args browsercontrol'],
    note: 'Adds the MCP server only. Needs uv on your PATH.',
  },
  {
    id: 'openclaw',
    label: 'OpenClaw',
    lines: ['openclaw mcp add browsercontrol --command uvx --arg browsercontrol'],
    note: 'Adds the MCP server only. Needs uv on your PATH.',
  },
  {
    id: 'uvx',
    label: 'Any client',
    lines: ['uvx browsercontrol'],
    note: 'Set this as the command in any MCP client.',
  },
  {
    id: 'pip',
    label: 'pip',
    lines: ['pip install browsercontrol'],
    note: 'Then use browsercontrol as the command.',
  },
]

const active = ref(options[0].id)
const copied = ref(false)
const current = computed(() => options.find((o) => o.id === active.value)!)
const tabsEl = ref<HTMLElement>()
const indicator = ref({ left: 0, top: 0, width: 0, height: 0 })

function place() {
  const el = tabsEl.value?.querySelector<HTMLElement>(`[data-id="${active.value}"]`)
  if (el) indicator.value = {
    left: el.offsetLeft,
    top: el.offsetTop,
    width: el.offsetWidth,
    height: el.offsetHeight,
  }
}

onMounted(() => {
  place()
  document.fonts?.ready.then(place)
})
watch(active, () => nextTick(place))

// The home page renders this component twice, so ids must be per instance.
const uid = useId()

function onTabKey(e: KeyboardEvent) {
  const next = tabKeyTarget(e)
  if (next !== null) active.value = options[next].id
}

async function copy() {
  await navigator.clipboard.writeText(current.value.lines.join('\n'))
  copied.value = true
  setTimeout(() => (copied.value = false), 1600)
}
</script>

<template>
  <div class="install vp-raw">
    <div ref="tabsEl" class="install-tabs" role="tablist" aria-label="Install method">
      <span class="install-indicator" :style="{ transform: `translate(${indicator.left}px, ${indicator.top}px)`, width: `${indicator.width}px`, height: `${indicator.height}px` }" />
      <button
        v-for="o in options"
        :key="o.id"
        :id="`${uid}-tab-${o.id}`"
        :data-id="o.id"
        role="tab"
        :aria-selected="active === o.id"
        :aria-controls="`${uid}-panel`"
        :tabindex="active === o.id ? 0 : -1"
        :class="{ active: active === o.id }"
        @click="active = o.id"
        @keydown="onTabKey"
      >
        {{ o.label }}
      </button>
    </div>
    <div :id="`${uid}-panel`" class="install-body" role="tabpanel" :aria-labelledby="`${uid}-tab-${active}`">
      <Transition name="install-swap" mode="out-in">
        <pre :key="active"><code><span v-for="line in current.lines" :key="line" class="line"><span class="prompt">{{ line.startsWith('/') ? '›' : '$' }}</span>{{ line }}</span></code></pre>
      </Transition>
      <button class="install-copy" :aria-label="copied ? 'Copied' : 'Copy command'" @click="copy">
        <svg v-if="!copied" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M5 15V6a2 2 0 0 1 2-2h9" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>
        <svg v-else viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </button>
    </div>
    <p class="install-note">{{ current.note }}</p>
  </div>
</template>

<style scoped>
.install {
  min-width: 0;
  border: 1px solid var(--bc-line);
  border-radius: var(--bc-radius);
  background: var(--vp-c-bg);
  box-shadow: var(--bc-shadow);
  overflow: hidden;
  max-width: 560px;
}
.install-tabs {
  position: relative;
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  padding: 6px;
  border-bottom: 1px solid var(--bc-line);
  background: var(--vp-c-bg-alt);
}
.install-tabs button {
  position: relative;
  z-index: 1;
  padding: 5px 11px;
  font-size: 13px;
  font-weight: 550;
  color: var(--vp-c-text-2);
  border-radius: 7px;
  white-space: nowrap;
  transition: color 0.2s;
}
.install-tabs button:hover,
.install-tabs button.active {
  color: var(--vp-c-text-1);
}
.install-indicator {
  position: absolute;
  top: 0;
  left: 0;
  border-radius: 7px;
  background: var(--vp-c-bg);
  border: 1px solid var(--bc-line);
  box-shadow: 0 1px 2px color-mix(in srgb, var(--vp-c-text-1) 8%, transparent);
  transition:
    transform 0.35s var(--bc-ease),
    width 0.35s var(--bc-ease);
}
.install-body {
  position: relative;
  padding: 14px 48px 14px 16px;
  min-height: 74px;
  display: flex;
  align-items: center;
}
pre {
  margin: 0;
  overflow-x: auto;
  scrollbar-width: thin;
}
code {
  font-family: var(--vp-font-family-mono);
  font-size: 13.5px;
  line-height: 1.75;
  color: var(--vp-c-text-1);
}
.line {
  display: block;
  white-space: pre;
}
.prompt {
  color: var(--bc-mark);
  margin-right: 10px;
  user-select: none;
}
.install-copy {
  position: absolute;
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  color: var(--vp-c-text-2);
  border: 1px solid transparent;
  transition: all 0.2s;
}
.install-copy:hover {
  color: var(--vp-c-text-1);
  border-color: var(--bc-line);
  background: var(--vp-c-bg-alt);
}
.install-note {
  margin: 0;
  padding: 8px 16px 10px;
  font-size: 12.5px;
  color: var(--vp-c-text-3);
  border-top: 1px dashed var(--bc-line);
}
.install-swap-enter-active,
.install-swap-leave-active {
  transition:
    opacity 0.18s,
    transform 0.18s var(--bc-ease),
    filter 0.18s;
}
.install-swap-enter-from {
  opacity: 0;
  transform: translateY(4px);
  filter: blur(2px);
}
.install-swap-leave-to {
  opacity: 0;
  transform: translateY(-4px);
  filter: blur(2px);
}
</style>
