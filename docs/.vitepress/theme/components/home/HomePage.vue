<script setup lang="ts">
import { withBase } from 'vitepress'
import MarksDemo from './MarksDemo.vue'
import FeatureGrid from './FeatureGrid.vue'
import AgentSection from './AgentSection.vue'
import InstallBox from '../InstallBox.vue'
import { data } from '../../tools.data'

const clients = [
  'Claude Code',
  'Claude Desktop',
  'Cursor',
  'VS Code Copilot',
  'Gemini CLI',
  'Cline',
  'Zed',
  'Continue',
  'OpenCode',
  'Python MCP SDK',
  'Any MCP client',
]
const ticks = Array.from({ length: 61 }, (_, i) => i)
</script>

<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-copy">
        <a class="pill" :href="withBase('/project/changelog')" v-reveal>
          <span class="pill-tag">New</span> Attach to your own Chrome, export tests, and more
          <span aria-hidden="true">→</span>
        </a>
        <h1 class="hero-title" v-reveal="60">
          Your agent
          <span class="hero-mark">
            <span class="hero-mark-n" aria-hidden="true">7</span>sees</span>
          the page.
        </h1>
        <p class="hero-lede" v-reveal="120">
          BrowserControl is a local MCP server that gives AI agents a real Chromium browser.
          Every action returns a screenshot with a number on everything clickable, so your
          agent says <code>click(7)</code> instead of guessing selectors.
        </p>
        <div class="hero-install" v-reveal="180">
          <InstallBox />
        </div>
        <div class="hero-actions" v-reveal="240">
          <a class="btn btn-primary" :href="withBase('/guide/quickstart')">Get started <span aria-hidden="true">→</span></a>
          <a class="btn" :href="withBase('/reference/')">Browse {{ data.count }} tools</a>
        </div>
      </div>
      <div class="hero-demo" v-reveal="150">
        <MarksDemo />
      </div>
    </section>

    <!-- Ruler + status -->
    <div class="ruler" aria-hidden="true">
      <span v-for="t in ticks" :key="t" :class="{ major: t % 10 === 0, mid: t % 5 === 0 }" />
    </div>
    <div class="status">
      <span class="status-item"><i class="status-dot" /> ready</span>
      <span class="status-item">stdio · http</span>
      <span class="status-item">{{ data.count }} tools</span>
      <span class="status-item hide-sm">Python 3.11.5+</span>
      <span class="status-item hide-sm">runs locally</span>
      <span class="status-item">MIT</span>
    </div>

    <!-- The loop -->
    <section class="section">
      <p class="eyebrow" v-reveal>How it works</p>
      <h2 class="section-title" v-reveal="60">One loop. <em>Act, settle, look.</em></h2>
      <p class="section-lede" v-reveal="120">
        Every tool runs the same cycle, so the agent always acts on a picture of the page as it is
        right now.
      </p>
      <ol class="loop">
        <li v-reveal="0">
          <div class="loop-viz viz-act"><code>click(<b>7</b>)</code><span class="ripple" /></div>
          <h3><span class="loop-n">1</span> Act</h3>
          <p>The agent names an element by its number. BrowserControl finds that exact element again, in its frame, through shadow DOM, and refuses if it moved.</p>
        </li>
        <li v-reveal="120">
          <div class="loop-viz viz-settle">
            <span class="settle-row"><i style="--d: 0s" /> load</span>
            <span class="settle-row"><i style="--d: .5s" /> network quiet</span>
            <span class="settle-row"><i style="--d: 1s" /> DOM quiet</span>
          </div>
          <h3><span class="loop-n">2</span> Settle</h3>
          <p>No fixed sleeps. It waits for the page load, in-flight requests, and DOM changes to finish, within a time budget.</p>
        </li>
        <li v-reveal="240">
          <div class="loop-viz viz-look">
            <span class="look-box" style="--i: 0; left: 10%; top: 18%; width: 34%; height: 22%"><b>1</b></span>
            <span class="look-box" style="--i: 1; left: 52%; top: 18%; width: 38%; height: 22%"><b>2</b></span>
            <span class="look-box" style="--i: 2; left: 10%; top: 54%; width: 80%; height: 26%"><b>3</b></span>
          </div>
          <h3><span class="loop-n">3</span> Look</h3>
          <p>A fresh screenshot comes back with numbered boxes and a matching text list. Old numbers are gone; new ones take their place.</p>
        </li>
      </ol>
    </section>

    <!-- Statement -->
    <section class="statement">
      <p class="statement-text" v-reveal>
        Selectors break when a site changes.
        <span class="statement-mark"><b>7</b>Numbers</span>
        come from what is on screen right now.
      </p>
      <div class="facts">
        <div v-reveal="0"><strong>Stale IDs are refused.</strong> If an element moved or vanished since the screenshot, the tool says so and hands back a fresh one instead of clicking the wrong thing.</div>
        <div v-reveal="100"><strong>Every frame counts.</strong> Controls inside iframes, cross-origin ones included, and open shadow roots get numbers too.</div>
        <div v-reveal="200"><strong>Covered means unnumbered.</strong> A control hidden under a cookie banner or modal gets no number, which tells the agent to deal with the overlay first.</div>
      </div>
    </section>

    <!-- Features -->
    <section class="section">
      <p class="eyebrow" v-reveal>What it can do</p>
      <h2 class="section-title" v-reveal="60">A whole browser, <em>not just clicks.</em></h2>
      <p class="section-lede" v-reveal="120">
        Read, extract, debug, mock, emulate, and record, all from the same MCP server and the same
        numbered screenshots.
      </p>
      <FeatureGrid />
    </section>

    <!-- Agents -->
    <AgentSection />

    <!-- Clients -->
    <section class="clients" aria-label="Works with">
      <p class="eyebrow center" v-reveal>Works with</p>
      <div class="marquee">
        <div class="marquee-track">
          <span v-for="(c, i) in [...clients, ...clients]" :key="i" :aria-hidden="i >= clients.length">{{ c }}</span>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta">
      <h2 class="cta-title" v-reveal>Your agent is <em>one command</em> away from a browser.</h2>
      <div class="cta-install" v-reveal="80"><InstallBox /></div>
      <div class="hero-actions center" v-reveal="160">
        <a class="btn btn-primary" :href="withBase('/guide/quickstart')">Read the quickstart <span aria-hidden="true">→</span></a>
        <a class="btn" href="https://github.com/adityasasidhar/browsercontrol">Star on GitHub</a>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home {
  --pad: clamp(20px, 4vw, 48px);
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 var(--pad);
  overflow-x: clip;
}

