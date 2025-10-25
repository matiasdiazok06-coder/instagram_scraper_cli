INSTAGRAM SCRAPER CLI
====================

Uso rápido:
-----------
1. Descomprime este ZIP en tu escritorio.

Windows
-------
1. Abre CMD o PowerShell y ejecuta:
   cd Escritorio\instagram_scraper_cli
   run.bat

macOS / Linux
-------------
1. Abre la Terminal y ejecuta:
   cd "$HOME/Escritorio/instagram_scraper_cli"
   ./run.sh

> **Notas:**
> - Se requiere Python 3.9 o superior. Si cuentas con Python 3.10+ se instalarán las
>   dependencias más nuevas automáticamente; con 3.9 se usan versiones compatibles.
> - Los scripts usan un entorno virtual en `.venv`. Si la descarga de dependencias
>   falla por un proxy o falta de certificados, vuelve a ejecutar el script una vez
>   resuelto el acceso a Internet.

Los scripts (`run.bat` y `run.sh`):
----------------------------------
- Crean un entorno virtual (si no existe).
- Instalan dependencias desde `requirements.txt` (seleccionando las adecuadas según
  la versión de Python detectada).
- Lanzan el menú interactivo del CLI si no se pasan argumentos manuales.

Menú interactivo
----------------
Al ejecutar `./run.sh` (o `run.bat`) sin argumentos aparecerá un menú paso a paso
que te pedirá:

1. Ruta del archivo de sesión (`session.json` por defecto).
2. Usuario y contraseña de tu cuenta (el password se solicita con ocultamiento).
3. Un proxy opcional.
4. Los usernames objetivo (desde archivo o escribiéndolos en pantalla).
5. El nombre del CSV de salida y el delay entre solicitudes.

Una vez confirmados los datos, el scraper inicia automáticamente y al finalizar
muestra la ruta del CSV generado.

Cómo ejecutar el scraper manualmente
------------------------------------
Si prefieres pasar los parámetros por línea de comandos:

```
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
python cli.py --session session.json \
  --username-mi-cuenta TU_USUARIO --password TU_PASSWORD \
  --targets-file usernames.txt --out-file resultado.csv
```

El archivo `usernames.txt` debe contener un usuario por línea. También puedes pasar
los objetivos directamente con `--targets usuario1 usuario2` o lanzar el menú con
`--menu`.

Columnas del CSV generado
-------------------------
- username
- pk
- full_name
- followers
- media_count
- is_private / is_public
- is_verified
- biography (en una sola línea)
- has_highlight_reels (si tiene historias destacadas)
- follower_bucket (segmento por cantidad de seguidores)
- error (detalle en caso de fallas individuales)
