<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { onVisible, prefersReducedMotion } from '../../reveal'

/*
 * A scripted, looping demo of the Set of Marks loop on a wireframe shop page.
 * Element boxes are in percent of the viewport so marks line up at any size.
 */
interface El {
  id: string
  x: number
  y: number
  w: number
  h: number
}
type Scene = 'home' | 'results'

const header: El[] = [
  { id: 'logo', x: 4, y: 3.5, w: 15, h: 6.5 },
  { id: 'shop', x: 55, y: 3.5, w: 9, h: 6.5 },
  { id: 'deals', x: 65.5, y: 3.5, w: 10, h: 6.5 },
  { id: 'cart', x: 77, y: 3.5, w: 19, h: 6.5 },
]
const homeEls: El[] = [
  ...header,
  { id: 'search', x: 4, y: 41, w: 62, h: 10.5 },
  { id: 'go', x: 68, y: 41, w: 18, h: 10.5 },
  { id: 'chip1', x: 4, y: 57, w: 19, h: 7.5 },
  { id: 'chip2', x: 25, y: 57, w: 16, h: 7.5 },
  { id: 'chip3', x: 43, y: 57, w: 16, h: 7.5 },
]
const cardX = [4, 35.5, 67]
const resultEls: El[] = [
  ...header,
  { id: 'sort', x: 77, y: 15.5, w: 19, h: 7 },
  ...cardX.flatMap((x, i) => [
    { id: `title${i}`, x: x + 2, y: 66, w: 21, h: 6 },
    { id: `add${i}`, x: x + 2, y: 83, w: 25, h: 8.5 },
  ]),
]

const state = reactive({
  scene: 'home' as Scene,
  url: 'acme.shop',
  typed: '',
  marks: [] as El[],
  marksVisible: false,
  scanning: false,
  cursor: { x: 78, y: 88 },
  clicking: false,
  pulse: '' as string,
  found: [] as string[],
  cart: 0,
  toast: false,
  badge: '',
  lines: [] as { id: number; call: string; reply: string; done: boolean }[],
})

const elsFor = computed(() => (state.scene === 'home' ? homeEls : resultEls))
const root = ref<HTMLElement>()
let visible = false
let alive = true
let wake: (() => void) | null = null
let stopObserving: () => void = () => {}

const sleep = (ms: number) =>
  new Promise<void>((resolve) => setTimeout(resolve, ms)).then(async () => {
    if (!alive) throw new Error('stopped')
    while (!visible) {
      await new Promise<void>((r) => (wake = r))
      if (!alive) throw new Error('stopped')
    }
  })

const center = (id: string) => {
  const el = elsFor.value.find((e) => e.id === id)!
  return { x: el.x + el.w / 2, y: el.y + el.h / 2 + 1.5 }
}

async function scan() {
  state.marksVisible = false
  state.found = []
  await sleep(120)
  state.marks = elsFor.value
  state.scanning = true
  await sleep(650)
  state.scanning = false
  state.marksVisible = true
  await sleep(420)
}

let lineId = 0
async function say(call: string, reply: string) {
  const line = reactive({ id: ++lineId, call: '', reply, done: false })
  state.lines.push(line)
  if (state.lines.length > 4) state.lines.shift()
  for (const ch of call) {
    line.call += ch
    await sleep(22)
  }
  return line
}

async function moveTo(id: string, ms = 750) {
  state.cursor = center(id)
  await sleep(ms)
}

async function click(id: string) {
  state.pulse = id
  state.clicking = true
  await sleep(180)
  state.clicking = false
  await sleep(220)
  state.pulse = ''
}

async function loop() {
  for (;;) {
    // reset
    Object.assign(state, {
      scene: 'home',
      url: 'acme.shop',
      typed: '',
      marks: [],
      marksVisible: false,
      found: [],
      cart: 0,
      toast: false,
      badge: '',
      cursor: { x: 78, y: 88 },
    })
    state.lines = []
    await sleep(500)

    let l = await say('navigate_to("acme.shop")', '9 elements')
    await scan()
    l.done = true
    await sleep(700)

    l = await say('type_text(5, "mechanical")', 'typed into [5]')
    await moveTo('search')
    await click('search')
    for (const ch of 'mechanical') {
      state.typed += ch
      await sleep(45)
    }
    await scan()
    l.done = true
    await sleep(500)

    l = await say('click(6)', 'navigated · 11 elements')
    await moveTo('go')
    await click('go')
    state.marksVisible = false
    state.url = 'acme.shop/search?q=mechanical'
    await sleep(250)
    state.scene = 'results'
    await sleep(350)
    await scan()
    l.done = true
    state.badge = 'New screenshot, new numbers'
    await sleep(1500)
    state.badge = ''

    l = await say('find("Add to cart", role="button")', '3 matches: [7] [9] [11]')
    await sleep(200)
    state.found = ['add0', 'add1', 'add2']
    l.done = true
    await sleep(1200)

    l = await say('click(9)', 'clicked [9]')
    await moveTo('add1')
    await click('add1')
    state.cart = 1
    state.toast = true
    await scan()
    l.done = true
    await sleep(2600)
    state.toast = false
    await sleep(400)
  }
}

