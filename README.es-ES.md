<p align="center">
  <a href="https://github.com/adityasasidhar/browsercontrol">
    <img loading="lazy" alt="BrowserControl" src="https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/assets/logo-main.png" width="140"/>
  </a>
</p>

# BrowserControl

[![Docs](https://img.shields.io/badge/docs-live-brightgreen)][docs]
[![PyPI version](https://img.shields.io/pypi/v/browsercontrol)](https://pypi.org/project/browsercontrol/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/browsercontrol)](https://pypi.org/project/browsercontrol/)
[![CI](https://github.com/adityasasidhar/browsercontrol/actions/workflows/ci.yml/badge.svg)](https://github.com/adityasasidhar/browsercontrol/actions/workflows/ci.yml)
[![MCP](https://img.shields.io/badge/MCP-server-6A5ACD)](https://modelcontextprotocol.io)
[![Playwright](https://img.shields.io/badge/Playwright-Chromium-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev/python/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://img.shields.io/badge/mypy-strict-blue)](https://mypy-lang.org/)
[![License MIT](https://img.shields.io/github/license/adityasasidhar/browsercontrol)](LICENSE)
[![PyPI Downloads](https://static.pepy.tech/badge/browsercontrol/month)](https://pepy.tech/projects/browsercontrol)

[English](README.md)

## ¿Qué es BrowserControl?

BrowserControl le da a tu cliente de IA un navegador Chromium local a través del
[Model Context Protocol](https://modelcontextprotocol.io). Cada acción devuelve
una captura de pantalla con cajas numeradas sobre los controles de la página,
junto con la misma lista en texto, para que el agente actúe por número
(`click(5)`) en lugar de adivinar selectores CSS.

<p align="center">
  <img loading="lazy" alt="Sesión grabada de BrowserControl que muestra los elementos numerados mientras el agente navega, busca y llena un formulario" src="https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/assets/som-demo.gif" width="100%"/>
</p>

## Funciones

- 🎯 Control centrado en la visión con [Set of Marks][som]: elementos numerados en cada captura, incluidos iframes y shadow DOM
- 🧭 [Navegar e interactuar][interaction]: clic, doble clic, arrastrar, escribir y `find("texto")` en cualquier parte de la página
- ⚡ Ejecuta varios pasos en una sola llamada con `act(steps)` y recibe una única captura
- 🔐 [Usa tu propio navegador][sessions]: conéctate a tu Chrome abierto y a los sitios donde ya iniciaste sesión, o abre sesiones aisladas
- 📝 [Llenar formularios][forms]: selecciona opciones, marca casillas y sube archivos locales
- 📖 [Lee páginas][content] como Markdown o texto y [extrae datos][extraction] como tablas, enlaces o campos JSON
- 🌐 [Prueba condiciones reales][network]: simula o bloquea peticiones, limita la red y emula dispositivos, ubicaciones, zonas horarias y modo oscuro
- 🐞 [Depura una aplicación web][debug]: registros de consola, cabeceras y cuerpos de peticiones, errores de página y exportación HAR
- 🎬 [Graba una sesión][recording]: trazas de Playwright, instantáneas y exportación a una prueba de Playwright ejecutable
- 🔌 Funciona con Claude Code, Cursor, VS Code y cualquier cliente MCP, por stdio o Streamable HTTP
- 🔒 Se ejecuta en local con un perfil persistente, así que los inicios de sesión sobreviven a los reinicios

### Novedades

- 🔗 Conéctate a tu propio Chrome por CDP con `connect_to_chrome`; desconectarse nunca lo cierra
- 🧪 `export_test` convierte una sesión del agente en un archivo de pytest-playwright o `@playwright/test`
- 💬 Los diálogos JS y las descargas se gestionan automáticamente y se informan en la siguiente respuesta
- ⏳ Espera inteligente tras cada acción: carga, red en calma y luego DOM en calma
- 👥 Sesiones aisladas por cliente con `--isolate-clients`

Consulta el [registro de cambios](CHANGELOG.md) para ver la lista completa.

## Inicio rápido

### 1. Instalar

Necesitas [uv](https://docs.astral.sh/uv/getting-started/installation/) en tu
`PATH`. En **Claude Code**, instala el servidor MCP y la
[habilidad para agentes](skills/browsercontrol/SKILL.md) juntos como plugin:

```text
/plugin marketplace add adityasasidhar/browsercontrol
/plugin install browsercontrol@browsercontrol
```

Después reinicia Claude Code o ejecuta `/reload-plugins`.

En **VS Code** o **Cursor**, instálalo con un clic:

<p>
  <a href="https://insiders.vscode.dev/redirect/mcp/install?name=browsercontrol&amp;config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22browsercontrol%22%5D%7D"><img src="https://img.shields.io/badge/VS_Code-Install_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white" alt="Install in VS Code"></a>
  <a href="https://insiders.vscode.dev/redirect/mcp/install?name=browsercontrol&amp;config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22browsercontrol%22%5D%7D&amp;quality=insiders"><img src="https://img.shields.io/badge/VS_Code_Insiders-Install_Server-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white" alt="Install in VS Code Insiders"></a>
  <a href="https://cursor.com/en/install-mcp?name=browsercontrol&amp;config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJicm93c2VyY29udHJvbCJdfQ%3D%3D"><img src="https://img.shields.io/badge/Cursor-Install_Server-000000?style=flat-square&logo=cursor&logoColor=white" alt="Install in Cursor"></a>
</p>

Para **cualquier otro cliente MCP**, ejecuta `uvx browsercontrol`. Los clientes
que usan JSON con `mcpServers` pueden añadir esta entrada:

```json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "uvx",
      "args": ["browsercontrol"]
    }
  }
}
```

O añádelo a Claude Code a mano:

```bash
claude mcp add --transport stdio browsercontrol -- uvx browsercontrol
```

Funciona en Linux, macOS y Windows con Python 3.11+. En el primer arranque,
BrowserControl reutiliza un navegador local compatible o descarga Chromium.

Encontrarás más [configuración de clientes][connect] (Cursor, VS Code y otros) y
[opciones de instalación][installation] (pip, desde el código fuente) en la
documentación.

### 2. Pídeselo a tu agente

Recarga tu cliente y prueba:

> Abre Hacker News con BrowserControl y dime la noticia principal.

### 3. Compartir un navegador (opcional)

Sirve por Streamable HTTP para que varios clientes usen el mismo navegador:

```bash
uvx browsercontrol --transport http                     # http://127.0.0.1:8000/mcp
uvx browsercontrol --transport http --isolate-clients   # una sesión por cliente
```

## Cómo funcionan los números de los elementos

Si un botón está marcado con el **5**, el agente llama a `click(5)`. Cada
captura anotada genera un mapa nuevo, así que **lee el mapa más reciente antes
de cada acción que use un ID**. Si un control está fuera de la pantalla,
desplázate hasta él o deja que `find("su texto")` busque en toda la página y se
desplace hasta allí.

Más información en [Set of Marks][som].

## Documentación

Consulta la [documentación][docs] de BrowserControl para la instalación, los
conceptos, la [referencia completa de herramientas][tools], la
[configuración][configuration] y la [solución de problemas][troubleshooting].

Los agentes también pueden leer la documentación: [`llms.txt`][llms] indexa todas
las páginas, [`llms-full.txt`][llms-full] la reúne en un solo archivo y
[`tools.json`][tools-json] lista cada herramienta con sus parámetros.

## Recetas

Ponte manos a la obra con las [recetas][guides]: [investigación web][guide-research],
[llenar formularios][guide-forms], [subir archivos][guide-upload],
[flujos con varias pestañas][guide-tabs],
[pruebas móviles y responsivas][guide-mobile],
[depurar una aplicación web][debug] y [grabar pruebas][guide-record].

## Ayuda y soporte

¿Encontraste un error o tienes una idea? Abre un
[issue](https://github.com/adityasasidhar/browsercontrol/issues).

## Contribuir

```bash
uv sync
uv run playwright install chromium
uv run pytest
cd docs && npm install && npm run dev
```

Lee la [guía de desarrollo][development] y las
[pautas de contribución](CONTRIBUTING.md) para más detalles.

## Licencia

BrowserControl se publica bajo la [licencia MIT](LICENSE).

[docs]: https://adityasasidhar.github.io/browsercontrol/
[som]: https://adityasasidhar.github.io/browsercontrol/concepts/set-of-marks
[interaction]: https://adityasasidhar.github.io/browsercontrol/reference/interaction
[sessions]: https://adityasasidhar.github.io/browsercontrol/recipes/your-chrome
[forms]: https://adityasasidhar.github.io/browsercontrol/recipes/fill-a-form
[content]: https://adityasasidhar.github.io/browsercontrol/reference/content
[extraction]: https://adityasasidhar.github.io/browsercontrol/recipes/extract-data
[network]: https://adityasasidhar.github.io/browsercontrol/recipes/edge-states
[recording]: https://adityasasidhar.github.io/browsercontrol/recipes/record-tests
[debug]: https://adityasasidhar.github.io/browsercontrol/recipes/debug
[tools]: https://adityasasidhar.github.io/browsercontrol/reference/
[configuration]: https://adityasasidhar.github.io/browsercontrol/reference/configuration
[troubleshooting]: https://adityasasidhar.github.io/browsercontrol/help/troubleshooting
[connect]: https://adityasasidhar.github.io/browsercontrol/guide/clients
[installation]: https://adityasasidhar.github.io/browsercontrol/guide/installation
[development]: https://adityasasidhar.github.io/browsercontrol/project/contributing
[guides]: https://adityasasidhar.github.io/browsercontrol/recipes/
[llms]: https://adityasasidhar.github.io/browsercontrol/llms.txt
[llms-full]: https://adityasasidhar.github.io/browsercontrol/llms-full.txt
[tools-json]: https://adityasasidhar.github.io/browsercontrol/tools.json
[guide-research]: https://adityasasidhar.github.io/browsercontrol/recipes/research
[guide-forms]: https://adityasasidhar.github.io/browsercontrol/recipes/fill-a-form
[guide-upload]: https://adityasasidhar.github.io/browsercontrol/recipes/upload-a-file
[guide-tabs]: https://adityasasidhar.github.io/browsercontrol/recipes/tabs
[guide-mobile]: https://adityasasidhar.github.io/browsercontrol/recipes/responsive
[guide-record]: https://adityasasidhar.github.io/browsercontrol/recipes/record-tests
