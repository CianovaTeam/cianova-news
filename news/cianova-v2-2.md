---
id: "cianova-v2-2"
type: "cianova"
title_es: "CianovaLauncher - Release v2.2"
title_en: "CianovaLauncher - Release v2.2"
summary_es: "[Changelog](Doc/Changelog.md) for see the latest updates."
summary_en: "[Changelog](Doc/Changelog.md) for see the latest updates."
url: "https://github.com/CianovaTeam/CianovaLauncher-mcpelauncher/releases/tag/v2.2"
published: "2026-03-01"
version: "v2.2"
source: "cianova"
---

# CianovaLauncher - Release v2.2

[Changelog](Doc/Changelog.md) for see the latest updates.

**NEW:** Soporte multiperfil disponible para aislar tus mundos, recursos y configuraciones de Minecraft en diferentes perfiles mediante enlaces simbólicos (Symlink).
**NEW:** Se cambiaron los diálogos genéricos de Tkinter por unos más temáticos con la interfaz usando el mismo CustomTkinter.
**NEW:** Gestor de recursos disponible para gestionar tus recursos de Minecraft de manera eficiente. Puedes importar, eliminar, activar/desactivar tus ResourcesPack (RP), BehaviorPacks (BP) y tus mundos donde también puedes exportarlos fácilmente.
  **SOPORTE:** Tiene soporte para leer archivos en diferentes formatos (.mcpack, .mcaddon, .mcworld, .mcworldtemplate). Resuelve la ubicación del tipo de addon y en el caso de que no pueda, se puede ajustar manualmente. Ademas también muestra el nombre del addon real si esta dentro de archivos `.lang`.
**FIX:** Se optimizó el sistema de renderizado a uno por lotes y caché para un desplazamiento fluido.
**FIX:** El botón "Fix Shaders" se corrigió a "Desactivar Shaders" siendo el terminó más correcto. Además que se agrego la opción de modificar el modo de graficos desde el *Configurador de juego* disponible en herramientas.
**FIX:** Ahora el resolvedor de las claves internas tendrá en cuenta `cianovalauncher-config.json` a la hora de actualizar los datos.

[Changelog](Doc/Changelog.md) for see the latest updates.

## Builds:

| VERSION        | FILE                   | FILE EXTENSION | NOTE             |
| -------------- | ---------------------- | -------------- | ---------------- |
| Compiled       | `CianovaLauncher-v2.2` | `.tar.gz`      | Not need Bin pack    |
| Flatpak Repo   | `CianovaLauncher`      | `.flatpakrepo` | Only store o CLI |
| Flatpak Bundle | `CianovaLauncher-v2.2` | `.flatpak`     | No autoupdates   |

(PRE-COMPILED BIN PACK is `BIN X.Y.Z (Date) + Note.tar.gz`)

INFORM ALL BUGS AND ISSUES in **Doc/Issues**

Enjoy CianovaLauncher :)
