---
hide:
  - navigation
  - toc
---

<div class="bc-page" markdown>

<!-- ============================================================
     HERO
     ============================================================ -->
<div class="bc-hero" aria-label="BrowserControl introduction">
  <div class="bc-hero-copy">
    <span class="bc-eyebrow">
      <span class="bc-eyebrow-dot" aria-hidden="true"></span>
      Vision-first MCP browser automation
    </span>

    <h1 class="bc-hero-headline">
      Your agent <span class="bc-mark-red">sees the page.</span><br>
      Then clicks the number.
    </h1>

    <p class="bc-hero-lede">
      BrowserControl is a local MCP server that gives any AI agent a real
      browser it can <strong>see</strong>, <strong>click</strong>,
      <strong>type</strong>, and <strong>debug</strong> &mdash; using a
      vision-first <strong>Set of Marks</strong> overlay. No selectors. No
      cloud. No API bill.
    </p>

    <div class="bc-hero-cta">
      <a href="getting-started/index.md" class="md-button md-button--primary">
        Get started
      </a>
      <a href="https://github.com/adityasasidhar/browsercontrol"
         class="md-button" rel="noopener">
        View on GitHub
      </a>
    </div>

    <div class="bc-trust-row" aria-label="Trust signals">
      <span><svg viewBox="0 0 16 16" aria-hidden="true"><path fill="currentColor" d="M8 1.5 2.5 4v4c0 3.4 2.4 5.7 5.5 6.5 3.1-.8 5.5-3.1 5.5-6.5V4L8 1.5Z"/></svg> 100% local</span>
      <span><svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M5 8.5 7 10.5 11 6.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg> MIT licensed</span>
      <span><svg viewBox="0 0 16 16" aria-hidden="true"><rect x="2.5" y="3.5" width="11" height="9" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M5.5 6.5 8 8.5 10.5 6.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg> Python 3.11+</span>
      <span><svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="2.5" fill="currentColor"/><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg> MCP-compatible</span>
    </div>
  </div>

  <div class="bc-hero-visual">
    <img src="assets/demo.svg"
         alt="Annotated screenshot of a browser with five red numbered Set of Marks, beside the textual element map returned to the agent and a click(5) action card showing the successful Sign in click."
         class="bc-demo">
  </div>
</div>

<!-- ============================================================
     BADGE STRIP — replaces loose shields.io row
     ============================================================ -->
<div class="bc-badge-strip" aria-label="Project status">
  <a class="bc-badge" href="https://pypi.org/project/browsercontrol/" rel="noopener">
    <span class="bc-badge-dot" aria-hidden="true"></span>
    PyPI &middot; 0.1.4
  </a>
  <a class="bc-badge bc-badge--red" href="https://www.python.org/downloads/" rel="noopener">
    <span class="bc-badge-dot" aria-hidden="true"></span>
    Python 3.11+
  </a>
  <a class="bc-badge bc-badge--violet" href="https://opensource.org/licenses/MIT" rel="noopener">
    <span class="bc-badge-dot" aria-hidden="true"></span>
    MIT License
  </a>
  <a class="bc-badge" href="https://modelcontextprotocol.io/" rel="noopener">
    <span class="bc-badge-dot" aria-hidden="true"></span>
    MCP Compatible
  </a>
  <a class="bc-badge bc-badge--ink" href="https://github.com/adityasasidhar/browsercontrol/actions" rel="noopener">
    <span class="bc-badge-dot" aria-hidden="true"></span>
    CI passing
  </a>
  <a class="bc-badge" href="https://github.com/adityasasidhar/browsercontrol/stargazers" rel="noopener">
    <span class="bc-badge-dot" aria-hidden="true"></span>
    Star on GitHub
  </a>
</div>

<!-- ============================================================
     THREE-STEP SoM EXPLANATION
     ============================================================ -->
<div class="bc-section">
  <span class="bc-section-eyebrow">Set of Marks</span>
  <h2 class="bc-section-title">See the page. Pick a number. Click.</h2>
  <p class="bc-section-lede">
    Every BrowserControl tool that touches the page returns the same shape:
    an annotated screenshot with numbered red boxes over each interactive
    element, plus a textual element map. The model picks a number. The click
    resolves through <code>document.elementFromPoint()</code> so overlays and
    sticky chrome never get in the way.
  </p>

  <div class="bc-steps">
    <div class="bc-step">
      <span class="bc-step-num">1</span>
      <h3 class="bc-step-title">See</h3>
      <p class="bc-step-body">
        A screenshot is annotated with numbered red boxes over every
        interactive element &mdash; inputs, links, buttons, even shadow-DOM
        descendants and same-origin iframes.
      </p>
      <span class="bc-step-arrow" aria-hidden="true">&rarr;</span>
    </div>
    <div class="bc-step">
      <span class="bc-step-num">2</span>
      <h3 class="bc-step-title">Choose</h3>
      <p class="bc-step-body">
        A compact textual element map lists each numbered target with its tag
        and label. The model picks a number &mdash; no selectors, no XPath,
        no hallucinated <code>div.flex &gt; button:nth-child(3)</code>.
      </p>
      <span class="bc-step-arrow" aria-hidden="true">&rarr;</span>
    </div>
    <div class="bc-step">
      <span class="bc-step-num">3</span>
      <h3 class="bc-step-title">Act</h3>
      <p class="bc-step-body">
        The agent calls <code>click(5)</code>. BrowserControl resolves the
        actual DOM element at the box center and drives Chromium. Cookies,
        login state, and history all survive restarts.
      </p>
    </div>
  </div>
