---
title: Recipes
description: Task-by-task walkthroughs for common BrowserControl jobs, from research and forms to debugging, testing, and test export.
---

# Recipes

Each recipe starts with a prompt you could give your agent, shows the tool calls it leads to, and explains the choices along the way.

## Do things on the web

<CardGrid>
  <Card icon="01" title="Research a question" link="/recipes/research">Search a site, open results, and answer with sources.</Card>
  <Card icon="02" title="Fill a form" link="/recipes/fill-a-form">Text, dropdowns, checkboxes, custom widgets, and submit.</Card>
  <Card icon="03" title="Upload a file" link="/recipes/upload-a-file">Attach local files without a native file picker.</Card>
  <Card icon="04" title="Extract data" link="/recipes/extract-data">Tables, links, and fields as JSON.</Card>
  <Card icon="05" title="Work across tabs" link="/recipes/tabs">Open, compare, and switch between pages.</Card>
  <Card icon="06" title="Use your own Chrome" link="/recipes/your-chrome">Work in sites you're already signed in to.</Card>
</CardGrid>

## Build and test web apps

<CardGrid>
  <Card icon="07" title="Debug a web app" link="/recipes/debug">Console, errors, and network, step by step.</Card>
  <Card icon="08" title="Test edge states" link="/recipes/edge-states">Mock failures, empty data, slow networks.</Card>
  <Card icon="09" title="Mobile & dark mode" link="/recipes/responsive">Check layouts on devices, themes, and locales.</Card>
  <Card icon="10" title="Record & export tests" link="/recipes/record-tests">Traces for bug reports, Playwright tests for CI.</Card>
</CardGrid>

::: tip Reading the transcripts
Lines starting with `→` are tool calls the agent makes. Numbers like `click(5)` stand for whatever number that element has in *your* latest screenshot; read yours rather than copying ours.
:::
