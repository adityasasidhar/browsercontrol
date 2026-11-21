---
title: Your first session
description: Fill in a public demo form with your agent and learn to read the element map as you go.
---

# Your first session

This walkthrough uses Selenium's public demo form, so nothing you type goes anywhere that matters. It takes two prompts and shows the habit every good BrowserControl session depends on: read the newest numbers before acting.

<div class="steps">

### Open the form

Ask your agent:

> Open https://www.selenium.dev/selenium/web/web-form.html with BrowserControl. Tell me the numbers of the text input and the Submit button.

The agent calls `navigate_to`, and BrowserControl answers with this:

<figure>

![The demo form with numbered boxes: the text input is 3 and Submit is 2](/images/annotated-web-form.webp)

<figcaption>Your numbers may differ. Always read them from your own session.</figcaption>
</figure>

Here the text input is <Mark n="3">Text input</Mark> and the button is <Mark n="2">Submit</Mark>. The disabled field is drawn grey and listed as `(disabled)`.

### Fill and submit

Ask:

> Type "BrowserControl demo" into the text input, then submit the form and confirm the next page says "Form submitted".

The agent works in three moves:

1. `type_text(3, "BrowserControl demo")`. The response is a **new** screenshot and map.
2. It finds Submit again **in that new map** and calls `click` with its current number.
3. It checks the result in the returned screenshot, or reads the page with `get_page_content()`.

</div>

::: tip Why look up Submit again?
Typing doesn't visibly change the form, but it does produce a new screenshot, and numbering is rebuilt from scratch every time. Here Submit probably kept number 2. On a page that shifts, it wouldn't. Reading the latest map costs nothing, while acting on an old number gets a [stale element](/concepts/set-of-marks#stale-ids) error at best.
:::

## Do it in one call

Once the agent knows the numbers, it can batch the steps with [`act`](/reference/interaction#act):

```text
→ act([{"action": "type", "element_id": 3, "text": "BrowserControl demo"},
       {"action": "click", "element_id": 2}])
Ran 2 of 2 step(s), 0 failed:
  1. ok: typed 'BrowserControl demo' into [3]
  2. ok: clicked [2]
```

Every ID in an `act` call refers to the screenshot taken before the call, so batching is safe as long as the steps don't navigate away halfway through.

## Try next

<CardGrid>
  <Card title="Fill a form" link="/recipes/fill-a-form">Dropdowns, checkboxes, and custom widgets.</Card>
  <Card title="Debug a web app" link="/recipes/debug">Console, network, and page errors.</Card>
  <Card title="Record & export tests" link="/recipes/record-tests">Turn a session into a Playwright test.</Card>
</CardGrid>
