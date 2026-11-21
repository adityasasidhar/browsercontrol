<script setup lang="ts">
import { withBase } from 'vitepress'
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { onVisible, prefersReducedMotion } from '../../reveal'
import { tabKeyTarget } from '../../tabs'

const SITE = 'https://adityasasidhar.github.io/browsercontrol'

const shows = [
  {
    file: 'llms.txt',
    cmd: `curl ${SITE}/llms.txt`,
    out: [
      '# BrowserControl',
      '> A local MCP server for browser automation…',
      '- **Element IDs are ephemeral.** Rebuilt after',
      '  every action; act on the latest screenshot.',
      '## Get started',
      '- [Quickstart](…/guide/quickstart.md)',
    ],
  },
  {
    file: 'tools.json',
    cmd: `curl -s ${SITE}/tools.json | jq '.tools[] | select(.name == "click")'`,
    out: [
      '{',
      '  "name": "click",',
      '  "category": "Interaction",',
      '  "signature": "click(element_id: int)",',
      '  "returns": "text + screenshot",',
      '}',
    ],
  },
  {
    file: 'any page as .md',
    cmd: `curl ${SITE}/concepts/set-of-marks.md`,
    out: [
      '# Set of Marks',
      '',
      'Every annotated screenshot rebuilds the map.',
      'An ID is only valid against the screenshot',
      'it came from…',
      '',
    ],
  },
]

const index = ref(0)
const typed = ref('')
const shown = ref(0)
const el = ref<HTMLElement>()
let timer: ReturnType<typeof setTimeout> | undefined
let visible = false
let stop: () => void = () => {}

function schedule(fn: () => void, ms: number) {
  timer = setTimeout(() => (visible ? fn() : schedule(fn, 400)), ms)
}

function play(i: number) {
  index.value = i
  typed.value = ''
  shown.value = 0
  const cmd = shows[i].cmd
  let c = 0
  const typeNext = () => {
    typed.value = cmd.slice(0, ++c)
    if (c < cmd.length) schedule(typeNext, 18)
    else schedule(printNext, 250)
  }
  const printNext = () => {
    shown.value++
    if (shown.value < shows[i].out.length) schedule(printNext, 110)
    else schedule(() => play((i + 1) % shows.length), 3200)
  }
  schedule(typeNext, 300)
}

function pick(i: number) {
  clearTimeout(timer)
  play(i)
}

function onTabKey(e: KeyboardEvent) {
  const next = tabKeyTarget(e, index.value, shows.length)
  if (next !== null) pick(next)
}

onMounted(() => {
  if (prefersReducedMotion()) {
    typed.value = shows[0].cmd
    shown.value = shows[0].out.length
    return
  }
  stop = onVisible(el.value!, (v) => (visible = v))
  play(0)
})
onBeforeUnmount(() => {
  clearTimeout(timer)
  stop()
})

const items = [
  { title: 'llms.txt', body: 'A map of every page with a one-line summary, plus the two rules that matter most.', href: '/llms.txt' },
  { title: 'llms-full.txt', body: 'The entire documentation in one file, ready to drop into a context window.', href: '/llms-full.txt' },
  { title: 'Every page as Markdown', body: 'Add .md to any URL. Each page also has Copy page and Open in Claude buttons.', href: '/guide/quickstart.md' },
  { title: 'tools.json', body: 'All 69 tools with signatures and parameters, generated from the server itself.', href: '/tools.json' },
  { title: 'Agent skill', body: 'An operating playbook that loads only when the agent drives a browser.', href: '/guide/agent-skill' },
]
</script>

<template>
  <section ref="el" class="agents">
    <div class="agents-copy">
      <p class="eyebrow" v-reveal>For agents and humans</p>
      <h2 class="title" v-reveal="60">Docs your agent <em>can read too.</em></h2>
      <p class="lede" v-reveal="120">
        Everything here is published twice: as pages for you, and as plain text and JSON for the
        model doing the work.
      </p>
      <ul class="items">
        <li v-for="(it, i) in items" :key="it.title" v-reveal="160 + i * 60">
          <a :href="withBase(it.href)" :target="it.href.includes('.') ? '_blank' : undefined">
            <strong>{{ it.title }}</strong>
            <span>{{ it.body }}</span>
          </a>
        </li>
      </ul>
    </div>

    <div class="term" v-reveal="120">
      <div class="term-tabs" role="tablist" aria-label="Machine-readable files">
        <button
          v-for="(s, i) in shows"
          :key="s.file"
          role="tab"
          :aria-selected="index === i"
          :tabindex="index === i ? 0 : -1"
          :class="{ active: index === i }"
          @click="pick(i)"
          @keydown="onTabKey"
        >
          {{ s.file }}
        </button>
      </div>
      <pre class="term-body"><code><span class="prompt">$</span> {{ typed }}<i v-if="shown === 0" class="caret" />
