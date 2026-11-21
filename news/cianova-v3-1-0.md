---
id: "cianova-v3-1-0"
type: "cianova"
title_es: "Cianova Launcher v3.1.0"
title_en: "Cianova Launcher v3.1.0"
summary_es: "Nueva versión de CianovaLauncher: Cianova Launcher v3.1.0."
summary_en: "Nueva versión de CianovaLauncher: Cianova Launcher v3.1.0."
url: "https://github.com/CianovaTeam/CianovaLauncher-mcpelauncher/releases/tag/v3.1.0"
published: "2026-07-04"
version: "v3.1.0"
source: "cianova"
---

# Cianova Launcher v3.1.0

Nueva versión de CianovaLauncher: Cianova Launcher v3.1.0.

### 🔧 Gestor de Recursos (Addons + Mods)
- Los `.zip` con múltiples manifests ahora se detectan y los RP+BP se instalan por separado.
- Validación de ZIP con `testzip()` antes de extraer para evitar instalaciones corruptas.
- Añadido soporte para `.mctemplate` en escaneo y filtro de archivos.
- Escaneo recursivo de subdirectorios en `mods/` para encontrar `.so`.
- Nombres duplicados en `.mcaddon` se resuelven con sufijo (`_1`, `_2`) automáticamente.
- Exportación de mundos con sanitización más permisiva para nombres de archivo.
- Corregido el filtro de pestañas: la pestaña RP ya no muestra mods por error.

### 📦 Mod DRM desde compilación propia de Leimsoto
- El mod DRM (mcpelauncher-updates) ahora se descarga directamente desde [github.com/Leimsoto/mcpelauncher-updates](https://github.com/Leimsoto/mcpelauncher-updates/releases) en lugar del repositorio oficial ModDB.
- Arquitecturas mapeadas: `x86_64` y `arm64-v8a` con release tagging `v1.0.0`.
- Fallback de librerías: `libmcpelauncher-updates.so` resuelve como `libmcpelauncher_mod.so` en `_ensure_mc_libraries`.
- El launcher busca librerías dentro del mod instalado como fuente adicional.
- Mensajes y créditos actualizados para reflejar la fuente MIT de Leimsoto.
- Al lanzar una versión instalada desde Google Play, si falta el mod DRM el launcher pregunta si instalarlo antes de continuar. Si está desactivado, muestra advertencia.
- La gestión del mod DRM se movió completamente al Gestor de Recursos, eliminando la sección duplicada en Herramientas.

### 🏷️ Control de carga de mods
- Cada mod tiene checkbox "Cargar al inicio" que persiste entre sesiones.
- El estado se guarda con escritura atómica (`tmp` + `os.replace`) para evitar corrupción.
- Directorios `patches/` se filtran automáticamente del listado de mods a cargar.
- Los directorios de mod ahora se pasan explícitamente al comando de lanzamiento con flags `-m`.

### 📋 Metadatos de instalación
- Ahora se registra si una versión se instaló desde Google Play o desde un APK local.

### 🚀 Comportamiento de Inicio
- Nuevo sistema LaunchAction con tres modos: `close` (cerrar launcher), `hide` (minimizar a bandeja del sistema), `none` (indicador de estado en la UI).
- Monitor de juego con QTimer cada 2s para detectar cuándo termina el proceso.
- Migración automática: si tenías `close_on_launch: true`, se convierte a `launch_action: "close"`.

### 💾 Persistencia de Configuración
- Los checkboxes de Nvidia/Zink/Gamemode/LaunchAction y el campo de variables de entorno ahora persisten inmediatamente al cambiar.
- Gamemode y LaunchAction sincronizados entre pestañas Play y Settings.

### 🎮 Discord Rich Presence
- Envío síncrono de estado además de la cola para actualización inmediata.
- Añadidas rutas IPC para Discord Canary y PTB Flatpak.
- Limpieza mejorada: `stop()` llama a `clear()` antes de `close()`.

### 📋 Diálogo de Instalación
- La pestaña APK Local es ahora la predeterminada (Google Play en segundo lugar).

### ⚙️ Ajustes reorganizados
- Los ajustes ahora se organizan en 4 categorías con pestañas superiores: General, Lanzamiento, Apariencia e Integraciones.
- Navegación por QStackedWidget para evitar el scroll infinito.
- La categoría seleccionada se resalta con el color de acento.

### 🖥️ Detector de Hardware mejorado
- Soporte para arquitecturas ARM (lectura de `Features` además de `flags`).
- Timeout en `glxinfo` para evitar congelamientos.
- Parseo robusto de OpenGL ES con regex.
- Soporte x86 (32-bit) con requisito SSSE3.
- Soporte ARM NEON con detección y clasificación.
- GL desconocido ya no marca como Incompatible — asume ES 3.0.
- Rangos de versión actualizados.
- El indicador CPU muestra SSE/SSSE3/NEON según la arquitectura.

### 🐛 Correcciones
- ProgressDialog: ahora muestra mensajes largos sin cortarlos, con método para actualizar texto en vivo.
- Guardado de configuración de mods ahora atómico (tmp + `os.replace`) para evitar archivos corruptos.
