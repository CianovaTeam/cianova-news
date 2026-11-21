---
id: "cianova-v3-0"
type: "cianova"
title_es: "CianovaLauncher - Release v3.0"
title_en: "CianovaLauncher - Release v3.0"
summary_es: "[Changelog](Doc/Changelog.md) for see the latest updates."
summary_en: "[Changelog](Doc/Changelog.md) for see the latest updates."
url: "https://github.com/CianovaTeam/CianovaLauncher-mcpelauncher/releases/tag/v3.0"
published: "2026-06-22"
version: "v3.0"
source: "cianova"
---

# CianovaLauncher - Release v3.0

[Changelog](Doc/Changelog.md) for see the latest updates.

# [3.0] - 2026-05-12 — The Qt6 Evolution

### 🔄 Framework: CustomTkinter → PySide6 (Qt6)
- Migración completa de toda la interfaz (19 archivos UI) de CustomTkinter a PySide6/Qt6.
- Las ventanas principales (`QMainWindow`), pestañas (`QWidget`) y diálogos (`QDialog`) ahora usan widgets Qt nativos.
- Los mensajes del sistema (`custom_dialogs.py`) reemplazaron los Tkinter messagebox por diálogos Qt temáticos.
- El sistema de imágenes migró de `CTkImage` a `QPixmap`/`QIcon` con caché centralizada.
- Los selectores de archivo migraron de `filedialog` a `QFileDialog`.
- El modelo de hilos migró a `QThread`/`QTimer`/`QProcess` para operaciones asíncronas.
- El sistema de estilos reemplazó los atributos de CustomTkinter por QSS (Qt Style Sheets) con selectores por ID.
- El tema oscuro usa `#242424` de fondo base con paneles `#3a3a3a` y acentos dinámicos.
- Dependencia eliminada: `customtkinter` → reemplazada por `PySide6`.
- Flatpak: actualizado de `org.kde.Platform//5.15` a `//6.10` (Qt6).

### ✨ Nuevas Funcionalidades

#### Google Play Integration
- Sistema completo de descarga desde Google Play: login vía `playdl-signin-ui-qt`, exploración de versiones con filtros Beta/Estables, descarga APK mediante `gplaydl`.
- Diálogo de instalación con dos pestañas: "Google Play" y "APK Local".
- Gestión de sesión: token guardado en `playdl.conf` con permisos `0o600`, detección de sesión alternativa vía `gplayver`.
- Mapeo de errores de Google Play traducibles a 7 idiomas.

#### Discord Rich Presence
- Integración completa vía `pypresence`: muestra "Explorando el launcher" en reposo y "Jugando {versión}" en juego con contador de tiempo.
- Activable desde el Play Tab y desde Ajustes.
- Client ID personalizable desde Ajustes (además del por defecto `1505628404362248213`).
- Permisos Flatpak para comunicación con Discord.

#### Gestor Avanzado de Versiones
- Nuevo diálogo para gestionar versiones instaladas: asignar iconos personalizados, ajustar posición/zoom, crear accesos directos `.desktop`, renombrar y eliminar carpetas, abrir directorios de datos y capturas.

#### Asistente de Migración (MigrationWizard)
- Reemplazado el antiguo `MigrationDialog` por un asistente de 5 pasos con tarjetas interactivas: Origen → Perfil → Contenido → Método → Resumen.
- +22 cadenas de texto traducidas a 7 idiomas.

#### Setup Wizard (Primer Inicio)
- Nuevo asistente de 7 pasos: Idioma → Términos → Migración → Estilo → Instalación → Changelog → Resumen.
- Flags CLI: `--first-wizard`, `--factory-reset`.

#### Changelog Dialog
- Nuevo diálogo que muestra el changelog en Markdown con cabecera de icono.

#### Update Checker
- Sistema de detección remota de actualizaciones. Consulta `version.json` en GitHub Pages al iniciar (máx. 1 vez/día) y muestra aviso si hay versión más reciente.
- Botón "Check Update (test)" en `--test-mode`.
- `version.json` soporta campo `prerelease`.
- Desplegado en `gh-pages`, compatible con GitHub Actions.

