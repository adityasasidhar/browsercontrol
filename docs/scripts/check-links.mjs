// Check every internal link and #anchor in the built site.
// VitePress catches dead pages at build time, but not dead anchors.
import { readFileSync, readdirSync, existsSync } from 'node:fs'
import { join, relative } from 'node:path'

const DIST = new URL('../.vitepress/dist/', import.meta.url).pathname
const BASE = '/browsercontrol/'

const files = []
const walk = (dir) => {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name)
    if (entry.isDirectory()) walk(path)
    else if (entry.name.endsWith('.html')) files.push(path)
  }
}
walk(DIST)

const ids = new Map()
const idsOf = (file) => {
  if (!ids.has(file)) {
    const html = readFileSync(file, 'utf-8')
    ids.set(file, new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])))
  }
  return ids.get(file)
}

const resolvePage = (path) => {
  const clean = decodeURIComponent(path.slice(BASE.length)).replace(/\/$/, '/index')
  for (const candidate of [clean, `${clean}.html`, `${clean}/index.html`]) {
    const file = join(DIST, candidate)
    if (existsSync(file) && !file.endsWith('/')) return file
  }
  return null
}

const problems = []
for (const file of files) {
  const html = readFileSync(file, 'utf-8')
  const page = '/' + relative(DIST, file)
  for (const [, href] of html.matchAll(/<a [^>]*href="([^"]+)"/g)) {
    if (/^(https?:|mailto:|javascript:)/.test(href)) continue
    let [path, hash] = href.split('#')
    let target = file
    if (path) {
      if (!path.startsWith(BASE)) continue
      if (/\.(txt|json|md|png|svg|webp|xml)$/.test(path)) {
        if (!existsSync(join(DIST, path.slice(BASE.length)))) problems.push(`${page}: missing file ${href}`)
        continue
      }
      target = resolvePage(path)
      if (!target) {
        problems.push(`${page}: dead link ${href}`)
        continue
      }
    }
    if (hash && !idsOf(target).has(decodeURIComponent(hash))) {
      problems.push(`${page}: missing anchor ${href}`)
    }
  }
}

if (problems.length) {
  console.error([...new Set(problems)].join('\n'))
  console.error(`\n${new Set(problems).size} broken link(s)`)
  process.exit(1)
}
console.log(`Checked ${files.length} pages: all internal links and anchors resolve.`)
