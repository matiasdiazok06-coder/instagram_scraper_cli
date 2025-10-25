@echo off
echo === Iniciando entorno virtual ===
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
echo.
echo === Ejemplo de uso ===
python cli.py --help
pause