</div>

<!-- ============================================================
     PROOF PANEL — annotated screenshot + tool output
     ============================================================ -->
<div class="bc-section">
  <span class="bc-section-eyebrow">Proof</span>
  <h2 class="bc-section-title">One tool call. One annotated screenshot. One click.</h2>
  <p class="bc-section-lede">
    This is the literal shape BrowserControl returns from
    <code>get_screenshot_with_summary()</code>: the marked-up page and the
    element map the model reads. A subsequent <code>click(5)</code> lands on
    the Sign in button.
  </p>

  <div class="bc-proof">
    <div class="bc-proof-img">
      <img src="assets/demo.svg"
           alt="Annotated browser screenshot with five numbered red marks, beside the element map returned to the agent and a click(5) action card showing a successful Sign in click."
           loading="lazy">
    </div>
    <div class="bc-proof-copy">
      <h3>Tool output &mdash; in the model&rsquo;s context</h3>
      <p>
        Every <code>get_*</code>, <code>click</code>, <code>type_text</code>,
        and <code>navigate</code> call returns this shape:
        an image plus a short element map. The model sees pixels and reads
        the list.
      </p>
      <ul class="bc-proof-legend">
        <li><span class="bc-proof-num">1</span><span class="bc-proof-type">input</span><span>Search or jump to&hellip;</span></li>
        <li><span class="bc-proof-num">2</span><span class="bc-proof-type">a</span><span>Pulls</span></li>
        <li><span class="bc-proof-num">3</span><span class="bc-proof-type">a</span><span>Issues</span></li>
        <li><span class="bc-proof-num">4</span><span class="bc-proof-type">a</span><span>Codespaces</span></li>
        <li><span class="bc-proof-num">5</span><span class="bc-proof-type">button</span><span>Sign in</span></li>
      </ul>
    </div>
  </div>
</div>

<!-- ============================================================
     CAPABILITY CARDS
     ============================================================ -->
<div class="bc-section">
  <span class="bc-section-eyebrow">Why BrowserControl</span>
  <h2 class="bc-section-title">Built for the agent loop. Not for humans.</h2>
  <p class="bc-section-lede">
    Every detail below exists because AI agents fail differently than
    humans do. BrowserControl is shaped around their failure modes &mdash;
    not around a human test runner.
  </p>

  <div class="bc-cap-grid">
    <div class="bc-cap">
      <span class="bc-cap-icon bc-cap-icon--red" aria-hidden="true">#</span>
      <h3 class="bc-cap-title">Vision-first, selector-free</h3>
      <p class="bc-cap-body">
        Numbered red boxes. The agent picks a number. No CSS selectors, no
        XPath, no hallucinated
        <code>div.flex-container &gt; button.btn-primary:nth-child(3)</code>.
      </p>
    </div>

    <div class="bc-cap">
      <span class="bc-cap-icon bc-cap-icon--violet" aria-hidden="true">{ }</span>
      <h3 class="bc-cap-title">Shadow DOM &amp; iframe aware</h3>
      <p class="bc-cap-body">
        Recursively descends into open shadow roots and same-origin iframes
        with coordinate-offset compensation. Modern web apps just work.
      </p>
    </div>

    <div class="bc-cap">
      <span class="bc-cap-icon bc-cap-icon--mint" aria-hidden="true">&#8634;</span>
      <h3 class="bc-cap-title">True persistent sessions</h3>
      <p class="bc-cap-body">
        Uses <code>launch_persistent_context</code>. Cookies, localStorage,
        login state, and history all survive restarts. Log in once.
      </p>
    </div>

    <div class="bc-cap">
      <span class="bc-cap-icon bc-cap-icon--red" aria-hidden="true">&#9881;</span>
      <h3 class="bc-cap-title">Built-in devtools</h3>
      <p class="bc-cap-body">
        Console logs, network requests with timing, JS errors, page
        performance, element inspection, computed styles. No second tool
        needed.
      </p>
    </div>

    <div class="bc-cap">
      <span class="bc-cap-icon bc-cap-icon--violet" aria-hidden="true">&#9737;</span>
      <h3 class="bc-cap-title">100% local &amp; private</h3>
      <p class="bc-cap-body">
        No LLM API key. No cloud. No telemetry. No usage cap. Your browsing
        stays on your machine &mdash; including the screenshots.
      </p>
    </div>

    <div class="bc-cap">
      <span class="bc-cap-icon bc-cap-icon--mint" aria-hidden="true">$0</span>
      <h3 class="bc-cap-title">Zero marginal cost</h3>
      <p class="bc-cap-body">
        Runs on your hardware. <strong>$0 per 1,000 actions</strong> &mdash;
        no API spend, no per-action fees, no surprise invoices at the end of
        the month.
      </p>
    </div>
  </div>