function staticFrame() {
  Object.assign(state, {
    scene: 'results',
    url: 'acme.shop/search?q=mechanical',
    typed: 'mechanical',
    marks: resultEls,
    marksVisible: true,
    cart: 1,
    cursor: center('add1'),
  })
  state.lines = [
    { id: 1, call: 'navigate_to("acme.shop")', reply: '9 elements', done: true },
    { id: 2, call: 'type_text(5, "mechanical")', reply: 'typed into [5]', done: true },
    { id: 3, call: 'click(6)', reply: 'navigated · 11 elements', done: true },
    { id: 4, call: 'click(9)', reply: 'clicked [9]', done: true },
  ]
}

onMounted(() => {
  if (prefersReducedMotion()) {
    staticFrame()
    return
  }
  stopObserving = onVisible(root.value!, (v) => {
    visible = v
    if (v && wake) {
      wake()
      wake = null
    }
  })
  loop().catch(() => {})
})

onBeforeUnmount(() => {
  alive = false
  stopObserving()
  wake?.()
})

const products = [
  { name: 'Halo 75', price: '$129' },
  { name: 'Tactile Pro', price: '$149' },
  { name: 'Lumen TKL', price: '$99' },
]
const markIndex = (id: string) => state.marks.findIndex((m) => m.id === id) + 1
</script>

