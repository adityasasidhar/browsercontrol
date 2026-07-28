---
hide:
  - navigation
  - toc
---
<div class="bc-page">
  <!-- ===================================================================
       HERO
       =================================================================== -->
  <section class="bc-hero">
    <div class="bc-wrap bc-hero-inner">
      <div class="bc-hero-copy">
        <a class="bc-pill" href="concepts/set-of-marks/">
          <span class="bc-pill-tag">SoM</span>
          <span>What Set of Marks actually does</span>
          <span class="bc-pill-arrow" aria-hidden="true">&rarr;</span>
        </a>
        <h1 class="bc-h1">Your agent <span class="bc-marked">sees</span> the page.<br>Then clicks the number.</h1>
        <p class="bc-hero-lede">BrowserControl is a local MCP server that hands any AI agent a real Chromium browser it can <strong>see</strong>, <strong>click</strong>, <strong>type</strong> into, and <strong>debug</strong> — through numbered marks drawn over every interactive element. No selectors. No cloud. No API bill.</p>
        <div class="bc-cta-row">
          <a class="bc-btn bc-btn--primary" href="getting-started/">
            Get started
            <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 8h11M9 3.5 13.5 8 9 12.5"/></svg>
          </a>
          <a class="bc-btn bc-btn--ghost" href="https://github.com/adityasasidhar/browsercontrol" rel="noopener">
            <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/></svg>
            View on GitHub
          </a>
        </div>
        <div class="bc-hero-cmd"><span class="bc-prompt" aria-hidden="true">$</span><code>pip install browsercontrol</code></div>
        <ul class="bc-trust">
          <li><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 8.5 3.2 3.2L13 5"/></svg> Runs 100% on your machine</li>
          <li><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 8.5 3.2 3.2L13 5"/></svg> No LLM API key</li>
          <li><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 8.5 3.2 3.2L13 5"/></svg> MIT licensed</li>
          <li><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 8.5 3.2 3.2L13 5"/></svg> Python 3.11+</li>
        </ul>
      </div>
      <!-- The hero visual is real markup, not a screenshot, so it follows
           the reader's colour scheme and stays crisp at any resolution. -->
      <div class="bc-hero-visual">
        <div class="bc-scope" role="img" aria-label="A browser cycling through four Set of Marks scenarios. Signing in: the search field, a nav link, the email and password fields and the Sign in button are outlined in red and numbered one to five, and the agent calls click(5). Filtering a shop search: the agent calls select_option(2) to re-sort 48 results. Debugging a local checkout page: the console shows errors and the agent calls get_page_errors(). Checking a mobile layout: the agent calls set_viewport(390, 844) and the page is re-marked.">
          <div class="bc-window">
            <div class="bc-window-bar">
              <span class="bc-dot"></span><span class="bc-dot"></span><span class="bc-dot"></span>
              <span class="bc-url-stack">
                <span class="bc-window-url bc-urlscene" data-s="0" style="--s:0">app.example.com/sign-in</span>
                <span class="bc-window-url bc-urlscene" data-s="1" style="--s:1">shop.example.com/search?q=desk+lamp</span>
                <span class="bc-window-url bc-urlscene" data-s="2" style="--s:2">localhost:3000/checkout</span>
                <span class="bc-window-url bc-urlscene" data-s="3" style="--s:3">app.example.com/signup &mdash; 390&times;844</span>
              </span>
              <span class="bc-window-tag">SoM</span>
            </div>
            <div class="bc-viewport">
              <!-- Scene 1 — sign in -->
              <div class="bc-scene" data-s="0" style="--s:0">
                <span class="bc-topbar"></span>
                <span class="bc-sk bc-sk--round" style="left:4%;top:4%;width:5%;height:5%"></span>
                <span class="bc-sk" style="left:12%;top:5.2%;width:7%;height:2.6%"></span>
                <span class="bc-sk" style="left:21%;top:5.2%;width:6%;height:2.6%"></span>
                <span class="bc-sk" style="left:29%;top:5.2%;width:8%;height:2.6%"></span>
                <span class="bc-sk bc-sk--field" style="left:58%;top:3.5%;width:26%;height:6%"></span>
                <span class="bc-sk bc-sk--round" style="left:88%;top:3.5%;width:6%;height:6%"></span>
                <span class="bc-panel"></span>
                <span class="bc-sk bc-sk--strong" style="left:30%;top:30%;width:24%;height:4%"></span>
                <span class="bc-sk" style="left:30%;top:36.5%;width:40%;height:2.2%"></span>
                <span class="bc-sk bc-sk--field" style="left:30%;top:43%;width:40%;height:7%"></span>
                <span class="bc-sk bc-sk--field" style="left:30%;top:53%;width:40%;height:7%"></span>
                <span class="bc-sk bc-sk--btn" style="left:30%;top:64%;width:40%;height:7.5%"></span>
                <span class="bc-sk" style="left:36%;top:76.5%;width:28%;height:2.2%"></span>
                <span class="bc-mark" data-n="1" style="--x:57.5%;--y:3%;--w:27%;--h:7%;--i:0"></span>
                <span class="bc-mark" data-n="2" style="--x:11%;--y:4.6%;--w:9%;--h:3.8%;--i:1"></span>
                <span class="bc-mark" data-n="3" style="--x:29%;--y:42.2%;--w:42%;--h:8.6%;--i:2"></span>
                <span class="bc-mark" data-n="4" style="--x:29%;--y:52.2%;--w:42%;--h:8.6%;--i:3"></span>
                <span class="bc-mark" data-n="5" style="--x:29%;--y:63.2%;--w:42%;--h:9.1%;--i:4"></span>
              </div>
              <!-- Scene 2 — search results with filters -->
              <div class="bc-scene" data-s="1" style="--s:1">
                <span class="bc-topbar"></span>
                <span class="bc-sk bc-sk--round" style="left:4%;top:4%;width:5%;height:5%"></span>
                <span class="bc-sk bc-sk--field" style="left:14%;top:3.5%;width:40%;height:6%"></span>
                <span class="bc-sk" style="left:60%;top:5.2%;width:7%;height:2.6%"></span>
                <span class="bc-sk" style="left:70%;top:5.2%;width:6%;height:2.6%"></span>
                <span class="bc-sk bc-sk--round" style="left:88%;top:3.5%;width:6%;height:6%"></span>
                <span class="bc-sk bc-sk--field" style="left:4%;top:18%;width:20%;height:74%"></span>
                <span class="bc-sk bc-sk--strong" style="left:6.5%;top:21%;width:12%;height:2.6%"></span>
                <span class="bc-sk" style="left:6.5%;top:27%;width:3%;height:3%"></span>
                <span class="bc-sk" style="left:11%;top:27.6%;width:11%;height:2.2%"></span>
                <span class="bc-sk" style="left:6.5%;top:34%;width:3%;height:3%"></span>
                <span class="bc-sk" style="left:11%;top:34.6%;width:9%;height:2.2%"></span>
                <span class="bc-sk" style="left:6.5%;top:41%;width:3%;height:3%"></span>
                <span class="bc-sk" style="left:11%;top:41.6%;width:12%;height:2.2%"></span>
                <span class="bc-sk" style="left:6.5%;top:48%;width:3%;height:3%"></span>
                <span class="bc-sk" style="left:11%;top:48.6%;width:10%;height:2.2%"></span>
                <span class="bc-sk" style="left:6.5%;top:58%;width:14%;height:1.6%"></span>
                <span class="bc-sk" style="left:6.5%;top:64%;width:3%;height:3%"></span>
                <span class="bc-sk" style="left:11%;top:64.6%;width:11%;height:2.2%"></span>
                <span class="bc-sk" style="left:6.5%;top:71%;width:3%;height:3%"></span>
                <span class="bc-sk" style="left:11%;top:71.6%;width:9%;height:2.2%"></span>
                <span class="bc-sk" style="left:6.5%;top:78%;width:3%;height:3%"></span>
                <span class="bc-sk" style="left:11%;top:78.6%;width:12%;height:2.2%"></span>
                <span class="bc-sk bc-sk--field" style="left:74%;top:17%;width:22%;height:6%"></span>
                <span class="bc-sk" style="left:28%;top:19%;width:16%;height:2.4%"></span>
                <span class="bc-sk bc-sk--field" style="left:28%;top:26%;width:20%;height:28%"></span>
                <span class="bc-sk bc-sk--field" style="left:52%;top:26%;width:20%;height:28%"></span>
                <span class="bc-sk bc-sk--field" style="left:76%;top:26%;width:20%;height:28%"></span>
                <span class="bc-sk bc-sk--btn" style="left:28%;top:57%;width:20%;height:6.5%"></span>
                <span class="bc-sk" style="left:52%;top:57%;width:20%;height:6.5%"></span>
                <span class="bc-sk" style="left:76%;top:57%;width:20%;height:6.5%"></span>
                <span class="bc-sk bc-sk--field" style="left:28%;top:69%;width:20%;height:23%"></span>
                <span class="bc-sk bc-sk--field" style="left:52%;top:69%;width:20%;height:23%"></span>
                <span class="bc-sk bc-sk--field" style="left:76%;top:69%;width:20%;height:23%"></span>
                <span class="bc-mark" data-n="1" style="--x:13.5%;--y:3%;--w:41%;--h:7%;--i:0"></span>
                <span class="bc-mark" data-n="2" style="--x:73.5%;--y:16.2%;--w:23%;--h:7.8%;--i:1"></span>
                <span class="bc-mark" data-n="3" style="--x:6%;--y:26.2%;--w:18%;--h:4.6%;--i:2"></span>
                <span class="bc-mark" data-n="4" style="--x:27.5%;--y:25.2%;--w:21%;--h:29.5%;--i:3"></span>
                <span class="bc-mark" data-n="5" style="--x:27.5%;--y:56.2%;--w:21%;--h:8%;--i:4"></span>
              </div>
              <!-- Scene 3 — debugging a local checkout, console docked -->
              <div class="bc-scene" data-s="2" style="--s:2">
                <span class="bc-topbar"></span>
                <span class="bc-sk bc-sk--round" style="left:4%;top:4%;width:5%;height:5%"></span>
                <span class="bc-sk bc-sk--field" style="left:26%;top:3.5%;width:34%;height:6%"></span>
                <span class="bc-sk bc-sk--round" style="left:88%;top:3.5%;width:6%;height:6%"></span>
                <span class="bc-sk bc-sk--strong" style="left:6%;top:20%;width:26%;height:4.5%"></span>
                <span class="bc-sk" style="left:6%;top:28%;width:50%;height:2.2%"></span>
                <span class="bc-sk" style="left:6%;top:33%;width:40%;height:2.2%"></span>
                <span class="bc-sk bc-sk--field" style="left:6%;top:39%;width:34%;height:7%"></span>
                <span class="bc-sk bc-sk--btn" style="left:6%;top:50%;width:20%;height:7.5%"></span>
                <span class="bc-sk" style="left:30%;top:52.5%;width:14%;height:2.6%"></span>
                <span class="bc-sk bc-sk--field" style="left:62%;top:20%;width:32%;height:26%"></span>
                <span class="bc-console"></span>
                <span class="bc-sk bc-sk--err" style="left:3%;top:64%;width:58%;height:3.4%"></span>
                <span class="bc-sk bc-sk--err" style="left:3%;top:70%;width:46%;height:3.4%"></span>
                <span class="bc-sk bc-sk--warn" style="left:3%;top:76%;width:38%;height:3.4%"></span>
                <span class="bc-sk bc-sk--dim" style="left:3%;top:82%;width:52%;height:3.4%"></span>
                <span class="bc-mark" data-n="1" style="--x:25.5%;--y:3%;--w:35%;--h:7%;--i:0"></span>
                <span class="bc-mark" data-n="2" style="--x:5.5%;--y:38.2%;--w:35%;--h:8.6%;--i:1"></span>
                <span class="bc-mark" data-n="3" style="--x:5.5%;--y:49.2%;--w:21%;--h:9%;--i:2"></span>
                <span class="bc-mark" data-n="4" style="--x:29%;--y:51.6%;--w:15%;--h:4%;--i:3"></span>
                <span class="bc-mark" data-n="5" style="--x:61.5%;--y:19.2%;--w:33%;--h:27.5%;--i:4"></span>
              </div>
              <!-- Scene 4 — same page re-marked at a phone viewport -->
              <div class="bc-scene" data-s="3" style="--s:3">
                <span class="bc-topbar"></span>
                <span class="bc-sk bc-sk--round" style="left:4%;top:4%;width:5%;height:5%"></span>
                <span class="bc-sk bc-sk--field" style="left:30%;top:3.5%;width:26%;height:6%"></span>
                <span class="bc-sk bc-sk--round" style="left:88%;top:3.5%;width:6%;height:6%"></span>
                <span class="bc-phone" style="left:36%;top:18%;width:28%;height:76%"></span>
                <span class="bc-sk bc-sk--round" style="left:45%;top:21%;width:10%;height:1.6%"></span>
                <span class="bc-sk bc-sk--strong" style="left:39%;top:26%;width:18%;height:3.5%"></span>
                <span class="bc-sk" style="left:39%;top:31.5%;width:22%;height:2%"></span>
                <span class="bc-sk bc-sk--field" style="left:39%;top:36%;width:22%;height:6.5%"></span>
                <span class="bc-sk bc-sk--field" style="left:39%;top:45%;width:22%;height:6.5%"></span>
                <span class="bc-sk bc-sk--btn" style="left:39%;top:54%;width:22%;height:7%"></span>
                <span class="bc-sk" style="left:42%;top:64%;width:16%;height:2%"></span>
                <span class="bc-sk" style="left:39%;top:71%;width:22%;height:2%"></span>
                <span class="bc-sk" style="left:39%;top:76%;width:18%;height:2%"></span>
                <span class="bc-sk" style="left:39%;top:84%;width:22%;height:5%"></span>
                <span class="bc-mark" data-n="1" style="--x:29.5%;--y:3%;--w:27%;--h:7%;--i:0"></span>
                <span class="bc-mark" data-n="2" style="--x:38.5%;--y:35.2%;--w:23%;--h:8%;--i:1"></span>
                <span class="bc-mark" data-n="3" style="--x:38.5%;--y:44.2%;--w:23%;--h:8%;--i:2"></span>
                <span class="bc-mark" data-n="4" style="--x:38.5%;--y:53.2%;--w:23%;--h:8.5%;--i:3"></span>
                <span class="bc-mark" data-n="5" style="--x:41.5%;--y:63.2%;--w:17%;--h:3.6%;--i:4"></span>
              </div>
            </div>
          </div>
          <div class="bc-map">
            <div class="bc-map-head"><span>element_map</span><b>5</b></div>
            <div class="bc-map-stack">
              <div class="bc-mapscene" data-s="0" style="--s:0">
                <ul class="bc-map-list">
                  <li style="--i:0"><span class="n">1</span><span class="t">input</span><span class="l">Search or jump to&hellip;</span></li>
                  <li style="--i:1"><span class="n">2</span><span class="t">a</span><span class="l">Pull requests</span></li>
                  <li style="--i:2"><span class="n">3</span><span class="t">input</span><span class="l">Email address</span></li>
                  <li style="--i:3"><span class="n">4</span><span class="t">input</span><span class="l">Password</span></li>
                  <li style="--i:4"><span class="n">5</span><span class="t">button</span><span class="l">Sign in</span></li>
                </ul>
                <div class="bc-map-call"><span class="arrow">&rsaquo;</span> <span class="fn">click(5)</span><br><span class="ok">&check; clicked "Sign in" &rarr; /dashboard</span></div>
              </div>
              <div class="bc-mapscene" data-s="1" style="--s:1">
                <ul class="bc-map-list">
                  <li style="--i:0"><span class="n">1</span><span class="t">input</span><span class="l">Search products</span></li>
                  <li style="--i:1"><span class="n">2</span><span class="t">select</span><span class="l">Sort: Featured</span></li>
                  <li style="--i:2"><span class="n">3</span><span class="t">input</span><span class="l">In stock only</span></li>
                  <li style="--i:3"><span class="n">4</span><span class="t">a</span><span class="l">Cove LED Desk Lamp</span></li>
                  <li style="--i:4"><span class="n">5</span><span class="t">button</span><span class="l">Add to cart</span></li>
                </ul>
                <div class="bc-map-call"><span class="arrow">&rsaquo;</span> <span class="fn">select_option(2, "Price &uarr;")</span><br><span class="ok">&check; re-sorted &mdash; 48 results</span></div>
              </div>
              <div class="bc-mapscene" data-s="2" style="--s:2">
                <ul class="bc-map-list">
                  <li style="--i:0"><span class="n">1</span><span class="t">input</span><span class="l">Search orders</span></li>
                  <li style="--i:1"><span class="n">2</span><span class="t">input</span><span class="l">Promo code</span></li>
                  <li style="--i:2"><span class="n">3</span><span class="t">button</span><span class="l">Place order</span></li>
                  <li style="--i:3"><span class="n">4</span><span class="t">a</span><span class="l">Terms of sale</span></li>
                  <li style="--i:4"><span class="n">5</span><span class="t">a</span><span class="l">Order summary</span></li>
                </ul>
                <div class="bc-map-call"><span class="arrow">&rsaquo;</span> <span class="fn">get_page_errors()</span><br><span class="err">&times; TypeError: cart.total is undefined</span></div>
              </div>
              <div class="bc-mapscene" data-s="3" style="--s:3">
                <ul class="bc-map-list">
                  <li style="--i:0"><span class="n">1</span><span class="t">input</span><span class="l">Search</span></li>
                  <li style="--i:1"><span class="n">2</span><span class="t">input</span><span class="l">Full name</span></li>
                  <li style="--i:2"><span class="n">3</span><span class="t">input</span><span class="l">Work email</span></li>
                  <li style="--i:3"><span class="n">4</span><span class="t">button</span><span class="l">Continue</span></li>
                  <li style="--i:4"><span class="n">5</span><span class="t">a</span><span class="l">Need help?</span></li>
                </ul>
                <div class="bc-map-call"><span class="arrow">&rsaquo;</span> <span class="fn">set_viewport(390, 844)</span><br><span class="ok">&check; re-marked at 390&times;844</span></div>
              </div>
            </div>
          </div>
          <div class="bc-ticks" aria-hidden="true">
            <span class="bc-tick" style="--s:0"></span>
            <span class="bc-tick" style="--s:1"></span>
            <span class="bc-tick" style="--s:2"></span>
            <span class="bc-tick" style="--s:3"></span>
          </div>
        </div>
      </div>
    </div>
  </section>
  <!-- ===================================================================
       STAT STRIP
       =================================================================== -->
  <div class="bc-stats">
    <div class="bc-wrap bc-stats-grid">
      <div class="bc-stat">
        <span class="bc-stat-num">39</span>
        <span class="bc-stat-label">MCP tools, every one returning a fresh annotated screenshot</span>
      </div>
      <div class="bc-stat">
        <span class="bc-stat-num">7</span>
        <span class="bc-stat-label">Categories: navigation, interaction, tabs, forms, content, devtools, recording</span>
      </div>
      <div class="bc-stat">
        <span class="bc-stat-num"><em>$0</em></span>
        <span class="bc-stat-label">Marginal cost per 1,000 browser actions</span>
      </div>
      <div class="bc-stat">
        <span class="bc-stat-num">0</span>
        <span class="bc-stat-label">Bytes of your browsing sent anywhere off-device</span>
      </div>
    </div>
  </div>
  <!-- ===================================================================
       THE LOOP
       =================================================================== -->
  <section class="bc-section bc-section--tint">
    <div class="bc-wrap">
      <div class="bc-head">
        <p class="bc-eyebrow">The loop</p>
        <h2 class="bc-h2">See the page. Pick a number. Act.</h2>
        <p class="bc-lede">Every tool that touches the page returns the same two things: an annotated screenshot and a textual element map. The model reads pixels <em>and</em> labels, then names a number. Clicks resolve through <code>document.elementFromPoint()</code>, so sticky headers, overlays, and cookie banners never steal the hit.</p>
      </div>
      <div class="bc-steps">
        <div class="bc-step">
          <span class="bc-step-n">1</span>
          <h3>See</h3>
          <p>A screenshot comes back with numbered red boxes over every interactive element — inputs, links, buttons, open shadow-DOM descendants, and same-origin iframes with their coordinate offsets already applied.</p>
        </div>
        <div class="bc-step">
          <span class="bc-step-n">2</span>
          <h3>Choose</h3>
          <p>Alongside it, a compact element map lists each mark with its tag and accessible label. The model picks a number — never a brittle <code>div.flex &gt; button:nth-child(3)</code> it hallucinated from stale HTML.</p>
        </div>
        <div class="bc-step">
          <span class="bc-step-n">3</span>
          <h3>Act</h3>
          <p>The agent calls <code>click(5)</code>. BrowserControl resolves the live DOM node under that box, drives Chromium, and re-marks the new page. Cookies and login state survive restarts.</p>
        </div>
      </div>
      <div class="bc-transcript">
        <div class="bc-transcript-head">
          <span class="bc-dot"></span><span class="bc-dot"></span><span class="bc-dot"></span>
          <span class="sp">agent session</span>
        </div>
        <pre class="bc-transcript-body"><span class="a">agent</span>  <span class="c">&rsaquo;</span> <span class="f">navigate_to</span>(<span class="s">"https://app.example.com/sign-in"</span>)
       <span class="c">&lsaquo; screenshot + element_map &mdash; <span class="m">5</span> elements marked</span>