</div>

<!-- ============================================================
     INSTALL BLOCK
     ============================================================ -->
<div class="bc-section">
  <span class="bc-section-eyebrow">Install</span>
  <h2 class="bc-section-title">Up and running in 30 seconds.</h2>
  <p class="bc-section-lede">
    Pick your installer. Chromium auto-installs on first run, so there is
    no system-level browser binary to manage.
  </p>

<div class="bc-install">

<h3>Install BrowserControl</h3>
<p>Pick whichever package manager you already have. Chromium auto-installs on first run.</p>

<div class="bc-install-tabs">
  <div class="bc-install-tab">
    <span class="bc-install-tab-label">pip</span>
    <pre class="bc-install-cmd"><code>pip install browsercontrol</code></pre>
  </div>
  <div class="bc-install-tab">
    <span class="bc-install-tab-label">uv</span>
    <pre class="bc-install-cmd"><code>uv add browsercontrol</code></pre>
  </div>
  <div class="bc-install-tab">
    <span class="bc-install-tab-label">pipx</span>
    <pre class="bc-install-cmd"><code>pipx install browsercontrol</code></pre>
  </div>
</div>

<div class="bc-install-note">
  If Chromium fails to auto-install for any reason, run it once manually:
  <code>python -m playwright install chromium</code>. That&rsquo;s it.
</div>

</div>
</div>

<!-- ============================================================
     DOC PATH CARDS
     ============================================================ -->
<div class="bc-section">
  <span class="bc-section-eyebrow">Documentation</span>
  <h2 class="bc-section-title">Where to next.</h2>
  <p class="bc-section-lede">
    Pick the path that matches the moment you're in. Everything is organized
    so the next click is obvious.
  </p>

  <div class="bc-doc-grid">
    <a class="bc-doc" href="getting-started/index.md">
      <span class="bc-doc-eyebrow">Start here</span>
      <h3 class="bc-doc-title">Getting started</h3>
      <p class="bc-doc-body">Install, connect, and run your first session in under five minutes.</p>
      <span class="bc-doc-arrow">&rarr;</span>
    </a>
    <a class="bc-doc" href="tools/index.md">
      <span class="bc-doc-eyebrow">Reference</span>
      <h3 class="bc-doc-title">Tool reference</h3>
      <p class="bc-doc-body">Every MCP tool, every parameter, organized by category.</p>
      <span class="bc-doc-arrow">&rarr;</span>
    </a>
    <a class="bc-doc" href="guides/index.md">
      <span class="bc-doc-eyebrow">Patterns</span>
      <h3 class="bc-doc-title">Guides</h3>
      <p class="bc-doc-body">Real-world recipes: research, debugging, recording, forms, multi-tab.</p>
      <span class="bc-doc-arrow">&rarr;</span>
    </a>
    <a class="bc-doc" href="concepts/index.md">
      <span class="bc-doc-eyebrow">Under the hood</span>
      <h3 class="bc-doc-title">Concepts</h3>
      <p class="bc-doc-body">How Set of Marks works, the action loop, and why it beats selectors.</p>
      <span class="bc-doc-arrow">&rarr;</span>
    </a>
  </div>
</div>

<!-- ============================================================
     FINAL CTA BAND
     ============================================================ -->
<div class="bc-final" aria-label="Install BrowserControl">
  <div class="bc-final-copy">
    <h3>Give your agent a browser that actually sees.</h3>
    <p>
      One install. Zero cloud. The shortest path from "ask the model" to
      "watch the browser do the thing."
    </p>
  </div>
  <div class="bc-final-cta">
    <a href="getting-started/installation.md" class="md-button md-button--primary">
      Install BrowserControl
    </a>
    <a href="https://github.com/adityasasidhar/browsercontrol"
       class="md-button" rel="noopener">
      Star on GitHub
    </a>
  </div>
</div>

</div>