<template>
  <div ref="root" class="demo" aria-label="Animated demo: an agent acting on numbered elements" role="img">
    <div class="window">
      <div class="chrome">
        <span class="dots"><i /><i /><i /></span>
        <div class="urlbar">
          <svg viewBox="0 0 24 24" width="11" height="11" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2" fill="currentColor"/><path d="M8 11V8a4 4 0 0 1 8 0v3" fill="none" stroke="currentColor" stroke-width="2"/></svg>
          <Transition name="url" mode="out-in"><span :key="state.url">{{ state.url }}</span></Transition>
        </div>
        <span class="chrome-tag">chromium</span>
      </div>

      <div class="viewport">
        <!-- shared header -->
        <div class="el el-logo" :style="{ left: '4%', top: '3.5%', width: '15%', height: '6.5%' }"><b>acme</b>.shop</div>
        <div class="el el-link" :style="{ left: '55%', top: '3.5%', width: '9%', height: '6.5%' }">Shop</div>
        <div class="el el-link" :style="{ left: '65.5%', top: '3.5%', width: '10%', height: '6.5%' }">Deals</div>
        <div class="el el-cart" :class="{ bump: state.cart }" :style="{ left: '77%', top: '3.5%', width: '19%', height: '6.5%' }">Cart · {{ state.cart }}</div>
        <div class="rule" />

        <Transition name="scene" mode="out-in">
          <div v-if="state.scene === 'home'" key="home" class="scene">
            <div class="el el-h1" :style="{ left: '4%', top: '18%', width: '70%' }">Find your next keyboard.</div>
            <div class="bar" :style="{ left: '4%', top: '30%', width: '46%' }" />
            <div class="el el-input" :class="{ pulse: state.pulse === 'search' }" :style="{ left: '4%', top: '41%', width: '62%', height: '10.5%' }">
              <span v-if="state.typed">{{ state.typed }}<i class="caret" /></span>
              <span v-else class="ph">Search keyboards…</span>
            </div>
            <div class="el el-btn" :class="{ pulse: state.pulse === 'go' }" :style="{ left: '68%', top: '41%', width: '18%', height: '10.5%' }">Search</div>
            <div class="el el-chip" :style="{ left: '4%', top: '57%', width: '19%', height: '7.5%' }">Mechanical</div>
            <div class="el el-chip" :style="{ left: '25%', top: '57%', width: '16%', height: '7.5%' }">Wireless</div>
            <div class="el el-chip" :style="{ left: '43%', top: '57%', width: '16%', height: '7.5%' }">Compact</div>
            <div class="banner" :style="{ left: '4%', top: '72%', width: '92%', height: '22%' }">
              <span /><span /><span />
            </div>
          </div>

          <div v-else key="results" class="scene">
            <div class="el el-meta" :style="{ left: '4%', top: '16.5%', width: '60%' }">3 results for “mechanical”</div>
            <div class="el el-select" :style="{ left: '77%', top: '15.5%', width: '19%', height: '7%' }">Sort ▾</div>
            <div v-for="(p, i) in products" :key="p.name" class="card" :style="{ left: `${cardX[i]}%`, top: '26%', width: '29%', height: '68%' }">
              <div class="card-img" :class="`img${i}`" />
            </div>
            <template v-for="(p, i) in products" :key="`t${i}`">
              <div class="el el-title" :style="{ left: `${cardX[i] + 2}%`, top: '66%', width: '21%', height: '6%' }">{{ p.name }}</div>
              <div class="el el-price" :style="{ left: `${cardX[i] + 2}%`, top: '74%' }">{{ p.price }}</div>
              <div class="el el-add" :class="{ pulse: state.pulse === `add${i}`, done: state.cart && i === 1 }" :style="{ left: `${cardX[i] + 2}%`, top: '83%', width: '25%', height: '8.5%' }">
                {{ state.cart && i === 1 ? 'Added ✓' : 'Add to cart' }}
              </div>
            </template>
          </div>
        </Transition>

        <!-- Set of Marks overlay -->
        <div class="marks" :class="{ on: state.marksVisible }">
          <div
            v-for="(m, i) in state.marks"
            :key="`${state.scene}-${m.id}`"
            class="mark"
            :class="{ found: state.found.includes(m.id) }"
            :style="{ left: `${m.x}%`, top: `${m.y}%`, width: `${m.w}%`, height: `${m.h}%`, '--i': i }"
          >
            <span>{{ markIndex(m.id) }}</span>
          </div>
        </div>
        <div v-if="state.scanning" class="scan" />

        <Transition name="toast"><div v-if="state.toast" class="toast">Added to cart</div></Transition>
        <Transition name="toast"><div v-if="state.badge" class="badge">{{ state.badge }}</div></Transition>

        <svg class="cursor" :class="{ clicking: state.clicking }" :style="{ left: `${state.cursor.x}%`, top: `${state.cursor.y}%` }" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
          <path d="M5 3l14 7.5-6.2 1.6L10 18.5z" fill="var(--vp-c-text-1)" stroke="var(--vp-c-bg)" stroke-width="1.4" stroke-linejoin="round" />
        </svg>
      </div>
    </div>

    <div class="term">
      <div class="term-head"><span class="term-dot" /> agent · mcp</div>
      <TransitionGroup name="line" tag="div" class="term-body">
        <div v-for="(l, i) in state.lines" :key="l.id" class="term-line">
          <div class="call"><span class="arrow">→</span> {{ l.call }}<i v-if="!l.done && i === state.lines.length - 1" class="caret" /></div>
          <Transition name="reply"><div v-if="l.done" class="reply">← screenshot · {{ l.reply }}</div></Transition>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<style scoped>
