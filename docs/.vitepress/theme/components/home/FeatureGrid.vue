<script setup lang="ts">
import { withBase } from 'vitepress'
</script>

<template>
  <div class="grid">
    <!-- find -->
    <a class="tile span2" :href="withBase('/reference/navigation#find')" v-reveal="0">
      <div class="viz viz-find" aria-hidden="true">
        <div class="find-page">
          <div class="find-scroll">
            <span v-for="n in 14" :key="n" class="find-line" :class="{ hit: n === 10 }" :style="{ width: `${40 + ((n * 37) % 50)}%` }">
              <template v-if="n === 10">Delete account</template>
            </span>
          </div>
          <span class="find-mark"><b>14</b></span>
        </div>
        <div class="find-query">
          <svg viewBox="0 0 24 24" width="14" height="14"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="M20 20l-3.5-3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          find("Delete account")
        </div>
      </div>
      <div class="copy">
        <h3>Find anything on the page</h3>
        <p>Search text and labels across the whole page, off-screen content, iframes and shadow DOM included. It scrolls there and hands back the element's number.</p>
      </div>
    </a>

    <!-- act -->
    <a class="tile" :href="withBase('/reference/interaction#act')" v-reveal="80">
      <div class="viz viz-act" aria-hidden="true">
        <span class="step" style="--i: 0">type <b>3</b> "ada@…"</span>
        <span class="step" style="--i: 1">type <b>4</b> ••••••</span>
        <span class="step" style="--i: 2">click <b>5</b></span>
        <span class="shot">1 screenshot</span>
      </div>
      <div class="copy">
        <h3>Batch steps with act</h3>
        <p>Fill a whole form in one call and get one screenshot back.</p>
      </div>
    </a>

    <!-- chrome -->
    <a class="tile" :href="withBase('/recipes/your-chrome')" v-reveal="0">
      <div class="viz viz-cdp" aria-hidden="true">
        <span class="node">BrowserControl</span>
        <svg class="wire" viewBox="0 0 100 10" preserveAspectRatio="none"><line x1="0" y1="5" x2="100" y2="5" /></svg>
        <span class="node node-chrome"><i />Your Chrome</span>
        <span class="port">localhost:9222</span>
      </div>
      <div class="copy">
        <h3>Use your own Chrome</h3>
        <p>Attach over CDP and work in the sites you're already signed in to.</p>
      </div>
    </a>

    <!-- extract -->
    <a class="tile" :href="withBase('/recipes/extract-data')" v-reveal="80">
      <div class="viz viz-extract" aria-hidden="true">
        <div class="tbl">
          <span v-for="r in 4" :key="r" class="tr" :style="{ '--r': r }"><i /><i /><i /></span>
        </div>
        <span class="json">[{"name": "Halo", "price": 129}, …]</span>
      </div>
      <div class="copy">
        <h3>Extract data as JSON</h3>
        <p>Tables, links, or any fields you describe with selectors.</p>
      </div>
    </a>

    <!-- network -->
    <a class="tile" :href="withBase('/recipes/edge-states')" v-reveal="160">
      <div class="viz viz-net" aria-hidden="true">
        <span class="lane"><span class="pkt" style="--d: 0s" /><span class="pkt" style="--d: 1.1s" /><span class="pkt bad" style="--d: 2.2s" /></span>
        <span class="net-label">GET /api/cart</span>
        <span class="net-status">500</span>
      </div>
      <div class="copy">
        <h3>Mock the network</h3>
        <p>Stub responses, force errors, block trackers, throttle to 3G or offline.</p>
      </div>
    </a>

    <!-- emulate -->
    <a class="tile" :href="withBase('/recipes/responsive')" v-reveal="0">
      <div class="viz viz-emu" aria-hidden="true">
        <div class="device"><span /><span /><span /></div>
      </div>
      <div class="copy">
        <h3>Emulate devices</h3>
        <p>Phones, tablets, dark mode, timezones, and locations.</p>
      </div>
    </a>

    <!-- devtools -->
    <a class="tile" :href="withBase('/recipes/debug')" v-reveal="80">
      <div class="viz viz-console" aria-hidden="true">
        <span class="log err" style="--i: 0">✕ TypeError: items is undefined</span>
        <span class="log warn" style="--i: 1">▲ 404 GET /api/users</span>
        <span class="log" style="--i: 2">› render took 412 ms</span>
        <span class="log" style="--i: 3">› POST /login → 200</span>
      </div>
      <div class="copy">
        <h3>Debug like DevTools</h3>
        <p>Console, page errors, request headers and bodies, HAR export.</p>
      </div>
    </a>

    <!-- export -->
    <a class="tile" :href="withBase('/recipes/record-tests')" v-reveal="160">
      <div class="viz viz-code" aria-hidden="true">
        <code><span class="cl" style="--i: 0"><span class="k">def</span> test_checkout(page):</span><span class="cl" style="--i: 1">  page.goto(<span class="s">"shop.test"</span>)</span><span class="cl" style="--i: 2">  page.get_by_label(<span class="s">"Email"</span>)…</span><span class="cl" style="--i: 3">  page.get_by_role(<span class="s">"button"</span>)…</span></code>
      </div>
      <div class="copy">
        <h3>Export a Playwright test</h3>
        <p>Turn what the agent did into a test you can keep and run in CI.</p>
      </div>
    </a>
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 48px;
}
.tile {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--bc-line);
  border-radius: 16px;
  background: var(--vp-c-bg);
  overflow: hidden;
  color: inherit;
  transition:
    border-color 0.25s,
    transform 0.35s var(--bc-ease),
    box-shadow 0.3s;
}
.tile:hover {
  border-color: var(--bc-line-strong);
  transform: translateY(-3px);
  box-shadow: var(--bc-shadow);
}
.span2 {
  grid-column: span 2;
}
.viz {
  position: relative;
  height: 180px;
  border-bottom: 1px dashed var(--bc-line-strong);
  background:
    radial-gradient(circle at 1px 1px, var(--bc-line) 1px, transparent 0) 0 0 / 14px 14px,
    var(--bc-surface);
  overflow: hidden;
  font-family: var(--vp-font-family-mono);
  font-size: 12px;
  color: var(--vp-c-text-2);
}
/* Pause every animation until the tile has been revealed */
.viz * {
  animation-play-state: paused !important;
}
.tile.is-visible .viz * {
  animation-play-state: running !important;
}
.copy {
  padding: 16px 18px 18px;
}
.copy h3 {
  margin: 0 0 4px;
  font-size: 1.05rem;
  font-weight: 640;
  letter-spacing: -0.02em;
  color: var(--vp-c-text-1);
}
.copy p {
  margin: 0;
  font-size: 14px;
  line-height: 1.55;
  color: var(--vp-c-text-2);
}