#### Gestor de Mods MCPELauncher
- Nueva pestaña "Mods MCPELauncher" en el Gestor de recursos.
- Escanea `mods/` en busca de `.so`; muestra tamaño, toggle activar/desactivar (`.so` ↔ `.so.disabled`) y eliminar.
- Importación de mods: file picker acepta `.so` (copia directa) y `.zip` (extrae los `.so` automáticamente).

#### Sistema de Advertencias de Compatibilidad
- Consulta remota de `version-warnings.json` en GitHub Pages.
- Muestra aviso en primer plano al instalar versiones con bugs conocidos, tanto en Google Play como en APK Local.
- El archivo JSON se actualiza remotamente sin necesidad de actualizar el launcher.

### 🎨 UI/UX y Personalización

#### Motor de Personalización
- Fondos de pantalla personalizados con control de opacidad.
- Sistema de marcas de agua (stickers) con opacidad y orden Z configurables.
- Transparencia dinámica por sección.
- Control de tamaño de iconos y títulos en las tarjetas de versión.
- Vista de lista o cuadrícula para el selector de versiones.

#### Temas de Color
- 12 temas profesionales: midnight, cherry, cyan, gray, ocean, orange, purple, red, yellow, más variantes claro/oscuro.
- Temas almacenados como JSON en `src/themes/`.
- Estilo QSS dinámico generado por `apply_theme_settings()` (~300 líneas).

#### Mejoras Visuales
- Tarjetas de versión con fondo sólido y etiquetas refinadas.
- Scrollbars consistentes en todas las secciones.
- Barra de pestañas centrada correctamente.
- Flecha de QComboBox renderizada correctamente (corregido el fallo del pseudo-triángulo CSS que se mostraba como "—").
- Layouts con limpieza optimizada de widgets sin fugas de memoria.

### 🧠 Arquitectura y Código

#### Reorganización del Código
- `constants.py` dividido en: `values.py` (modos/estilos), `config_keys.py` (claves de configuración), `ui_strings.py` (cadenas UI, +600 líneas).
- Nuevos módulos: `install_ops.py` (operaciones de instalación), `worker.py` (QThread genérico), `utils/colors.py` (utilidades de color).
- `app_logic.py` reducido de ~591 a ~338 líneas como fachada.
- Total: 45 archivos Python, ~9,660 líneas.

#### Optimizaciones de Rendimiento
- Carga de versiones asíncrona mediante QThread (elimina el bloqueo "Searching...").
- QSS global con selectores por ID elimina los congelamientos al cambiar de pestaña.
- Debounce de 100ms para reposicionamiento de overlays al redimensionar.
- Caché centralizada de imágenes (`ImageManager`) para minimizar E/S de disco.
- Las versiones se muestran en orden inverso (nuevas primero) con filtro "Estables" por defecto.
- Renderizado por lotes en lugar de actualizaciones individuales.

### ⚙️ Sistema de Compilación y Empaquetado

#### PyInstaller
- Spec actualizado: colección PySide6, import oculto `pypresence`, datos: `icon.png`, `src/langs`, `src/themes`, `Docs`.

#### Flatpak
- Runtime Qt6 (`org.kde.Platform//6.10` + `io.qt.qtwebengine.BaseApp//6.10`).
- Permisos: Discord IPC, red, sistema de archivos para migración.
- Variables de entorno: `QT_QPA_PLATFORMTHEME=kde`, `QT_STYLE_OVERRIDE=kvantum`.

#### CLI
- `--test-mode`, `--first-wizard`, `--factory-reset`, `--force-flatpak-ui`, `--force-nvidia-ui`.

### 🌐 Traducciones (i18n)
- 7 idiomas: español, inglés, francés, alemán, italiano, portugués, catalán.
- `LEGAL_TEXT` movido de archivos de idioma a constantes.py.
- Errores de Google Play traducibles en todos los idiomas.
- Sistema de traducción mediante monkey-patching de `constants` vía `language_manager.py`.

