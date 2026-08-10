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
uv run pytest
uv run ruff check .
uv run mypy .
```

## Estado actual

**M1**: dominio (`Metric`, `Report`) y el puerto `DataSource` con dos adapters mock,
verificando que el caso de uso `GenerateReportUseCase` es indiferente a cuál
implementación de `DataSource` recibe (Liskov Substitution). Sin API HTTP, sin
persistencia y sin PDF todavía — eso llega en los siguientes hitos del roadmap.