.demo {
  position: relative;
  width: 100%;
  max-width: 640px;
  margin-left: auto;
  padding-bottom: 112px;
}
.window {
  border: 1px solid var(--bc-line-strong);
  border-radius: 14px;
  background: var(--vp-c-bg);
  box-shadow: var(--bc-shadow), 0 40px 80px -40px color-mix(in srgb, var(--bc-mark) 25%, transparent);
  overflow: hidden;
}
.chrome {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 12px;
  border-bottom: 1px solid var(--bc-line);
  background: var(--vp-c-bg-alt);
}
.dots {
  display: flex;
  gap: 6px;
}
.dots i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--bc-line-strong);
}
.dots i:nth-child(1) {
  background: var(--bc-red);
}
.dots i:nth-child(2) {
  background: var(--bc-yellow);
}
.dots i:nth-child(3) {
  background: var(--bc-green);
}
.urlbar {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 7px;
  height: 26px;
  padding: 0 10px;
  border-radius: 7px;
  background: var(--vp-c-bg);
  border: 1px solid var(--bc-line);
  font-family: var(--vp-font-family-mono);
  font-size: 11.5px;
  color: var(--vp-c-text-2);
  overflow: hidden;
  white-space: nowrap;
}
.urlbar svg {
  color: var(--bc-green);
  flex: none;
}
.chrome-tag {
  font-family: var(--vp-font-family-mono);
  font-size: 10.5px;
  color: var(--vp-c-text-3);
}
.viewport {
  position: relative;
  aspect-ratio: 16 / 10.5;
  container-type: inline-size;
  background:
    linear-gradient(var(--bc-grid) 1px, transparent 1px) 0 0 / 100% 8.33%,
    var(--vp-c-bg);
  overflow: hidden;
}
.scene {
  position: absolute;
  inset: 0;
}
.el,
.bar,
.banner,
.card {
  position: absolute;
}
.el {
  display: flex;
  align-items: center;
  font-size: 2.1cqw;
  color: var(--vp-c-text-2);
  border-radius: 1cqw;
  transition:
    background-color 0.2s,
    transform 0.2s;
}
.el-logo {
  font-size: 2.5cqw;
  color: var(--vp-c-text-1);
  gap: 0;
}
.el-logo b {
  color: var(--bc-mark);
  font-weight: 750;
}
.el-link,
.el-cart {
  justify-content: center;
  font-weight: 550;
}
.el-cart {
  border: 1px solid var(--bc-line);
  color: var(--vp-c-text-1);
}
.el-cart.bump {
  animation: bump 0.5s var(--bc-ease);
}
@keyframes bump {
  40% {
    transform: scale(1.12);
  }
}
.rule {
  position: absolute;
  left: 0;
  right: 0;
  top: 13%;
  border-top: 1px dashed var(--bc-line);
}
.el-h1 {
  font-size: 4.6cqw;
  font-weight: 680;
  letter-spacing: -0.03em;
  color: var(--vp-c-text-1);
}
.bar {
  height: 2.4%;
  border-radius: 99px;
  background: var(--bc-line);
}
.el-input {
  padding: 0 2cqw;
  border: 1.5px solid var(--bc-line-strong);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-family: var(--vp-font-family-mono);
}
.el-input .ph {
  color: var(--vp-c-text-3);
  font-family: var(--vp-font-family-base);
}
.el-btn {
  justify-content: center;
  font-weight: 650;
  background: var(--vp-c-text-1);
  color: var(--vp-c-bg);
}
.el-chip {
  justify-content: center;
  border: 1px solid var(--bc-line);
  border-radius: 99px;
}
.banner {
  display: flex;
  gap: 2%;
  padding: 2.5%;
  border-radius: 1.2cqw;
  background: linear-gradient(120deg, color-mix(in srgb, var(--bc-lavender) 22%, transparent), color-mix(in srgb, var(--bc-peach) 18%, transparent));
}
.banner span {
  flex: 1;
  border-radius: 1cqw;
  background: color-mix(in srgb, var(--vp-c-bg) 55%, transparent);
}
.el-meta {
  font-size: 2.3cqw;
  color: var(--vp-c-text-1);
  font-weight: 550;
}
.el-select {
  justify-content: center;
  border: 1px solid var(--bc-line);
}
.card {
  border: 1px solid var(--bc-line);
  border-radius: 1.4cqw;
  overflow: hidden;
}
.card-img {
  height: 50%;
  margin: 6%;
  border-radius: 1cqw;
}
.img0 {
  background: color-mix(in srgb, var(--bc-mauve) 22%, transparent);
}
.img1 {
  background: color-mix(in srgb, var(--bc-teal) 22%, transparent);
}
.img2 {
  background: color-mix(in srgb, var(--bc-peach) 22%, transparent);
}
.el-title {
  font-weight: 650;
  color: var(--vp-c-text-1);
}
.el-price {
  font-family: var(--vp-font-family-mono);
  font-size: 1.9cqw;
}
.el-add {
  justify-content: center;
  font-weight: 600;
  border: 1px solid var(--bc-line-strong);
}
.el-add.done {
  background: color-mix(in srgb, var(--bc-green) 20%, transparent);
  border-color: var(--bc-green);
  color: var(--vp-c-text-1);
}
.pulse {
  transform: scale(0.96);
  background-color: var(--bc-mark-soft);
}
.caret {
  display: inline-block;
  width: 1px;
  height: 1.1em;
  margin-left: 1px;
  vertical-align: -0.15em;
  background: currentColor;
  animation: bc-blink 1s steps(1) infinite;
}