/* Hero */
.hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr);
  gap: clamp(32px, 5vw, 72px);
  align-items: center;
  padding: clamp(40px, 7vw, 96px) 0 48px;
}
.hero > *,
.hero-install,
.cta-install {
  min-width: 0;
}
.pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px 4px 4px;
  border: 1px solid var(--bc-line);
  border-radius: 99px;
  font-size: 13px;
  color: var(--vp-c-text-2);
  background: var(--vp-c-bg);
  transition: border-color 0.2s, color 0.2s;
}
.pill:hover {
  border-color: var(--bc-mark);
  color: var(--vp-c-text-1);
}
.pill-tag {
  padding: 1px 8px;
  border-radius: 99px;
  font-size: 11.5px;
  font-weight: 650;
  color: var(--vp-c-bg);
  background: var(--bc-mark);
}
.hero-title {
  margin: 22px 0 18px;
  font-size: clamp(2.8rem, 1.6rem + 4.6vw, 5rem);
  line-height: 1.02;
  letter-spacing: -0.045em;
  font-weight: 650;
  color: var(--bc-ink);
}
.hero-mark {
  position: relative;
  display: inline-block;
  padding: 0 0.1em 0.02em;
  margin: 0 0.08em 0 0.1em;
  color: var(--bc-mark);
}
.hero-mark::before {
  content: '';
  position: absolute;
  inset: 0.08em -0.02em 0;
  border: 0.045em solid var(--bc-mark);
  border-radius: 0.08em;
  background: var(--bc-mark-soft);
  clip-path: inset(0 100% 0 0);
  animation: wipe 0.8s var(--bc-ease) 0.45s forwards;
}
@keyframes wipe {
  to {
    clip-path: inset(0 0 0 0);
  }
}
.hero-mark-n {
  position: absolute;
  top: -0.42em;
  left: -0.62em;
  display: grid;
  place-items: center;
  width: 1.35em;
  height: 1.35em;
  font-family: var(--vp-font-family-mono);
  font-size: 0.3em;
  font-weight: 700;
  line-height: 1;
  letter-spacing: 0;
  color: var(--vp-c-bg);
  background: var(--bc-mark);
  border-radius: 0.22em;
  transform: scale(0);
  animation: pop 0.45s cubic-bezier(0.3, 1.6, 0.5, 1) 1.15s forwards;
}
@keyframes pop {
  to {
    transform: scale(1);
  }
}
.hero-lede {
  max-width: 540px;
  font-size: clamp(1.05rem, 1rem + 0.25vw, 1.2rem);
  line-height: 1.65;
  color: var(--vp-c-text-2);
}
.hero-lede code,
.section-lede code {
  font-family: var(--vp-font-family-mono);
  font-size: 0.9em;
  color: var(--bc-mark);
}
.hero-install {
  margin: 28px 0 20px;
}
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.hero-actions.center {
  justify-content: center;
}
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 42px;
  padding: 0 18px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 560;
  border: 1px solid var(--bc-line-strong);
  color: var(--vp-c-text-1);
  transition: transform 0.2s var(--bc-ease), border-color 0.2s, background-color 0.2s;
}
.btn:hover {
  border-color: var(--vp-c-text-2);
  transform: translateY(-1px);
}
.btn-primary {
  background: var(--vp-c-text-1);
  border-color: var(--vp-c-text-1);
  color: var(--vp-c-bg);
}
.btn-primary:hover {
  background: color-mix(in srgb, var(--vp-c-text-1) 86%, var(--vp-c-bg));
  border-color: transparent;
}
.btn-primary span {
  transition: transform 0.25s var(--bc-ease);
}
.btn-primary:hover span {
  transform: translateX(3px);
}