/* find */
.find-page {
  position: absolute;
  left: 8%;
  top: 14px;
  bottom: -1px;
  width: 52%;
  border: 1px solid var(--bc-line-strong);
  border-bottom: 0;
  border-radius: 10px 10px 0 0;
  background: var(--vp-c-bg);
  overflow: hidden;
}
.find-scroll {
  display: flex;
  flex-direction: column;
  gap: 9px;
  padding: 14px;
  animation: find-scroll 5s var(--bc-ease) infinite;
}
@keyframes find-scroll {
  0%,
  15% {
    transform: translateY(0);
  }
  45%,
  90% {
    transform: translateY(-112px);
  }
  100% {
    transform: translateY(0);
  }
}
.find-line {
  height: 8px;
  border-radius: 99px;
  background: var(--bc-line);
  flex: none;
}
.find-line.hit {
  height: 22px;
  width: auto !important;
  align-self: flex-start;
  padding: 0 10px;
  display: flex;
  align-items: center;
  border-radius: 6px;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--vp-c-bg);
  background: var(--vp-c-text-1);
}
.find-mark {
  position: absolute;
  left: 10px;
  top: 92px;
  width: 124px;
  height: 30px;
  border: 1.5px solid var(--bc-mark);
  border-radius: 7px;
  opacity: 0;
  animation: find-mark 5s var(--bc-ease) infinite;
}
.find-mark b {
  position: absolute;
  top: -9px;
  left: -8px;
  padding: 0 4px;
  font-size: 10.5px;
  line-height: 16px;
  color: var(--vp-c-bg);
  background: var(--bc-mark);
  border-radius: 4px;
}
@keyframes find-mark {
  0%,
  48% {
    opacity: 0;
    transform: scale(1.15);
  }
  56%,
  88% {
    opacity: 1;
    transform: none;
  }
  100% {
    opacity: 0;
  }
}
.find-query {
  position: absolute;
  right: 6%;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid var(--bc-line-strong);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 13px;
  box-shadow: var(--bc-shadow);
}
.find-query svg {
  color: var(--bc-mark);
}