<span class="a">agent</span>  <span class="c">&rsaquo;</span> <span class="f">type_text</span>(<span class="m">3</span>, <span class="s">"ada@example.com"</span>)
<span class="a">agent</span>  <span class="c">&rsaquo;</span> <span class="f">type_text</span>(<span class="m">4</span>, <span class="s">"&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;"</span>)
<span class="a">agent</span>  <span class="c">&rsaquo;</span> <span class="f">click</span>(<span class="m">5</span>)
       <span class="c">&lsaquo; <span class="s">&check;</span> clicked &lt;button&gt; "Sign in" &rarr; /dashboard &mdash; <span class="m">12</span> new elements</span>
<span class="a">agent</span>  <span class="c">&rsaquo;</span> <span class="f">get_console_logs</span>()
       <span class="c">&lsaquo; <span class="s">0 errors</span>, 2 warnings</span></pre>
      </div>
    </div>
  </section>
  <!-- ===================================================================
       FEATURES
       =================================================================== -->
  <section class="bc-section">
    <div class="bc-wrap">
      <div class="bc-head">
        <p class="bc-eyebrow">Why it works</p>
        <h2 class="bc-h2">Shaped around how agents fail, not how humans test.</h2>
        <p class="bc-lede">Selector-driven automation assumes you already know the DOM. Agents don&rsquo;t — they guess, and they guess wrong. Every decision below exists to remove one of those guesses.</p>
      </div>
      <div class="bc-features">
        <div class="bc-feature">
          <span class="bc-feature-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="7.5"/><path d="M12 1.5v3M12 19.5v3M1.5 12h3M19.5 12h3"/><circle cx="12" cy="12" r="2.2" fill="currentColor" stroke="none"/></svg></span>
          <h3>Vision-first, selector-free</h3>
          <p>Numbered red boxes over the live page. The agent names a number. There is no CSS selector to get wrong, no XPath to invent, no class name to hallucinate.</p>
        </div>
        <div class="bc-feature bc-feature--violet">
          <span class="bc-feature-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 3 8l9 5 9-5-9-5Z"/><path d="m3 16 9 5 9-5"/><path d="m3 12 9 5 9-5"/></svg></span>
          <h3>Shadow DOM &amp; iframe aware</h3>
          <p>The element collector descends recursively into open shadow roots and same-origin iframes, compensating coordinate offsets as it goes. Component-framework apps just work.</p>
        </div>
        <div class="bc-feature bc-feature--teal">
          <span class="bc-feature-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 12a8.5 8.5 0 1 1-2.9-6.4"/><path d="M20.5 3.5v5h-5"/></svg></span>
          <h3>Sessions that actually persist</h3>
          <p>Chromium runs against a real profile directory via <code>launch_persistent_context</code>. Cookies, localStorage, and login state survive server restarts. Log in once, not once per run.</p>
        </div>
        <div class="bc-feature">
          <span class="bc-feature-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2.75" y="4" width="18.5" height="16" rx="2.5"/><path d="m7 9.5 3 2.5-3 2.5"/><path d="M13 15h4"/></svg></span>
          <h3>DevTools in the same server</h3>
          <p>Console logs, network requests with timing, uncaught JS errors, performance metrics, computed styles, cookies. Debugging a page needs no second MCP server.</p>
        </div>
        <div class="bc-feature bc-feature--violet">
          <span class="bc-feature-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.5 4.5 5.6v5.2c0 4.6 3.1 8.1 7.5 9.7 4.4-1.6 7.5-5.1 7.5-9.7V5.6L12 2.5Z"/><path d="m8.8 11.8 2.3 2.3 4.1-4.4"/></svg></span>
          <h3>Local, private, uncapped</h3>
          <p>No cloud relay, no telemetry, no vendor rate limit. Screenshots are captured, annotated, and consumed on your machine — including the ones of your logged-in accounts.</p>
        </div>
        <div class="bc-feature bc-feature--teal">
          <span class="bc-feature-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M13.5 2 4.5 13.5h6l-1.2 8.5 9.2-12h-6L13.5 2Z"/></svg></span>
          <h3>Zero marginal cost</h3>
          <p>Everything runs on hardware you already pay for. A thousand clicks cost exactly the same as one: nothing. No per-action pricing, no surprise invoice.</p>
        </div>
      </div>
    </div>
  </section>
  <!-- ===================================================================
       COMPARISON
       =================================================================== -->
  <section class="bc-section bc-section--tint">
    <div class="bc-wrap">
      <div class="bc-head">
        <p class="bc-eyebrow">How it compares</p>
        <h2 class="bc-h2">Three ways to give an agent a browser.</h2>
        <p class="bc-lede">Selector-based drivers are precise but blind. Hosted browser agents can see, but they meter every action and route your session through someone else&rsquo;s infrastructure.</p>
      </div>
      <div class="bc-compare-scroll">
        <table class="bc-compare">
          <thead>
            <tr>
              <th scope="col">&nbsp;</th>
              <th scope="col" class="us">BrowserControl</th>
              <th scope="col">Selector-driven MCP</th>
              <th scope="col">Hosted browser agent</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">How the agent targets</th>
              <td class="us">Numbered marks on a screenshot</td>
              <td>CSS / XPath it has to guess</td>
              <td>Natural language, resolved remotely</td>
            </tr>
            <tr>
              <th scope="row">Sees the rendered page</th>
              <td class="us">Yes, on every single call</td>
              <td>No &mdash; text and DOM only</td>
              <td>Yes</td>
            </tr>
            <tr>
              <th scope="row">Where it runs</th>
              <td class="us">Your machine</td>
              <td>Your machine</td>
              <td>Vendor cloud</td>
            </tr>
            <tr>
              <th scope="row">Cost per 1,000 actions</th>
              <td class="us">$0</td>
              <td>$0</td>
              <td>Metered per action</td>
            </tr>
            <tr>
              <th scope="row">Logged-in sessions</th>
              <td class="us">Persistent local profile</td>
              <td>Usually per-run, ephemeral</td>
              <td>Credentials leave your machine</td>
            </tr>
            <tr>
              <th scope="row">Console &amp; network access</th>
              <td class="us">Built in</td>
              <td>Rarely</td>
              <td>Rarely exposed</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
  <!-- ===================================================================
       QUICKSTART
       =================================================================== -->
  <section class="bc-section">
    <div class="bc-wrap">
      <div class="bc-head">
        <p class="bc-eyebrow">Quickstart</p>
        <h2 class="bc-h2">Installed and wired up in about a minute.</h2>
        <p class="bc-lede">Chromium installs itself on first run, so there is no system browser binary to manage and nothing to keep in sync.</p>
      </div>
      <div class="bc-quick">
        <div>
          <ol class="bc-quick-steps">
            <li>
              <h3>Install the package</h3>
              <p>Use whichever package manager you already have.</p>
              <div class="bc-cmd"><span class="bc-prompt" aria-hidden="true">$</span>pip install browsercontrol</div>
              <div class="bc-cmd"><span class="bc-prompt" aria-hidden="true">$</span>uv add browsercontrol</div>
              <div class="bc-cmd"><span class="bc-prompt" aria-hidden="true">$</span>pipx install browsercontrol</div>
            </li>
            <li>
              <h3>Point your client at it</h3>
              <p>Drop the server block on the right into your MCP client config — Claude Desktop, Claude Code, Cursor, or anything else that speaks MCP.</p>
            </li>
            <li>
              <h3>Ask for something visual</h3>
              <p>&ldquo;Open my dashboard, screenshot it, and tell me which network requests failed.&rdquo; The first call boots Chromium and marks the page. See the <a href="getting-started/first-session/">first session walkthrough</a>.</p>
            </li>
          </ol>
        </div>
        <div>
          <div class="bc-code-card">
            <div class="bc-code-card-head"><span>claude_desktop_config.json</span><span class="badge">json</span></div>
            <pre>{
  <span class="k">"mcpServers"</span><span class="p">:</span> {
    <span class="k">"browsercontrol"</span><span class="p">:</span> {
      <span class="k">"command"</span><span class="p">:</span> <span class="v">"browsercontrol"</span>
    }
  }
}</pre>
          </div>
          <p class="bc-quick-note">If Chromium ever fails to install itself, run <code>python -m playwright install chromium</code> once. Every configuration option is an environment variable — see <a href="configuration/">Configuration</a>.</p>
        </div>
      </div>
    </div>
  </section>
  <!-- ===================================================================
       DOC PATHS
       =================================================================== -->
  <section class="bc-section bc-section--tint">
    <div class="bc-wrap">
      <div class="bc-head bc-head--center">
        <p class="bc-eyebrow">Documentation</p>
        <h2 class="bc-h2">Where to go next.</h2>
        <p class="bc-lede">Four entry points, depending on what you&rsquo;re trying to do right now.</p>
      </div>
      <div class="bc-docs-grid">
        <a class="bc-doc-card" href="getting-started/">
          <span class="bc-doc-kicker">Start here</span>
          <h3>Getting started</h3>
          <p>Install, connect your client, and run a first session end to end.</p>
          <span class="bc-doc-arrow" aria-hidden="true">&rarr;</span>
        </a>
        <a class="bc-doc-card" href="tools/">
          <span class="bc-doc-kicker">Reference</span>
          <h3>Tool reference</h3>
          <p>All 39 MCP tools with parameters and return shapes, by category.</p>
          <span class="bc-doc-arrow" aria-hidden="true">&rarr;</span>
        </a>
        <a class="bc-doc-card" href="guides/">
          <span class="bc-doc-kicker">Recipes</span>
          <h3>Guides</h3>
          <p>Research, debugging, form filling, multi-tab work, recorded test runs.</p>
          <span class="bc-doc-arrow" aria-hidden="true">&rarr;</span>
        </a>
        <a class="bc-doc-card" href="concepts/">
          <span class="bc-doc-kicker">Under the hood</span>
          <h3>Concepts</h3>
          <p>How marks are collected, why IDs are ephemeral, and the architecture.</p>
          <span class="bc-doc-arrow" aria-hidden="true">&rarr;</span>
        </a>
      </div>
    </div>
  </section>
  <!-- ===================================================================
       CLOSING CTA
       =================================================================== -->
  <section class="bc-cta">
    <div class="bc-wrap bc-cta-inner">
      <img class="bc-cta-art" src="assets/mascot.png" alt="" width="512" height="512" loading="lazy" aria-hidden="true">
      <div class="bc-cta-copy">
        <h2>Give your agent a browser that actually sees.</h2>
        <p>One install, no cloud, no key. The shortest path from &ldquo;ask the model&rdquo; to watching the browser do the thing.</p>
      </div>
      <div class="bc-cta-row">
        <a class="bc-btn bc-btn--primary" href="getting-started/installation/">
          Install BrowserControl
          <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 8h11M9 3.5 13.5 8 9 12.5"/></svg>
        </a>
        <a class="bc-btn bc-btn--ghost" href="https://github.com/adityasasidhar/browsercontrol" rel="noopener">
          <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/></svg>
          Star on GitHub
        </a>
      </div>
    </div>
  </section>
</div>
