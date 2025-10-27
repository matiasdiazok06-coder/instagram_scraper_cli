INSTAGRAM SCRAPER CLI - propiedad de matidiazlife/elite
Consejos adicionales
--------------------
* Entre cada solicitud se introduce un retardo aleatorio para reducir el riesgo de rate limits.
* Ante errores de login o límites de Instagram, el CLI muestra mensajes descriptivos y permite reintentar.
* Si necesitas actualizar dependencias manualmente, activa el entorno virtual (`source venv/bin/activate` o `venv\Scripts\activate`) y ejecuta:
  1. `pip install --pre --only-binary=:all: pydantic-core>=2.27.0 pydantic>=2.9.2`
  2. `pip install -r requirements-base.txt`
  3. `pip install --no-deps instagrapi>=2.1.2`