### 🐛 Correcciones
- **UI freezes eliminados:** Cambio de pestañas y carga de versiones ya no bloquean la interfaz.
- **"Searching..." corregido:** La lista de versiones ya no se queda cargando infinitamente.
- **Ruta de sesión de Google Play:** Corregida para funcionar dentro del sandbox de Flatpak.
- **Detección alternativa de sesión:** Fallback vía `gplayver` cuando falla la lectura de archivos.
- **Nombre de archivo device.conf:** Corregido (era `cianova-device.conf`).
- **Detección de runtimes Flatpak:** Ahora funciona desde dentro del sandbox.
- **Artefactos visuales:** Al hacer clic en tarjetas de versión durante movimiento de ventana.
- **Suavidad de overlays:** Movimiento de fondo y sticker al redimensionar.
- **execve fallback:** En equipos restrictivos, si falla el lanzamiento normal, reemplaza el proceso.
- **Señales de checkbox:** Actualizadas con `Qt.Checked.value` para compatibilidad PySide6 reciente.
- **Sincronización de ajustes:** GameMode y Cerrar-al-iniciar ahora sincronizados entre pestañas.
- **Visibilidad de stickers:** Corregido orden Z y caché de pixmaps.
- **Alpha de Qt:** Corregido rango de 0.0-1.0 (Tkinter) a 0-255 (Qt).
- **Clave "Blur" residual:** Eliminada de configuración (feature roto).
- **Importaciones faltantes:** `json`, `platform`, `shlex` restauradas tras la migración.

### 🚀 Soporte y Compatibilidad
- **Nvidia Prime/Zink:** Gestión limpia de variables de entorno con opciones separadas.
- **GameMode:** Soporte completo con sincronización entre tabs.
- **Variables de entorno personalizadas:** Configurables desde Ajustes.
- **Verificador de dependencias:** Compatible con Flatpak.
- **Verificador de hardware:** Ahora funciona dentro de Flatpak.
- **Selector de modo de gráficos:** En el Configurador de Juego.

### 🗑️ Archivos Eliminados
- `src/gui/migration_dialog.py` (317 líneas, reemplazado por `migration_wizard.py`).
- Tkinter font tuples en `constants.py`.
- Blur config keys (feature roto).

### 📦 Archivos Nuevos (v3.0)
| Archivo | Líneas | Propósito |
|---------|--------|-----------|
| `src/core/google_integration.py` | 602 | Google Play login/download |
| `src/core/discord_rpc.py` | 193 | Discord Rich Presence |
| `src/core/config_keys.py` | 91 | Claves de configuración |
| `src/core/values.py` | 22 | Constantes de modo/estilo |
| `src/core/ui_strings.py` | 609 | Cadenas de interfaz |
| `src/core/install_ops.py` | 304 | Operaciones de instalación |
| `src/core/worker.py` | 22 | QThread worker genérico |
| `src/utils/colors.py` | 21 | Utilidades de color |
| `src/gui/setup_wizard.py` | ~450 | Asistente de primer inicio |
| `src/gui/migration_wizard.py` | 828 | Asistente de migración |
| `src/gui/changelog_dialog.py` | ~100 | Diálogo de changelog |
| `src/gui/version_manager_dialog.py` | 364 | Gestor avanzado de versiones |


[Changelog](Doc/Changelog.md) for see the latest updates.

## Builds:

| VERSION        | FILE                   | FILE EXTENSION | NOTE             |
| -------------- | ---------------------- | -------------- | ---------------- |
| Compiled       | `CianovaLauncher-v3.0` | `.tar.gz`      | Not need Bin pack    |
| Flatpak Repo   | `CianovaLauncher`      | `.flatpakrepo` | Only store o CLI |
| Flatpak Bundle | `CianovaLauncher-v3.0` | `.flatpak`     | No autoupdates   |

(PRE-COMPILED BIN PACK is `BIN 1.7.4 (220626) + Qt6(Patch).tar.gz`)

INFORM ALL BUGS AND ISSUES in **Doc/Issues**

Enjoy CianovaLauncher :)
