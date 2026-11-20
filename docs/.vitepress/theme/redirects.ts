/**
 * Addresses from the old MkDocs site, mapped to their new pages. GitHub Pages
 * serves 404.html for any unknown path, and the layout forwards these.
 */
export const redirects: Record<string, string> = {
  'getting-started': '/guide/',
  'getting-started/installation': '/guide/installation',
  'getting-started/connect-your-ai': '/guide/clients',
  'getting-started/first-session': '/guide/first-session',
  'getting-started/agent-skill': '/guide/agent-skill',
  tools: '/reference/',
  'tools/navigation': '/reference/navigation',
  'tools/interaction': '/reference/interaction',
  'tools/tabs': '/reference/tabs',
  'tools/forms': '/reference/forms',
  'tools/content': '/reference/content',
  'tools/devtools': '/reference/devtools',
  'tools/recording': '/reference/recording',
  'tools/waiting': '/reference/waiting',
  'tools/extraction': '/reference/extraction',
  'tools/network': '/reference/network',
  'tools/emulation': '/reference/emulation',
  'tools/sessions': '/reference/sessions',
  guides: '/recipes/',
  'guides/web-research': '/recipes/research',
  'guides/debug-web-app': '/recipes/debug',
  'guides/record-tests': '/recipes/record-tests',
  'guides/fill-forms': '/recipes/fill-a-form',
  'guides/multi-tab': '/recipes/tabs',
  'guides/mobile-responsive': '/recipes/responsive',
  'guides/upload-files': '/recipes/upload-a-file',
  'guides/use-your-chrome': '/recipes/your-chrome',
  'guides/mock-apis': '/recipes/edge-states',
  concepts: '/concepts/how-it-works',
  'concepts/architecture': '/concepts/how-it-works',
  configuration: '/reference/configuration',
  troubleshooting: '/help/troubleshooting',
  development: '/project/contributing',
  about: '/project/about',
  'about/changelog': '/project/changelog',
  'about/license': '/project/about',
}

/** The new path for an old address, or null. `path` excludes the site base. */
export function redirectFor(path: string): string | null {
  const key = path.replace(/^\/+|\/+$/g, '').replace(/(\/index)?\.html$/, '')
  if (key in redirects) return redirects[key]
  // Same page name, old trailing-slash form: /concepts/set-of-marks/ -> /concepts/set-of-marks
  if (path.endsWith('/') && key) return `/${key}`
  return null
}
