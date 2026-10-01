# Guion del video (máx. 5:00)

**Antony** presenta Bandit · **Adriana** presenta CodeQL. ~700 palabras habladas en total.

## Preparación (antes de grabar)
- [ ] Pestañas abiertas: repo · Actions run #7 · Security → Code scanning · PR #1 (pestañas *Conversation* y *Checks*) · https://sast-flask-demo.onrender.com (ábrela 1 min antes para despertarla) · `bandit.html` de `03_bandit/antes/`.
- [ ] Terminal en `sast-flask-demo`, con la versión vulnerable para las demos en vivo:
  ```powershell
  git switch --detach v1-vulnerable
  .\.venv\Scripts\python.exe -m app.app          # en otra terminal
  ```
  Al terminar de grabar: `git switch main`.
- [ ] Usuarios de prueba en la app local: `ana / clave-ana` y `beto / clave-beto`, con la nota "Privado de Beto". Si se borraron, créalos de nuevo.
- [ ] SonarCloud quitado del repo, o evitar que se vea su comentario en el PR.
- [ ] Plan B: si algo falla en vivo, mostrar las capturas de `09_capturas/`.

---

### 0:00–0:25 · Intro (Adriana)
**Pantalla:** README del repo (diagrama Mermaid).
> "Hola, somos Adriana Laos y Antony Solorzano, del curso Calidad y Pruebas de Software de la UPT. Construimos NotasApp, una app Flask con cinco vulnerabilidades a propósito. La analizamos con dos herramientas SAST de la lista de OWASP, Bandit y CodeQL, y armamos un pipeline que bloquea el despliegue si encuentra fallas graves."

### 0:25–1:05 · La app y dos ataques (Antony)
**Pantalla:** app local → Buscar → `' OR 1=1 --` → Ping → `127.0.0.1 && whoami`.
> "Iniciamos sesión como Ana. Si en el buscador escribo comilla, OR 1 igual 1, guion guion, aparece la nota privada de Beto: es una inyección SQL, porque la consulta se arma con un f-string. En la utilidad de ping escribo una IP seguida de 'y y whoami' y el servidor ejecuta mi comando: inyección de comandos, por `shell=True`. Además, la app tiene la SECRET_KEY escrita en el código, guarda las contraseñas con MD5 y corre en modo debug."

### 1:05–2:05 · Bandit (Antony)
**Pantalla:** terminal → `bandit -r app` → abrir `bandit.html`.
> "Bandit es de PyCQA, licencia Apache y solo para Python. Se instala con pip y se corre con un comando: `bandit -r app`. En menos de medio segundo encontró las cinco vulnerabilidades: B608 para la SQL, B602 para shell=True, B105 para el secreto, B324 para MD5 y B201 para el debug."

**Pantalla:** resaltar B608 "Severity: Medium, Confidence: Low".
> "Bandit busca patrones en el árbol sintáctico, pero no sabe de dónde viene el dato. Por eso califica la inyección SQL con confianza baja, y con el filtro de severidad alta, `-lll`, no la bloquearía. Es rapidísimo, pero no tiene contexto."

### 2:05–3:05 · CodeQL (Adriana)
**Pantalla:** `04_codeql/antes/codeql.txt` (sección py/sql-injection con el flujo de datos).
> "Mi herramienta iba a ser Bearer CLI, pero al revisar sus reglas vimos que no reconoce `flask.request` y solo detectó una de cinco. Por eso usamos CodeQL, de GitHub."

> "CodeQL convierte el código en una base de datos y hace taint tracking: sigue el dato del usuario desde `request.args` hasta el `execute`. Mírenlo aquí: línea 110, la variable `q`, la consulta y la línea 115. Detectó las cinco con precisión alta, la inyección de comandos con 9.8, crítica. Un detalle: el secreto en el código solo lo detecta con una consulta experimental que activamos en la configuración."

> "Su costo: el paquete pesa casi 700 megas y es unas 50 veces más lento que Bandit."

### 3:05–4:10 · Pipeline y quality gate (Antony → Adriana)
**Pantalla (Antony):** Actions run #7 (4 jobs en verde) → Artifacts → Security → Code scanning.
> "En GitHub Actions corren cuatro jobs: pruebas con pytest, Bandit, CodeQL y deploy. Los dos escáneres suben sus resultados en formato SARIF a Code Scanning, donde están las 11 alertas de la versión vulnerable, ya cerradas."

**Pantalla (Adriana):** PR #1 → comentarios del bot (Bandit Error, CodeQL Critical con "Show paths") → caja de checks en rojo.
> "Para probar el quality gate, en este Pull Request volvimos a meter la inyección de comandos. Las dos herramientas comentan la línea exacta, y CodeQL hasta sugiere la corrección. Los jobs de pruebas, Bandit y CodeQL fallan, y el despliegue se omite: el código inseguro no llega a producción. Como la acción de CodeQL no falla sola, escribimos un script que lee el SARIF y corta si la severidad es 7 o más."

### 4:10–4:45 · Corrección y despliegue (Antony)
**Pantalla:** `05_comparativa/antes_vs_despues.md` (V1 y V2) → app en Render.
> "Corregimos cada falla en un commit separado: consultas parametrizadas, subprocess sin shell con validación del host, la clave en una variable de entorno, contraseñas con scrypt y debug desactivado. Bandit bajó de 6 hallazgos a 2 avisos informativos y CodeQL de 5 a cero. La versión corregida se despliega en Render con un Deploy Hook y ya está en línea."

**Pantalla:** en la app de Render, Ping con `127.0.0.1 && whoami` → "Host no válido".

### 4:45–5:00 · Cierre (Adriana)
**Pantalla:** tabla comparativa del README.
> "En conclusión, se complementan: Bandit es un filtro rápido y sin configuración; CodeQL es más lento, pero entiende el flujo de los datos y no dio falsos positivos. El código y las evidencias están en el repositorio. ¡Gracias!"

---

## Consejos
- Ensayar una vez con cronómetro. Si se pasan del tiempo, recortar primero la parte de Render (4:10).
- Hacer zoom en el navegador (Ctrl +) y usar una terminal con letra grande.
- No mostrar la página de Settings → Secrets ni el Deploy Hook.
