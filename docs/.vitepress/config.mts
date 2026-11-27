import { readFileSync } from 'node:fs'
import { defineConfig, type DefaultTheme } from 'vitepress'
import llmstxt, { copyOrDownloadAsMarkdownButtons } from 'vitepress-plugin-llms'
import { groupIconMdPlugin, groupIconVitePlugin } from 'vitepress-plugin-group-icons'

const SITE = 'https://adityasasidhar.github.io'
const BASE = '/browsercontrol/'
const REPO = 'https://github.com/adityasasidhar/browsercontrol'
// Read from pyproject.toml so the header can't drift from the released version.
const pyproject = readFileSync(new URL('../../pyproject.toml', import.meta.url), 'utf8')
const VERSION = pyproject.match(/^version\s*=\s*"([^"]+)"/m)?.[1]
if (!VERSION) throw new Error('docs config: could not read version from pyproject.toml')

const description =
  'A local MCP server that gives AI agents a real Chromium browser. Every action returns a screenshot with numbered boxes on what can be clicked, so agents act with click(7) instead of guessing selectors.'

const reference: DefaultTheme.SidebarItem[] = [
  { text: 'All tools', link: '/reference/' },
  { text: 'Navigation', link: '/reference/navigation' },
  { text: 'Interaction', link: '/reference/interaction' },
  { text: 'Waiting & dialogs', link: '/reference/waiting' },
  { text: 'Assertions', link: '/reference/assertions' },
  { text: 'Forms', link: '/reference/forms' },
  { text: 'Content', link: '/reference/content' },
  { text: 'Extraction', link: '/reference/extraction' },
  { text: 'Tabs', link: '/reference/tabs' },
  { text: 'Sessions', link: '/reference/sessions' },
  { text: 'DevTools', link: '/reference/devtools' },
  { text: 'Network', link: '/reference/network' },
  { text: 'Emulation', link: '/reference/emulation' },
  { text: 'Recording', link: '/reference/recording' },
  { text: 'MCP resources', link: '/reference/resources' },
  { text: 'Configuration', link: '/reference/configuration' },
]

const sidebar: DefaultTheme.Sidebar = [
  {
    text: 'Get started',
    items: [
      { text: 'Introduction', link: '/guide/' },
      { text: 'Quickstart', link: '/guide/quickstart' },
      { text: 'Installation', link: '/guide/installation' },
      { text: 'Connect a client', link: '/guide/clients' },
      { text: 'Your first session', link: '/guide/first-session' },
      { text: 'Agent skill', link: '/guide/agent-skill' },
      { text: 'Share over HTTP', link: '/guide/http' },
    ],
  },
  {
    text: 'Concepts',
    collapsed: false,
    items: [
      { text: 'How it works', link: '/concepts/how-it-works' },
      { text: 'Set of Marks', link: '/concepts/set-of-marks' },
      { text: 'Settling', link: '/concepts/settling' },
      { text: 'Sessions & profiles', link: '/concepts/sessions' },
      { text: 'How it compares', link: '/concepts/comparison' },
    ],
  },
  {
    text: 'Recipes',
    collapsed: false,
    items: [
      { text: 'Overview', link: '/recipes/' },
      { text: 'Research a question', link: '/recipes/research' },
      { text: 'Fill a form', link: '/recipes/fill-a-form' },
      { text: 'Upload a file', link: '/recipes/upload-a-file' },
      { text: 'Extract data', link: '/recipes/extract-data' },
      { text: 'Work across tabs', link: '/recipes/tabs' },
      { text: 'Debug a web app', link: '/recipes/debug' },
      { text: 'Test edge states', link: '/recipes/edge-states' },
      { text: 'Mobile & dark mode', link: '/recipes/responsive' },
      { text: 'Use your own Chrome', link: '/recipes/your-chrome' },
      { text: 'Record & export tests', link: '/recipes/record-tests' },
    ],
  },
  { text: 'Reference', collapsed: false, items: reference },
  {
    text: 'Help',
    collapsed: false,
    items: [
      { text: 'Troubleshooting', link: '/help/troubleshooting' },
      { text: 'FAQ', link: '/help/faq' },
    ],
  },
  {
    text: 'Project',
    collapsed: true,
    items: [
      { text: 'Contributing', link: '/project/contributing' },
      { text: 'Changelog', link: '/project/changelog' },
      { text: 'About', link: '/project/about' },
    ],
  },
]

