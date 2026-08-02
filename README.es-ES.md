

<p align="center">
  <img src="https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/assets/logo-main.png" alt="" width="130">
</p>

<h1 align="center">BrowserControl</h1>

<p align="center"><b>Un servidor MCP que le proporciona a tu agente un navegador que puede ver.</b></p>

<p align="center">
  <a href="https://pypi.org/project/browsercontrol/"><img src="https://img.shields.io/pypi/v/browsercontrol?color=1f6feb&label=pypi" alt="PyPI"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11+-3776ab.svg" alt="Python 3.11+"></a>
  <a href="https://github.com/adityasasidhar/browsercontrol/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/adityasasidhar/browsercontrol/ci.yml?branch=main&label=ci" alt="CI"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-3fb950.svg" alt="MIT"></a>
  <a href="https://adityasasidhar.github.io/browsercontrol/"><img src="https://img.shields.io/badge/docs-live-8957e5.svg" alt="Documentation"></a>
</p>

<p align="center">
  <a href="https://insiders.vscode.dev/redirect/mcp/install?name=browsercontrol&amp;config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22browsercontrol%22%5D%7D"><img src="https://img.shields.io/badge/VS_Code-Install_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white" alt="Install in VS Code"></a>
  <a href="https://insiders.vscode.dev/redirect/mcp/install?name=browsercontrol&amp;config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22browsercontrol%22%5D%7D&amp;quality=insiders"><img src="https://img.shields.io/badge/VS_Code_Insiders-Install_Server-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white" alt="Install in VS Code Insiders"></a>
  <a href="https://cursor.com/en/install-mcp?name=browsercontrol&amp;config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJicm93c2VyY29udHJvbCJdfQ%3D%3D"><img src="https://img.shields.io/badge/Cursor-Install_Server-000000?style=flat-square&logo=cursor&logoColor=white" alt="Install in Cursor"></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/assets/som-demo.gif" alt="Doce acciones consecutivas de BrowserControl en tres sitios: navegación, desplazamiento, escritura en un campo de búsqueda, seguimiento de un resultado y luego llenado de un formulario — escritura en un campo de texto y un textarea, selección de una opción desplegable, marcación de una casilla y envío. La página está marcada con cajas rojas numeradas y se remarca después de cada acción." width="880">
</p>

<p align="center"><sub>Una sesión real, doce acciones, nada coreografiado: navegar, desplazarse, escribir, seleccionar, marcar, hacer clic. Observa los números: se reconstruyen desde cero después de <em>cada</em> acción, por eso el agente los vuelve a leer cada vez.</sub></p>

## La idea

La mayoría de las herramientas para navegadores le entregan un árbol DOM a un modelo y esperan que escriba un selector funcional.
BrowserControl le entrega una **imagen**.

Cada acción devuelve una captura de pantalla nueva con cajas rojas numeradas dibujadas sobre los elementos interactivos, además de la misma lista en formato de texto. El agente actúa por número:

```text
click(5)
type_text(3, "hello world")
upload_file(7, "/path/to/resume.pdf")
```

Sin selectores que adivinar, ninguno que se rompa en el próximo rediseño. Este es el patrón [Set of Marks](https://adityasasidhar.github.io/browsercontrol/concepts/set-of-marks/), utilizado como interfaz principal en lugar de un recurso secundario.

## Inicio rápido

```bash
uv add browsercontrol      # o: pip install browsercontrol
```

Chromium se instala automáticamente en la primera ejecución. Si falla, ejecuta
`python -m playwright install chromium` una vez.

Apunta tu cliente al comando `browsercontrol`:

```json
{
  "mcpServers": {
    "browsercontrol": {
      "command": "browsercontrol"
    }
  }
}
```

<details>
<summary>Ubicación del archivo según el cliente</summary>

| Cliente | Ubicación |
|---|---|
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) · `~/.config/Claude/claude_desktop_config.json` (Linux) · `%APPDATA%\Claude\claude_desktop_config.json` (Windows) |
| **Claude Code** | `claude mcp add browsercontrol -- browsercontrol` |
| **Cursor** | Settings → Model Context Protocol |
| **Cline** | Settings → MCP Servers |
| **Continue.dev** | `~/.continue/config.json`, bajo `mcpServers` |
| **Zed** | `~/.config/zed/settings.json`, bajo `context_servers` como `{"command": {"path": "browsercontrol"}}` |

