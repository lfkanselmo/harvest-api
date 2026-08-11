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
```

## Estado actual

**M3**: identidad visual de marca cerrada ("Cosecha": ámbar/verde bosque, Fraunces +
Inter) aplicada en `PDFExporter` (WeasyPrint + Jinja2) y `ReportFactory` (Factory
Method, elige plantilla diaria/semanal). Junto con M1/M2, `GenerateReportUseCase`
sigue siendo indiferente a cuál de los cinco `DataSource` reciba (Liskov
Substitution). Sin API HTTP, scheduler ni envío de correo todavía — eso llega en
M4.
