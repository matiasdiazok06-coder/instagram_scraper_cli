INSTAGRAM SCRAPER CLI - propiedad de matidiazlife/elite
======================================================

Requisitos
----------
* Python 3.11 o superior instalado en el sistema (`python3` en macOS/Linux, `py -3` en Windows).
* Acceso a Internet para instalar dependencias y comunicarse con Instagram.

Instalación rápida
------------------
1. Descomprime el proyecto en tu escritorio.
2. Abre una terminal en la carpeta `instagram_scraper_cli`.
3. Ejecuta el script según tu sistema operativo:

   **macOS / Linux**
   ```bash
   cd "$HOME/Escritorio/instagram_scraper_cli"
   ./run.sh
   ```

   **Windows (PowerShell o CMD)**
   ```cmd
   cd %USERPROFILE%\Desktop\instagram_scraper_cli
   run.bat
   ```

Los scripts crean/reutilizan un entorno virtual `venv`, instalan las dependencias definidas en `requirements.txt` y lanzan el menú interactivo del CLI.

> ⚠️ **Python 3.14+**: Los scripts de arranque fuerzan la descarga de binarios precompilados de `pydantic` y `pydantic-core` (sin intentar compilar código Rust). Si todavía no existen wheels compatibles, el proceso se abortará con una advertencia que recomienda usar Python 3.13.x para garantizar la instalación.

Dependencias clave
------------------
* `instagrapi>=2.1.2`
* `pydantic>=2.9.2`
* `pandas`
* `rich`
* `tabulate`

El archivo `requirements.txt` fija estas librerías junto con los paquetes de soporte necesarios (Pillow, typing-extensions, etc.).

Menú principal
--------------
Al ejecutar `cli.py` sin argumentos aparecerá un menú con el encabezado:

```
===========================================
INSTAGRAM SCRAPER CLI - propiedad de matidiazlife/elite
1. Iniciar sesión en Instagram
2. Hacer scraping por hashtags
3. Hacer scraping por perfiles
4. Aplicar filtros a resultados existentes
5. Configuración y sesión actual
6. Salir
===========================================
```

Descripción de opciones
-----------------------
1. **Iniciar sesión en Instagram**: pide usuario y contraseña, maneja 2FA/challenges y guarda la sesión en `session.json` junto con los metadatos en `session_meta.json`. Si existe una sesión previa se ofrece reutilizarla.
2. **Scraping por hashtags**: solicita un hashtag, la cantidad máxima de publicaciones y filtros opcionales (rango de seguidores, mínimo de posts, privacidad, verificación, historias destacadas). Guarda `result.csv` en `~/Desktop/instagram_scraper_results/<hashtag>/` y muestra una tabla con los primeros 10 resultados.
3. **Scraping por perfiles**: admite una lista manual o desde archivo `.txt`. Permite elegir entre seguidores o seguidos, aplicar los mismos filtros y crea `followers.csv` o `following.csv` dentro de `~/Desktop/instagram_scraper_results/perfiles/<username>/`.
4. **Aplicar filtros a resultados existentes**: lista los CSV guardados, permite seleccionar uno y aplicar filtros sin volver a scrapear. El resultado se guarda como `filtered_result.csv` en la misma carpeta.
5. **Configuración y sesión actual**: muestra la ruta de `session.json`, el usuario almacenado, la carpeta de resultados y ofrece eliminar la sesión guardada.
6. **Salir**: finaliza la ejecución con el mensaje de agradecimiento correspondiente.

Estructura de resultados
------------------------
Todos los CSV se guardan en `~/Desktop/instagram_scraper_results/` siguiendo esta convención:

```
instagram_scraper_results/
├── <hashtag>/
│   ├── result.csv
│   └── filtered_result.csv (opcional)
└── perfiles/
    └── <username>/
        ├── followers.csv o following.csv
        └── filtered_result.csv (opcional)
```

Columnas exportadas
-------------------
Cada CSV incluye al menos estas columnas:
* `username`
* `full_name`
* `followers`
* `following`
* `media_count`
* `is_private`
* `is_verified`
* `has_highlight_reels`
* `source` (solo en listados de perfiles para identificar la cuenta origen)

Consejos adicionales
--------------------
* Entre cada solicitud se introduce un retardo aleatorio para reducir el riesgo de rate limits.
* Ante errores de login o límites de Instagram, el CLI muestra mensajes descriptivos y permite reintentar.
* Si necesitas actualizar dependencias manualmente, activa el entorno virtual (`source venv/bin/activate` o `venv\Scripts\activate`) y ejecuta `pip install -r requirements.txt`.