Sin instalación alguna, si lo prefieres: `"command": "uvx", "args": ["browsercontrol"]`.

</details>

Reinicia el cliente y pídele algo:

> *"Abre Hacker News y dime la noticia principal."*

Guía completa: [Introducción](https://adityasasidhar.github.io/browsercontrol/getting-started/).

## La única regla

**Los números de los elementos caducan después de cada acción.** El mapa se reconstruye desde cero en cada clic, escritura, desplazamiento, navegación y captura de pantalla: el elemento `7` antes de un clic rara vez será el elemento `7` después.

Por lo tanto, un agente nunca debería planificar dos clics a partir de una sola captura. Actúa, lee la nueva captura, vuelve a encontrar el objetivo y luego actúa nuevamente. Casi todos los fallos que valen la pena depurar se remontan a esto.

Dos corolarios:

- **Solo lo que está en el viewport se marca.** La ausencia de un número suele significar "más abajo" — desplázate y vuelve a mirar.
- **Los iframes de origen cruzado nunca se marcan.** Las raíces de sombra abiertas y los frames del mismo origen se recorren y numeran; los campos de pago de terceros y los widgets embebidos no pueden. Es un límite del navegador, no un error.

## Herramientas

39 herramientas en siete categorías. Todo lo que interactúa con la página devuelve una captura de pantalla anotada junto con el mapa de elementos.

| Categoría | | Herramientas |
|---|:-:|---|
| [**Navegación**](https://adityasasidhar.github.io/browsercontrol/tools/navigation/) | 5 | `navigate_to` `go_back` `go_forward` `refresh_page` `scroll` |
| [**Interacción**](https://adityasasidhar.github.io/browsercontrol/tools/interaction/) | 7 | `click` `click_at` `type_text` `press_key` `hover` `scroll_to_element` `wait` |
| [**Formularios**](https://adityasasidhar.github.io/browsercontrol/tools/forms/) | 3 | `select_option` `check_checkbox` `upload_file` |
| [**Contenido**](https://adityasasidhar.github.io/browsercontrol/tools/content/) | 5 | `get_page_content` `get_text` `get_page_info` `run_javascript` `screenshot` |
| [**Pestañas**](https://adityasasidhar.github.io/browsercontrol/tools/tabs/) | 4 | `create_tab` `switch_tab` `close_tab` `list_tabs` |
| [**DevTools**](https://adityasasidhar.github.io/browsercontrol/tools/devtools/) | 11 | `get_console_logs` `get_network_requests` `get_page_errors` `run_in_console` `inspect_element` `get_page_performance` `get_cookies` `set_cookie` `delete_cookie` `clear_cookies` `set_viewport` |
| [**Grabación**](https://adityasasidhar.github.io/browsercontrol/tools/recording/) | 4 | `start_recording` `stop_recording` `take_snapshot` `list_recordings` |

Algunos comportamientos que no son evidentes por los nombres:

- `type_text` usa `fill()` de Playwright: **reemplaza** el campo, no agrega texto.
- `click` resuelve el elemento más superior en el centro de la marca, por lo que un banner de cookies que cubra tu objetivo absorberá el clic. Cierra las superposiciones primero.
- `upload_file` usa `set_input_files`, que funciona en sitios donde controlar el selector de archivos no es viable.
- `screenshot(annotate=True, full_page=True)` devuelve una imagen *limpia* — las capturas de página completa no pueden marcarse.
- `get_page_content` devuelve Markdown, limitado a 30 KB.
- Las grabaciones son trazas de Playwright. Ábrelas con
  `npx playwright show-trace ~/.browsercontrol/recordings/<name>.zip`.

## Enseña a tu agente a usarlo bien

Conectar el servidor le indica a un agente *qué* herramientas existen. La [habilidad para agentes](skills/browsercontrol/SKILL.md) incluida le dice *cómo usarlas correctamente* —
que los números caducan, que un banner puede absorber un clic, que un número faltante indica que hay que desplazarse.

```bash
mkdir -p ~/.claude/skills/browsercontrol
curl -fsSL https://raw.githubusercontent.com/adityasasidhar/browsercontrol/main/skills/browsercontrol/SKILL.md \
  -o ~/.claude/skills/browsercontrol/SKILL.md
```

Se carga solo cuando una tarea involucra realmente un navegador, por lo que solo cuesta una línea de contexto el resto del tiempo. Los agentes que prefieran leer la documentación directamente pueden empezar por [`llms.txt`](https://adityasasidhar.github.io/browsercontrol/llms.txt).

## Configuración

Variables de entorno, leídas una sola vez al inicio.

| Variable | Predeterminado | |
|---|---|---|
| `BROWSER_HEADLESS` | `true` | `false` para ver trabajar al navegador |
| `BROWSER_VIEWPORT_WIDTH` | `1280` | |
| `BROWSER_VIEWPORT_HEIGHT` | `720` | |
| `BROWSER_TIMEOUT` | `30000` | Tiempo de espera de navegación, en ms |
| `BROWSER_USER_DATA_DIR` | `~/.browsercontrol/user_data` | Directorio del perfil |
| `BROWSER_EXTENSION_PATH` | — | Extensión sin empaquetar para cargar al iniciar |
| `BROWSER_EXECUTABLE_PATH` | — | Binario de Chromium para usar, cuando Playwright no incluye una versión para tu plataforma |
| `BROWSER_RECORDINGS_DIR` | junto al perfil | Dónde se guardan las trazas |
| `BROWSER_SNAPSHOTS_DIR` | junto al perfil | Dónde se guardan las instantáneas |
| `LOG_LEVEL` | `INFO` | |

```bash
BROWSER_HEADLESS=false BROWSER_VIEWPORT_WIDTH=390 BROWSER_VIEWPORT_HEIGHT=844 browsercontrol
```

## ¿Por qué esta herramienta?

La sesión es un perfil real de Chromium (`launch_persistent_context`), por lo que las cookies,
`localStorage` y los inicios de sesión sobreviven a los reinicios: inicia sesión una vez y tu agente permanecerá conectado. DevTools son de primera clase: la consola, el tiempo de red, las excepciones no capturadas, el rendimiento y los estilos calculados son herramientas, no un añadido secundario. Y
se ejecuta completamente en tu máquina: sin clave de API de LLM, sin viajes de ida y vuelta a la nube, sin
costo por acción, nada sale de tu equipo.

Posicionamiento honesto: si te conformas con controlar el árbol de accesibilidad, Playwright
MCP es excelente. Si quieres que un LLM planifique las interacciones por ti, mira
Stagehand o Browser-Use. El nicho de BrowserControl es el **control de navegador totalmente local
centrado en la visión con devtools integrados**. Comparación más detallada
[en la documentación](https://adityasasidhar.github.io/browsercontrol/concepts/comparison/).

## Desarrollo

```bash
git clone https://github.com/adityasasidhar/browsercontrol
cd browsercontrol
uv sync
uv run playwright install chromium --with-deps

uv run pytest                                  # pruebas (Playwright está simulado: sin navegador real)
uv run ruff check . && uv run ruff format .    # lint + formato
uv run fastmcp dev browsercontrol/server.py    # servidor de desarrollo con el inspector de MCP
```

```
browsercontrol/
├── server.py     # Instancia FastMCP, ciclo de vida, registro de herramientas
├── browser.py    # BrowserManager: ciclo de vida de Playwright, detección de elementos, renderizado de SoM
├── config.py     # configuración de variables de entorno
└── tools/        # un módulo por categoría, cada uno exporta register_*_tools(mcp)
```

CI ejecuta la suite en Ubuntu, Windows y macOS con `ruff`, `mypy --strict`,
`bandit` y `pytest`.

## Contribuir

Issues y PRs son bienvenidos — consulta [CONTRIBUTING.md](CONTRIBUTING.md). Las nuevas herramientas deben
incluir una prueba para el caso exitoso *y* para el caso de error; los archivos existentes
`tests/test_*.py` muestran el patrón.

En la lista, si buscas por dónde empezar: soporte para Firefox y WebKit,
configuraciones predeterminadas para dispositivos móviles, simulación de red, comparación de DOM entre instantáneas,
y auditorías de accesibilidad.

## Licencia

[MIT](LICENSE). Construido sobre [FastMCP](https://gofastmcp.com) y
[Playwright](https://playwright.dev).
