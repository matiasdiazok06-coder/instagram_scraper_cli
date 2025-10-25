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

Los scripts (`run.bat` y `run.sh`):
----------------------------------
- Crean un entorno virtual (si no existe).
- Instalan dependencias desde `requirements.txt`.
- Muestran la ayuda del CLI para que veas las opciones disponibles.

Cómo ejecutar el scraper
------------------------
Una vez instalado el entorno, puedes ejecutar el scraper así:

```
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
python cli.py --session session.json \
  --username-mi-cuenta TU_USUARIO --password TU_PASSWORD \
  --targets-file usernames.txt --out-file resultado.csv
```

El archivo `usernames.txt` debe contener un usuario por línea. También puedes pasar
los objetivos directamente con `--targets usuario1 usuario2`.

El CSV resultante incluye:
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
