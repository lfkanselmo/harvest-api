# Harvest API

Generador de informes ejecutivos automáticos. Orquesta fuentes de datos heterogéneas,
las normaliza vía el patrón Adapter y produce un informe PDF enviado por correo.
Backend en Python 3.12 + Arquitectura Hexagonal (Ports & Adapters). Ver la
especificación completa en
[`SAD_Harvest_Generador_Informes.md`](../SAD_Harvest_Generador_Informes.md).

---

## Requisitos

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/)
- Docker, solo para lo relacionado a generación de PDF (ver más abajo)

---

## Desarrollo

```bash
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run ruff check .
uv run mypy .
```

### WeasyPrint en Windows

`weasyprint` depende de librerías nativas (Pango/Cairo/GTK) que Windows no trae.
Cualquier comando que importe `src.infrastructure.pdf` (incluida la suite de tests
completa, porque pytest colecciona todos los módulos) debe correr dentro de un
contenedor Linux con esas librerías instaladas:

```bash
docker build -t harvest-pdf-dev -f docker/Dockerfile.dev .
docker run --rm -v "$(pwd):/app" -w /app \
  -e PYTHONPATH=/app -e UV_PROJECT_ENVIRONMENT=/opt/venv \
  harvest-pdf-dev bash -c "uv sync --quiet && uv run pytest -q -m ''"
```

`UV_PROJECT_ENVIRONMENT` apunta el venv del contenedor fuera del volumen montado
para no pisar el `.venv` de Windows con uno de Linux. En macOS/Linux nativos
`uv sync` + `uv run pytest` funcionan directo, sin contenedor.

```bash
uv run pytest              # tests unitarios (excluye integration)
uv run pytest -m integration
uv run python scripts/render_sample_report.py   # PDFs de muestra en data/
uv run python src/main.py                        # levanta la API en :8000 (con reload)
```

### Variables de entorno nuevas en M4

Ver [`.env.example`](.env.example). `API_KEY` es obligatoria (generar con
`python -c "import secrets; print(secrets.token_hex(32))"`). Sin `SMTP_HOST`
configurado, el envío de correo se omite de forma segura (`NullNotifier`, queda
logueado) en vez de fallar.

### Levantar el stack completo (API + Mailpit)

Ver [`../README.md`](../README.md) — el `docker-compose.yml` vive en la raíz porque
orquesta este repo junto a Mailpit.

## Estado actual

**M4**: `GenerateAndDeliverReportUseCase` conecta todo el ciclo — genera el reporte,
lo exporta a PDF, lo guarda en `data/reports/` + tabla `reports` (SQLite), y lo envía
por correo (`SmtpNotifier`/`NullNotifier`). Lo dispara tanto APScheduler (cron diario
8:00 AM) como `POST /api/v1/reports/generate` (auth por `X-API-Key`). `GET /reports`
lista el historial, `GET /reports/{id}/download` descarga el PDF. Verificado
end-to-end con `docker compose up`: auth, trigger manual, listado, descarga y correo
con adjunto en Mailpit. Pendiente: decisión de frontend (`harvest-web`).