/* Ruler + status */
.ruler {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  height: 14px;
  border-top: 1px solid var(--bc-line-strong);
  margin-top: 8px;
}
.ruler span {
  width: 1px;
  height: 4px;
  background: var(--bc-line-strong);
}
.ruler span.mid {
  height: 7px;
}
.ruler span.major {
  height: 12px;
  background: var(--vp-c-text-3);
}
.status {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 22px;
  padding: 10px 0 0;
  font-family: var(--vp-font-family-mono);
  font-size: 12px;
  color: var(--vp-c-text-3);
}
.status-item {
  display: inline-flex;
  align-items: center;
  gap: 7px;
}
.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--bc-green);
  animation: bc-pulse 2s infinite;
}

/* Sections */
.section {
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
.eyebrow.center {
  text-align: center;
}
.section-title,
.cta-title {
  font-size: clamp(2rem, 1.3rem + 2.8vw, 3.4rem);
  line-height: 1.06;
  letter-spacing: -0.04em;
  font-weight: 640;
  color: var(--bc-ink);
  margin: 0;
  max-width: 820px;
}
.section-title em,
.cta-title em,
.statement-text em {
  font-style: normal;
  color: var(--bc-mark);
}
.section-lede {
  max-width: 620px;
  margin: 18px 0 0;
  font-size: 1.1rem;
  line-height: 1.65;
  color: var(--vp-c-text-2);
}

/* Loop */
.loop {
  list-style: none;
  padding: 0;
  margin: 48px 0 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  counter-reset: none;
}
.loop li {
  padding: 18px;
  border: 1px solid var(--bc-line);
  border-radius: 16px;
  background: var(--vp-c-bg);
  transition: border-color 0.25s, transform 0.3s var(--bc-ease);
}
.loop li:hover {
  border-color: var(--bc-line-strong);
  transform: translateY(-3px);
}
.loop h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 18px 0 6px;
  font-size: 1.15rem;
  font-weight: 640;
  letter-spacing: -0.02em;
  color: var(--vp-c-text-1);
}
.loop-n {
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  font-family: var(--vp-font-family-mono);
  font-size: 12px;
  font-weight: 700;
  color: var(--bc-mark);
  border: 1.5px solid var(--bc-mark);
  border-radius: 6px;
}
.loop p {
  margin: 0;
  font-size: 14.5px;
  line-height: 1.6;
  color: var(--vp-c-text-2);
}
.loop-viz {
  position: relative;
  height: 150px;
  border-radius: 10px;
  border: 1px dashed var(--bc-line-strong);
  background:
    radial-gradient(circle at 1px 1px, var(--bc-line) 1px, transparent 0) 0 0 / 14px 14px,
    var(--bc-surface);
  overflow: hidden;
}
.viz-act {
  display: grid;
  place-items: center;
}
.viz-act code {
  position: relative;
  z-index: 1;
  font-family: var(--vp-font-family-mono);
  font-size: 22px;
  padding: 8px 16px;
  border-radius: 10px;
  background: var(--vp-c-bg);
  border: 1px solid var(--bc-line-strong);
  color: var(--vp-c-text-1);
}
.viz-act b {
  color: var(--bc-mark);
}
.ripple {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 60px;
  height: 60px;
  margin: -30px 0 0 -30px;
  border-radius: 50%;
  border: 2px solid var(--bc-mark);
  animation: ripple 2.4s var(--bc-ease) infinite;
}
@keyframes ripple {
  0% {
    transform: scale(0.6);
    opacity: 0.9;
  }
  70%,
  100% {
    transform: scale(3.2);
    opacity: 0;
  }
}
.viz-settle {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
  padding: 0 22px;
  font-family: var(--vp-font-family-mono);
  font-size: 13px;
  color: var(--vp-c-text-2);
}
.settle-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.settle-row i {
  position: relative;
  flex: 0 0 120px;
  height: 6px;
  border-radius: 99px;
  background: var(--bc-line);
  overflow: hidden;
}
.settle-row i::after {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--bc-green);
  transform-origin: left;
  transform: scaleX(0);
  animation: fill 3s var(--bc-ease) infinite;
  animation-delay: var(--d);
}
@keyframes fill {
  0% {
    transform: scaleX(0);
  }
  35%,
  85% {
    transform: scaleX(1);
  }
  100% {
    transform: scaleX(1);
    opacity: 0;
  }
}
.look-box {
  position: absolute;
  border: 1.5px solid var(--bc-mark);
  border-radius: 5px;
  background: color-mix(in srgb, var(--bc-mark) 8%, transparent);
  animation: look 3s var(--bc-ease) infinite;
  animation-delay: calc(var(--i) * 0.15s);
}
.look-box b {
  position: absolute;
  top: -9px;
  left: -8px;
  display: grid;
  place-items: center;
  width: 17px;
  height: 17px;
  font-family: var(--vp-font-family-mono);
  font-size: 10.5px;
  color: var(--vp-c-bg);
  background: var(--bc-mark);
  border-radius: 4px;
}
@keyframes look {
  0%,
  8% {
    opacity: 0;
    transform: scale(1.1);
  }
  20%,
  85% {
    opacity: 1;
    transform: none;
  }
  100% {
    opacity: 0;
  }
}