export default defineConfig({
  title: 'BrowserControl',
  titleTemplate: ':title · BrowserControl',
  description,
  lang: 'en-US',
  base: BASE,
  cleanUrls: true,
  lastUpdated: true,
  srcExclude: ['superpowers/**', 'README.md'],
  sitemap: { hostname: `${SITE}${BASE}` },

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: `${BASE}images/favicon.svg` }],
    ['meta', { name: 'theme-color', content: '#1e1e2e' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:site_name', content: 'BrowserControl' }],
    ['meta', { property: 'og:image', content: `${SITE}${BASE}og-card.png` }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:image', content: `${SITE}${BASE}og-card.png` }],
    ['link', { rel: 'alternate', type: 'text/plain', title: 'llms.txt', href: `${BASE}llms.txt` }],
  ],

  transformPageData(pageData) {
    const canonical = `${SITE}${BASE}${pageData.relativePath}`
      .replace(/index\.md$/, '')
      .replace(/\.md$/, '')
    pageData.frontmatter.head ??= []
    pageData.frontmatter.head.push(
      ['link', { rel: 'canonical', href: canonical }],
      ['meta', { property: 'og:url', content: canonical }],
      ['meta', { property: 'og:title', content: pageData.title || 'BrowserControl' }],
      [
        'meta',
        { property: 'og:description', content: pageData.description || description },
      ],
    )
  },

  markdown: {
    theme: { light: 'catppuccin-latte', dark: 'catppuccin-mocha' },
    image: { lazyLoading: true },
    config(md) {
      md.use(groupIconMdPlugin)
      md.use(copyOrDownloadAsMarkdownButtons)
    },
  },

  vite: {
    plugins: [
      groupIconVitePlugin({
        customIcon: {
          'claude code': 'logos:claude-icon',
          cursor: 'vscode-icons:file-type-cursorrules',
          'vs code': 'logos:visual-studio-code',
          uv: 'vscode-icons:file-type-uv',
          pip: 'vscode-icons:file-type-pip',
        },
      }),
      llmstxt({
        domain: SITE,
        title: 'BrowserControl',
        description:
          'A local MCP server for browser automation. BrowserControl marks interactive elements in Chromium screenshots with numbered boxes, and agents refer to those numbers in tool calls such as `click(7)`.',
        details: [
          'Python 3.11.5+, built on FastMCP and Playwright. MIT licensed. 79 MCP tools; a machine-readable catalog of every tool with its parameters is at ' +
            `${SITE}${BASE}tools.json.`,
          '',
          'Two rules govern correct use:',
          '',
          '- **Element IDs are ephemeral.** The element map is rebuilt after every action and screenshot. An ID is valid only against the most recent screenshot; never plan two actions from one screenshot. Use `act` to batch steps against one map.',
          '- **Only what is visible in the viewport is numbered.** A missing number usually means "scroll" or "covered by an overlay", not "absent". `find(query)` searches the whole page, including off-screen content, iframes, and shadow DOM.',
          '',
          `If you are an agent driving BrowserControl, read the agent skill first: ${REPO}/blob/main/skills/browsercontrol/SKILL.md`,
        ].join('\n'),
      }),
    ],
  },

  themeConfig: {
    logo: { src: '/logo-mascot.png', alt: '' },
    siteTitle: 'BrowserControl',
    nav: [
      { text: 'Guide', link: '/guide/', activeMatch: '^/guide/' },
      { text: 'Concepts', link: '/concepts/how-it-works', activeMatch: '^/concepts/' },
      { text: 'Recipes', link: '/recipes/', activeMatch: '^/recipes/' },
      { text: 'Reference', link: '/reference/', activeMatch: '^/reference/' },
      {
        text: `v${VERSION}`,
        items: [
          { text: 'Changelog', link: '/project/changelog' },
          { text: 'Contributing', link: '/project/contributing' },
          { text: 'PyPI', link: 'https://pypi.org/project/browsercontrol/' },
          { text: 'Releases', link: `${REPO}/releases` },
        ],
      },
    ],
    sidebar: {
      '/guide/': sidebar,
      '/concepts/': sidebar,
      '/recipes/': sidebar,
      '/reference/': sidebar,
      '/help/': sidebar,
      '/project/': sidebar,
    },
    outline: { level: [2, 3], label: 'On this page' },
    socialLinks: [{ icon: 'github', link: REPO, ariaLabel: 'BrowserControl on GitHub' }],
    editLink: { pattern: `${REPO}/edit/main/docs/:path`, text: 'Edit this page on GitHub' },
    lastUpdated: { text: 'Updated', formatOptions: { dateStyle: 'medium' } },
    search: {
      provider: 'local',
      options: {
        detailedView: true,
        miniSearch: { searchOptions: { fuzzy: 0.2, prefix: true, boost: { title: 4, text: 2 } } },
      },
    },
    footer: {
      message: 'Released under the MIT License.',
      copyright: `BrowserControl · <a href="${BASE}llms.txt">llms.txt</a> · <a href="${BASE}llms-full.txt">llms-full.txt</a> · <a href="${BASE}tools.json">tools.json</a>`,
    },
    externalLinkIcon: true,
    notFound: {
      code: '404',
      title: 'Element 404 not found',
      quote:
        "This page is stale: it moved, or it never existed. Here's a fresh map to pick from.",
      linkLabel: 'Go to the home page',
      linkText: 'Back to the docs',
    },
    docFooter: { prev: 'Previous', next: 'Next' },
    darkModeSwitchLabel: 'Theme',
    returnToTopLabel: 'Back to top',
    llms: {
      copyText: 'Copy page',
      copiedText: 'Copied',
      viewMarkdownText: 'View as Markdown',
      openInAIText: 'Open in {provider}',
    },
  } as DefaultTheme.Config & { llms: Record<string, string> },
})