/* Marks */
.marks {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.mark {
  position: absolute;
  border: 1.5px solid var(--bc-mark);
  border-radius: 0.8cqw;
  background: color-mix(in srgb, var(--bc-mark) 7%, transparent);
  opacity: 0;
  transform: scale(1.08);
  transition:
    opacity 0.25s var(--bc-ease) calc(var(--i) * 40ms),
    transform 0.35s var(--bc-ease) calc(var(--i) * 40ms),
    background-color 0.25s,
    box-shadow 0.25s;
}
.marks.on .mark {
  opacity: 1;
  transform: none;
}
.marks:not(.on) .mark {
  transition-delay: 0s;
}
.mark span {
  position: absolute;
  top: -1.7cqw;
  left: -1.3cqw;
  min-width: 3cqw;
  height: 3cqw;
  padding: 0 0.5cqw;
  display: grid;
  place-items: center;
  font-family: var(--vp-font-family-mono);
  font-size: 1.9cqw;
  font-weight: 750;
  color: var(--vp-c-bg);
  background: var(--bc-mark);
  border-radius: 0.6cqw;
}
.mark.found {
  background: color-mix(in srgb, var(--bc-mark) 20%, transparent);
  box-shadow: 0 0 0 0.6cqw color-mix(in srgb, var(--bc-mark) 18%, transparent);
}
.scan {
  position: absolute;
  left: 0;
  right: 0;
  height: 18%;
  top: -18%;
  background: linear-gradient(to bottom, transparent, color-mix(in srgb, var(--bc-mark) 14%, transparent) 85%, var(--bc-mark));
  opacity: 0.8;
  animation: scan 0.65s cubic-bezier(0.5, 0, 0.5, 1) forwards;
  pointer-events: none;
}
@keyframes scan {
  to {
    top: 100%;
  }
}

/* Cursor */
.cursor {
  position: absolute;
  z-index: 5;
  width: 3.4cqw;
  height: 3.4cqw;
  transition:
    left 0.75s cubic-bezier(0.6, 0, 0.25, 1),
    top 0.75s cubic-bezier(0.6, 0, 0.25, 1),
    transform 0.15s;
  filter: drop-shadow(0 2px 3px rgb(0 0 0 / 0.25));
}
.cursor.clicking {
  transform: scale(0.82);
}

.toast,
.badge {
  position: absolute;
  z-index: 6;
  left: 50%;
  transform: translateX(-50%);
  padding: 1cqw 2.2cqw;
  border-radius: 99px;
  font-size: 1.9cqw;
  font-weight: 600;
  white-space: nowrap;
}
.toast {
  bottom: 4%;
  background: var(--vp-c-text-1);
  color: var(--vp-c-bg);
}
.badge {
  top: 24%;
  background: var(--bc-mark);
  color: var(--vp-c-bg);
  box-shadow: 0 6px 20px -6px var(--bc-mark);
}

/* Transcript */
.term {
  position: absolute;
  left: -28px;
  bottom: 0;
  width: min(320px, 64%);
  border: 1px solid var(--bc-line-strong);
  border-radius: 12px;
  background: color-mix(in srgb, var(--vp-c-bg-alt) 92%, transparent);
  backdrop-filter: blur(10px);
  box-shadow: var(--bc-shadow);
  font-family: var(--vp-font-family-mono);
  font-size: 11.5px;
  overflow: hidden;
}
.term-head {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 7px 12px;
  border-bottom: 1px solid var(--bc-line);
  color: var(--vp-c-text-3);
  font-size: 10.5px;
  letter-spacing: 0.04em;
}
.term-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--bc-green);
  animation: bc-pulse 2s infinite;
}
.term-body {
  position: relative;
  padding: 8px 12px 10px;
  min-height: 124px;
}
.term-line {
  padding: 2px 0;
}
.call {
  color: var(--vp-c-text-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.arrow {
  color: var(--bc-mark);
}
.reply {
  color: var(--vp-c-text-3);
  padding-left: 15px;
}

/* Transitions */
.scene-enter-active,
.scene-leave-active {
  transition:
    opacity 0.3s,
    transform 0.3s var(--bc-ease);
}
.scene-enter-from {
  opacity: 0;
  transform: translateY(2%);
}
.scene-leave-to {
  opacity: 0;
}
.url-enter-active,
.url-leave-active {
  transition: opacity 0.2s;
}
.url-enter-from,
.url-leave-to {
  opacity: 0;
}
.toast-enter-active,
.toast-leave-active {
  transition:
    opacity 0.3s,
    transform 0.35s var(--bc-ease);
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, 30%);
}
.line-enter-active {
  transition:
    opacity 0.25s,
    transform 0.25s var(--bc-ease);
}
.line-leave-active {
  position: absolute;
  transition: opacity 0.2s;
}
.line-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.line-leave-to {
  opacity: 0;
}
.line-move {
  transition: transform 0.3s var(--bc-ease);
}
.reply-enter-active {
  transition: opacity 0.3s;
}
.reply-enter-from {
  opacity: 0;
}

@media (max-width: 960px) {
  .demo {
    margin: 0 auto;
  }
  .term {
    left: 12px;
  }
}
</style>