/* act */
.viz-act {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 7px;
  padding: 0 22px;
}
.step {
  align-self: flex-start;
  padding: 5px 10px;
  border-radius: 7px;
  border: 1px solid var(--bc-line-strong);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  opacity: 0;
  animation: step 4s var(--bc-ease) infinite;
  animation-delay: calc(var(--i) * 0.35s);
}
.step b {
  color: var(--bc-mark);
}
@keyframes step {
  0% {
    opacity: 0;
    transform: translateX(-10px);
  }
  12%,
  80% {
    opacity: 1;
    transform: none;
  }
  92%,
  100% {
    opacity: 0;
    transform: translateX(6px);
  }
}
.shot {
  position: absolute;
  right: 18px;
  bottom: 18px;
  padding: 4px 10px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 600;
  color: var(--vp-c-bg);
  background: var(--bc-green);
  opacity: 0;
  animation: shot 4s var(--bc-ease) infinite;
}
@keyframes shot {
  0%,
  38% {
    opacity: 0;
    transform: scale(0.8);
  }
  46%,
  80% {
    opacity: 1;
    transform: none;
  }
  92%,
  100% {
    opacity: 0;
  }
}

/* cdp */
.viz-cdp {
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 0;
}
.node {
  flex: none;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid var(--bc-line-strong);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 11.5px;
  z-index: 1;
}
.node-chrome {
  display: flex;
  align-items: center;
  gap: 6px;
}
.node-chrome i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: conic-gradient(var(--bc-red) 0 33%, var(--bc-yellow) 0 66%, var(--bc-green) 0);
}
.wire {
  flex: 1;
  height: 10px;
}
.wire line {
  stroke: var(--bc-mark);
  stroke-width: 2;
  vector-effect: non-scaling-stroke;
  stroke-dasharray: 4 4;
  animation: dash 0.8s linear infinite;
}
@keyframes dash {
  to {
    stroke-dashoffset: -8;
  }
}
.port {
  position: absolute;
  bottom: 22px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: var(--vp-c-text-3);
}

