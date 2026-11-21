import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import { useRoute } from 'vitepress'
import { nextTick, onMounted, watch } from 'vue'
import mediumZoom from 'medium-zoom'
import CopyOrDownloadAsMarkdownButtons from 'vitepress-plugin-llms/vitepress-components/CopyOrDownloadAsMarkdownButtons.vue'

import '@catppuccin/vitepress/theme/mocha/red.css'
import '@fontsource-variable/geist'
import '@fontsource-variable/geist-mono'
import 'virtual:group-icons.css'
import './style/vars.css'
import './style/base.css'
import './style/docs.css'

import Layout from './Layout.vue'
import HomePage from './components/home/HomePage.vue'
import InstallBox from './components/InstallBox.vue'
import ToolExplorer from './components/ToolExplorer.vue'
import Mark from './components/Mark.vue'
import CardGrid from './components/CardGrid.vue'
import Card from './components/Card.vue'
import { reveal } from './reveal'

export default {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }) {
    app.component('CopyOrDownloadAsMarkdownButtons', CopyOrDownloadAsMarkdownButtons)
    app.component('HomePage', HomePage)
    app.component('InstallBox', InstallBox)
    app.component('ToolExplorer', ToolExplorer)
    app.component('Mark', Mark)
    app.component('CardGrid', CardGrid)
    app.component('Card', Card)
    app.directive('reveal', reveal)
  },
  setup() {
    const route = useRoute()
    const zoom = () => {
      mediumZoom('.vp-doc img:not(.no-zoom)', { background: 'var(--vp-c-bg)', margin: 24 })
    }
    onMounted(zoom)
    watch(
      () => route.path,
      () => nextTick(zoom),
    )
  },
} satisfies Theme
