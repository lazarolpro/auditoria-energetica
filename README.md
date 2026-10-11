# Capa 6 — Analítica de eficiencia energética

[![CI](https://github.com/lazarolpro/auditoria-energetica/actions/workflows/ci.yml/badge.svg)](https://github.com/lazarolpro/auditoria-energetica/actions/workflows/ci.yml)
[`lazarolpro/auditoria-energetica`](https://github.com/lazarolpro/auditoria-energetica) · parte del [portafolio de 6 capacidades](https://github.com/lazarolpro/portafolio)

**Capacidad demostrada:** convertir la curva de carga de un medidor en
indicadores de eficiencia y en un ahorro estimado con acciones concretas.

## Problema real

El consumo "fuera de horario" y las cargas ociosas se pagan todos los meses sin
que nadie las vea. Sin analizar la curva de carga, el desperdicio es invisible.

## Qué hace

- Ingestiona la curva de carga de un medidor (intervalos de 15 minutos).
- Calcula consumo, carga base, demanda punta, **factor de carga** y consumo
  fuera de horario.
- Detecta desperdicio y estima el ahorro potencial en kWh y USD.
- Genera un informe Markdown y un gráfico SVG sin dependencias.

## Cómo ejecutar

```bash
python energy_audit.py --demo
python energy_audit.py --input data/meter_15min.csv --out report.md
python energy_audit.py --json
python -m pytest -q
```

## Evidencia que produce

- `report.md` — informe con KPIs y recomendaciones.
- `load_profile.svg` — gráfico de la curva de carga.
- Pruebas en verde.

## Stack

Python 3 (biblioteca estándar). Sin dependencias externas.

## Por qué le importa a la empresa

Responde a **proyectos de eficiencia energética**: identificar el desperdicio,
cuantificarlo en dinero y proponer acciones medibles.