/* extract */
.viz-extract {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 14px;
  padding: 0 22px;
}
.tbl {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.tr {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 6px;
  opacity: 0;
  animation: row 4.4s var(--bc-ease) infinite;
  animation-delay: calc(var(--r) * 0.18s);
}
.tr i {
  height: 12px;
  border-radius: 3px;
  background: var(--bc-line);
}
.tr:first-child i {
  background: var(--bc-line-strong);
}
@keyframes row {
  0% {
    opacity: 0;
  }
  10%,
  85% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}
.json {
  font-size: 11.5px;
  color: var(--bc-teal);
  white-space: nowrap;
  overflow: hidden;
  border-right: 2px solid var(--bc-teal);
  width: 0;
  animation: type-json 4.4s steps(34) infinite;
}
@keyframes type-json {
  0%,
  25% {
    width: 0;
  }
  65%,
  90% {
    width: 34ch;
  }
  100% {
    width: 0;
  }
}

/* network */
.viz-net {
  display: flex;
  align-items: center;
  padding: 0 18px;
}
.lane {
  position: relative;
  flex: 1;
  height: 2px;
  background: var(--bc-line-strong);
}
.pkt {
  position: absolute;
  top: -5px;
  left: 0;
  width: 12px;
  height: 12px;
  border-radius: 3px;
  background: var(--bc-green);
  animation: pkt 3.3s linear infinite;
  animation-delay: var(--d);
  opacity: 0;
}
.pkt.bad {
  animation-name: pkt-bad;
}
@keyframes pkt {
  0% {
    left: 0;
    opacity: 1;
  }
  33% {
    left: calc(100% - 12px);
    opacity: 1;
  }
  34%,
  100% {
    opacity: 0;
  }
}
@keyframes pkt-bad {
  0% {
    left: 0;
    opacity: 1;
    background: var(--bc-green);
  }
  16% {
    left: 50%;
    background: var(--bc-green);
    transform: none;
  }
  20% {
    left: 50%;
    background: var(--bc-red);
    transform: scale(1.4);
  }
  30% {
    left: 50%;
    opacity: 1;
    background: var(--bc-red);
  }
  34%,
  100% {
    left: 50%;
    opacity: 0;
  }
}
.net-label {
  position: absolute;
  left: 18px;
  top: 34%;
  font-size: 11.5px;
}
.net-status {
  position: absolute;
  left: calc(50% + 6px);
  top: 58%;
  padding: 1px 7px;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 700;
  color: var(--vp-c-bg);
  background: var(--bc-red);
  animation: status 3.3s linear infinite;
  animation-delay: 2.2s;
  opacity: 0;
}
@keyframes status {
  18%,
  32% {
    opacity: 1;
  }
  0%,
  16%,
  36%,
  100% {
    opacity: 0;
  }
}

/* emulate */
.viz-emu {
  display: grid;
  place-items: center;
}
.device {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px;
  border: 2px solid var(--vp-c-text-2);
  border-radius: 10px;
  background: var(--vp-c-bg);
  animation: morph 6s var(--bc-ease) infinite;
}
.device span {
  height: 9px;
  border-radius: 3px;
  background: var(--bc-line-strong);
}
.device span:first-child {
  height: 30px;
  background: color-mix(in srgb, var(--bc-mauve) 25%, transparent);
}
@keyframes morph {
  0%,
  22% {
    width: 210px;
    height: 120px;
    border-radius: 8px;
  }
  33%,
  55% {
    width: 120px;
    height: 140px;
    border-radius: 12px;
  }
  66%,
  88% {
    width: 70px;
    height: 132px;
    border-radius: 16px;
    background: var(--vp-c-text-1);
  }
  100% {
    width: 210px;
    height: 120px;
  }
}

/* console */
.viz-console {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
  padding: 0 18px;
  font-size: 11.5px;
}
.log {
  padding: 3px 8px;
  border-radius: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 0;
  animation: log 5s var(--bc-ease) infinite;
  animation-delay: calc(var(--i) * 0.4s);
}
.log.err {
  color: var(--bc-red);
  background: color-mix(in srgb, var(--bc-red) 10%, transparent);
}
.log.warn {
  color: var(--bc-yellow);
  background: color-mix(in srgb, var(--bc-yellow) 10%, transparent);
}
@keyframes log {
  0% {
    opacity: 0;
    transform: translateY(6px);
  }
  8%,
  82% {
    opacity: 1;
    transform: none;
  }
  95%,
  100% {
    opacity: 0;
  }
}

/* code */
.viz-code {
  display: flex;
  align-items: center;
  padding: 0 18px;
}
.viz-code code {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 11.5px;
  color: var(--vp-c-text-1);
}
.cl {
  white-space: pre;
  overflow: hidden;
  width: 0;
  animation: cl 5.5s steps(30) infinite;
  animation-delay: calc(var(--i) * 0.55s);
}
@keyframes cl {
  0% {
    width: 0;
  }
  18%,
  85% {
    width: 30ch;
  }
  100% {
    width: 0;
  }
}
.k {
  color: var(--bc-mauve);
}
.s {
  color: var(--bc-green);
}

@media (max-width: 960px) {
  .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 640px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .span2 {
    grid-column: auto;
  }
  .find-query {
    display: none;
  }
  .find-page {
    width: 84%;
  }
}
</style>
