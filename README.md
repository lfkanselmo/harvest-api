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

---

## Desarrollo

```bash
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run pytest              # tests unitarios (excluye integration)
uv run pytest -m integration
uv run ruff check .
uv run mypy .
```

## Estado actual

**M2**: además del dominio y `GenerateReportUseCase` de M1, ahora hay tres adapters
reales — `WeatherAdapter` (Open-Meteo + reintentos con `tenacity`), `NewsAdapter`
(RSS vía `feedparser`) y `ErpAdapter` (lee `internal_metrics`, tabla sembrada por
Alembic) — que conviven con los dos adapters mock demostrando que
`GenerateReportUseCase` es indiferente a cuál de los cinco reciba (Liskov
Substitution). Sin API HTTP, scheduler ni PDF todavía — eso llega en los
siguientes hitos del roadmap.
