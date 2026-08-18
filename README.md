# Harvest API

[![CI](https://github.com/lfkanselmo/harvest-api/actions/workflows/ci.yml/badge.svg)](https://github.com/lfkanselmo/harvest-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.14%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/license-proprietary-lightgrey)

Generador de informes ejecutivos automáticos. Orquesta fuentes de datos heterogéneas
(clima, noticias, métricas internas de negocio), las normaliza vía el patrón Adapter y
produce un informe PDF con identidad visual propia, enviado por correo todos los días a
las 8:00 AM. Backend en Python 3.14 + FastAPI, construido con Arquitectura Hexagonal
(Ports & Adapters). Ver la especificación completa en
[`SAD_Harvest_Generador_Informes.md`](../SAD_Harvest_Generador_Informes.md).

---

## Requisitos

- Python 3.14+
- [`uv`](https://docs.astral.sh/uv/)
- Docker — necesario para generar PDFs en Windows (ver más abajo); opcional en macOS/Linux

---

## Configuración

### Variables de entorno

| Variable | Ejemplo | Descripción |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/harvest.db` | Conexión SQLite (SQLAlchemy 2.0 async) |
| `API_KEY` | (sin default) | Autentica `POST/GET /reports*`. Obligatoria — la app no arranca sin ella. Generar con `python -c "import secrets; print(secrets.token_hex(32))"` |
| `CORS_ORIGINS` | `["http://localhost:4200"]` | Orígenes permitidos para `harvest-web` en desarrollo (`ng serve`). En producción vía `docker compose`, nginx reenvía `/api/v1/` al mismo origen y no hace falta CORS |
| `REPORTS_DIR` | `./data/reports` | Carpeta donde se guardan los PDF generados |
| `SCHEDULER_TIMEZONE` | `America/Bogota` | Zona horaria del cron diario (APScheduler) |
| `WEATHER_LATITUDE` / `WEATHER_LONGITUDE` | `4.7110` / `-74.0721` | Coordenadas para `WeatherAdapter` (Open-Meteo, sin API key) |
| `NEWS_FEED_URL` | RSS de Google News | Feed que consume `NewsAdapter` (`feedparser`, sin API key) |
| `HTTP_TIMEOUT_SECONDS` | `5.0` | Timeout de las llamadas HTTP salientes |
| `SMTP_HOST` | (sin default, opcional) | Servidor SMTP para el envío del informe. Sin configurar, `NullNotifier` loguea y no envía — falla de forma segura, no bloquea la generación/guardado del informe |
| `SMTP_PORT` | `587` | Puerto SMTP |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | (sin default, opcionales) | Credenciales SMTP |
| `SMTP_FROM_ADDRESS` | `no-reply@harvest.local` | Remitente del correo |
| `SMTP_USE_TLS` | `true` | Si el servidor SMTP requiere STARTTLS |
| `REPORT_RECIPIENTS` | `["ops@harvest.local"]` | Destinatarios del informe diario |

Ver [`.env.example`](.env.example). Centralizadas en `Settings` (`pydantic-settings`,
`src/infrastructure/config.py`).

### Migraciones (Alembic)

```bash
uv run alembic upgrade head                          # aplica migraciones pendientes
uv run alembic revision --autogenerate -m "mensaje"  # genera una nueva migración
```

La migración inicial siembra `internal_metrics` (las métricas de negocio que lee
`ErpAdapter`) con datos de ejemplo; la segunda crea `reports`, el historial de informes
generados.

---

## Ejecución

### Local

```bash
uv sync
cp .env.example .env   # y completar API_KEY
uv run alembic upgrade head
uv run python src/main.py   # uvicorn con --reload, http://localhost:8000
```

Documentación interactiva en `/docs`.

### Docker

Ver [`../README.md`](../README.md) para el stack completo (API + panel web + Mailpit).
El `Dockerfile` de este repo (`docker/Dockerfile`) corre `alembic upgrade head`
automáticamente antes de levantar `uvicorn`.

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

`UV_PROJECT_ENVIRONMENT` apunta el venv del contenedor fuera del volumen montado para no
pisar el `.venv` de Windows con uno de Linux. En macOS/Linux nativos `uv sync` +
`uv run pytest` funcionan directo, sin contenedor — igual que en CI (`ubuntu-latest`
instala esas librerías vía `apt` y corre todo nativo).

---

## Tests

```bash
uv run pytest                                    # unitarios (dominio + aplicación + infraestructura)
uv run pytest -m integration                     # integración (SQLite real, PDF real, API con ASGITransport)
uv run mypy .                                     # tipado estricto
uv run ruff check .                               # lint
uv run python scripts/render_sample_report.py    # genera PDFs de muestra en data/, para revisión visual
```

Cobertura exigida: **100% en `src/domain`** (`--cov-fail-under=100` en `pyproject.toml`).
El test de contrato (`tests/unit/infrastructure/adapters/test_adapter_contract.py`)
ejercita las 5 implementaciones de `DataSource` (2 mock + 3 reales, con sus dependencias
externas mockeadas/inyectadas) para verificar que son intercambiables sin tocar
`GenerateReportUseCase` (Liskov Substitution).

---

## Documentación de la API

Todas las rutas bajo `/api/v1/reports*` requieren el header `X-API-Key` salvo `/health*`.

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| `GET` | `/api/v1/health` | pública | Liveness check |
| `GET` | `/api/v1/health/sources` | pública | Estado (`ok`/`unavailable`) de cada `DataSource`, llamando a cada una en vivo (golpea Open-Meteo/RSS de verdad — pensado para chequeo manual, no monitoreo de alta frecuencia) |
| `POST` | `/api/v1/reports/generate` | `X-API-Key` | Genera un informe ahora mismo (mismo flujo que dispara el scheduler), lo guarda y lo envía por correo |
| `GET` | `/api/v1/reports` | `X-API-Key` | Lista el historial de informes generados (`limit`, default 20) |
| `GET` | `/api/v1/reports/{id}/download` | `X-API-Key` | Descarga el PDF de un informe (`404` si no existe) |

---

## Arquitectura

```text
src/
├── domain/                # Metric, MetricStatus, Report, ReportPeriod — cero dependencias externas
├── application/
│   ├── ports/               # DataSource, ReportExporter, ReportRepository, Notifier (Protocol/ABC)
│   └── use_cases/            # GenerateReportUseCase, GenerateAndDeliverReportUseCase
└── infrastructure/
    ├── adapters/              # WeatherAdapter, NewsAdapter, ErpAdapter (+ 2 mocks)
    ├── pdf/                     # PDFExporter (WeasyPrint+Jinja2), ReportFactory, templates/, assets/fonts/
    ├── persistence/              # SQLAlchemy async: database.py, orm_models.py, SqliteReportRepository
    ├── email/                     # SmtpNotifier, NullNotifier
    ├── scheduling/                 # APScheduler
    └── api/                         # FastAPI: main.py (lifespan+CORS), dependencies.py, v1/
```

### Patrón Adapter y resiliencia

`DataSource` es el único contrato que conoce `GenerateReportUseCase` — nunca sabe si una
métrica vino de una API HTTP externa (`WeatherAdapter`, `NewsAdapter`) o de una tabla
interna (`ErpAdapter`). Cada adapter es responsable de su propia degradación: ante un
timeout o error, retorna una `Metric(status=unavailable)` en vez de propagar la
excepción; `GenerateReportUseCase` agrega una segunda capa de resiliencia
(`asyncio.gather(..., return_exceptions=True)`) por si un adapter mal implementado no
cumple su contrato. El fallback usa `source.source_name` (una etiqueta legible como
"Clima"), nunca el nombre de la clase Python.

### Generación de PDF

`PDFExporter` renderiza una plantilla Jinja2 (`ReportFactory` elige diaria/semanal,
Factory Method) y llama a WeasyPrint. La identidad visual ("Cosecha": ámbar `#A06509` +
verde bosque `#2F5233`, tipografía Fraunces/Inter autohospedada) vive en
`templates/report.css` como variables CSS, reutilizadas tal cual en `harvest-web`.

---

## Tecnologías

FastAPI · Pydantic v2 · SQLAlchemy 2.0 (async) · Alembic · aiosqlite · httpx · tenacity ·
feedparser · WeasyPrint · Jinja2 · APScheduler · aiosmtplib · pytest · mypy (`--strict`)
· ruff · uv

---

## Roadmap

Roadmap original de 4 semanas completo, más un hito adicional de frontend:

- **M1** — Dominio, puerto `DataSource`, 2 adapters mock, tests de contrato.
- **M2** — Adapters reales (`WeatherAdapter`/`NewsAdapter` vía HTTP, `ErpAdapter` sobre
  datos internos sembrados) + persistencia con SQLAlchemy/Alembic.
- **M3** — Identidad visual "Cosecha" y `PDFExporter` (WeasyPrint + Jinja2).
- **M4** — `GenerateAndDeliverReportUseCase` conecta generación → PDF → guardado →
  correo; scheduler (APScheduler), API con auth por `X-API-Key`, Dockerfile oficial.
- **M5** (`harvest-web`, repo aparte) — panel admin con la misma identidad visual.

Detalle completo, decisiones de diseño y razonamiento de cada hito en
[`SAD_Harvest_Generador_Informes.md`](../SAD_Harvest_Generador_Informes.md).