/* Statement */
.statement {
  margin-top: clamp(80px, 10vw, 140px);
  padding: clamp(40px, 6vw, 72px) 0;
  border-top: 1px solid var(--bc-line);
  border-bottom: 1px solid var(--bc-line);
}
.statement-text {
  max-width: 980px;
  margin: 0;
  font-size: clamp(1.7rem, 1rem + 2.6vw, 3rem);
  line-height: 1.2;
  letter-spacing: -0.035em;
  font-weight: 560;
  color: var(--vp-c-text-3);
}
.statement-mark {
  position: relative;
  display: inline-block;
  padding: 0 0.15em;
  margin: 0 0.1em;
  color: var(--vp-c-text-1);
  border: 2px solid var(--bc-mark);
  border-radius: 6px;
}
.statement-mark b {
  position: absolute;
  top: -0.75em;
  left: -0.85em;
  display: grid;
  place-items: center;
  width: 1.45em;
  height: 1.45em;
  line-height: 1;
  font-family: var(--vp-font-family-mono);
  font-size: 0.4em;
  color: var(--vp-c-bg);
  background: var(--bc-mark);
  border-radius: 4px;
}
.facts {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  margin-top: 48px;
}
.facts div {
  font-size: 15px;
  line-height: 1.65;
  color: var(--vp-c-text-2);
  padding-left: 16px;
  border-left: 2px solid var(--bc-line);
}
.facts strong {
  display: block;
  color: var(--vp-c-text-1);
  font-weight: 620;
  margin-bottom: 4px;
}

/* Clients */
.clients {
  padding: clamp(72px, 10vw, 120px) 0 0;
}
.marquee {
  overflow: hidden;
  mask-image: linear-gradient(90deg, transparent, black 12%, black 88%, transparent);
}
.marquee-track {
  display: flex;
  gap: 48px;
  width: max-content;
  animation: marquee 38s linear infinite;
}
.marquee:hover .marquee-track {
  animation-play-state: paused;
}
.marquee-track span {
  font-size: clamp(1.1rem, 1rem + 0.6vw, 1.5rem);
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--vp-c-text-3);
  white-space: nowrap;
  transition: color 0.2s;
}
.marquee-track span:hover {
  color: var(--vp-c-text-1);
}
@keyframes marquee {
  to {
    transform: translateX(calc(-50% - 24px));
  }
}

/* CTA */
.cta {
  margin: clamp(80px, 10vw, 140px) 0 96px;
  padding: clamp(40px, 6vw, 72px) var(--pad);
  border: 1px solid var(--bc-line);
  border-radius: 24px;
  text-align: center;
  background:
    radial-gradient(ellipse at 50% 0%, color-mix(in srgb, var(--bc-mark) 12%, transparent), transparent 60%),
    var(--bc-surface);
}
.cta-title {
  margin: 0 auto;
}
.cta-install {
  display: flex;
  justify-content: center;
  margin: 32px 0 20px;
  text-align: left;
}
.cta-install :deep(.install) {
  width: 100%;
}

@media (max-width: 960px) {
  .hero {
    grid-template-columns: 1fr;
  }
  .loop,
  .facts {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 640px) {
  .hide-sm {
    display: none;
  }
  .hero-title {
    font-size: 2.6rem;
  }
  .pill {
    font-size: 12px;
    max-width: 100%;
  }
}
</style>