<template v-for="(line, i) in shows[index].out" :key="`${index}-${i}`"><span v-if="i < shown" class="out" :class="{ head: line.startsWith('#') || line.startsWith('{') || line.startsWith('}') }">{{ line }}
</span></template></code></pre>
    </div>
  </section>
</template>

<style scoped>
.agents {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr);
  gap: clamp(32px, 5vw, 72px);
  align-items: center;
  padding: clamp(72px, 10vw, 128px) 0 0;
}
.eyebrow {
  font-family: var(--vp-font-family-mono);
  font-size: 12.5px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--bc-mark);
  margin: 0 0 14px;
}
.title {
  font-size: clamp(2rem, 1.3rem + 2.8vw, 3.4rem);
  line-height: 1.06;
  letter-spacing: -0.04em;
  font-weight: 640;
  color: var(--bc-ink);
  margin: 0;
}
.title em {
  font-style: normal;
  color: var(--bc-mark);
}
.lede {
  margin: 18px 0 0;
  font-size: 1.1rem;
  line-height: 1.65;
  color: var(--vp-c-text-2);
}
.items {
  list-style: none;
  padding: 0;
  margin: 28px 0 0;
  border-top: 1px solid var(--bc-line);
}
.items li {
  border-bottom: 1px solid var(--bc-line);
}
.items a {
  display: grid;
  grid-template-columns: 170px 1fr;
  gap: 16px;
  padding: 12px 4px;
  color: inherit;
  transition: background-color 0.2s, padding 0.25s var(--bc-ease);
}
.items a:hover {
  background: var(--bc-surface);
  padding-left: 10px;
}
.items strong {
  font-family: var(--vp-font-family-mono);
  font-size: 13.5px;
  font-weight: 600;
  color: var(--vp-c-text-1);
}
.items span {
  font-size: 14px;
  line-height: 1.55;
  color: var(--vp-c-text-2);
}
.agents > * {
  min-width: 0;
}
.term {
  border: 1px solid var(--bc-line-strong);
  border-radius: 14px;
  background: var(--vp-c-bg-alt);
  box-shadow: var(--bc-shadow);
  overflow: hidden;
}
.term-tabs {
  display: flex;
  gap: 4px;
  padding: 8px;
  border-bottom: 1px solid var(--bc-line);
  overflow-x: auto;
}
.term-tabs button {
  padding: 4px 10px;
  border-radius: 7px;
  font-family: var(--vp-font-family-mono);
  font-size: 12px;
  color: var(--vp-c-text-3);
  white-space: nowrap;
  transition: all 0.2s;
}
.term-tabs button:hover {
  color: var(--vp-c-text-1);
}
.term-tabs button.active {
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg);
  box-shadow: inset 0 0 0 1px var(--bc-line);
}
.term-body {
  margin: 0;
  padding: 16px 18px;
  min-height: 228px;
  font-family: var(--vp-font-family-mono);
  font-size: 12.5px;
  line-height: 1.75;
  color: var(--vp-c-text-1);
  white-space: pre-wrap;
  word-break: break-all;
}
.prompt {
  color: var(--bc-mark);
}
.out {
  color: var(--vp-c-text-2);
  animation: out 0.25s var(--bc-ease);
}
.out.head {
  color: var(--vp-c-text-1);
  font-weight: 600;
}
@keyframes out {
  from {
    opacity: 0;
    transform: translateY(3px);
  }
}
.caret {
  display: inline-block;
  width: 7px;
  height: 1.1em;
  vertical-align: -0.2em;
  margin-left: 2px;
  background: var(--bc-mark);
  animation: bc-blink 1s steps(1) infinite;
}
@media (max-width: 960px) {
  .agents {
    grid-template-columns: 1fr;
  }
  .items a {
    grid-template-columns: 1fr;
    gap: 2px;
  }
}
</style>
