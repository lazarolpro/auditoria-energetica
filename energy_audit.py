#!/usr/bin/env python3
"""Auditoria energetica sobre datos de medidor (intervalos de 15 minutos).

Capacidad 6 - Eficiencia energetica.

Ingiere la curva de carga de un medidor trifasico, calcula los indicadores que
mira una auditoria (consumo, carga base, demanda punta, factor de carga, consumo
fuera de horario), detecta desperdicio y estima el ahorro potencial. Genera un
informe Markdown y un grafico SVG sin dependencias externas.

Uso:
    python energy_audit.py --demo
    python energy_audit.py --input data/meter_15min.csv --out report.md

Solo biblioteca estandar de Python 3.
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

INTERVAL_H = 0.25          # 15 minutos
WORK_START, WORK_END = 8, 18
BASE_LOAD_KW = 18.0        # consumo nocturno minimo (kW)
TARIFF_USD_KWH = 0.15      # tarifa media para valorar el ahorro


def make_sample(path: Path, days: int = 7, seed: int = 21) -> None:
    rng = random.Random(seed)
    start = datetime(2026, 5, 4, 0, 0, 0)
    rows = []
    steps = int(days * 24 / INTERVAL_H)
    for i in range(steps):
        ts = start + timedelta(hours=i * INTERVAL_H)
        hour = ts.hour
        if WORK_START <= hour < WORK_END:
            load = 58 + rng.uniform(-6, 6)
        else:
            # Fuga: la linea 3 queda energizada de noche (desperdicio).
            load = BASE_LOAD_KW + rng.uniform(-1, 1)
            if hour in (22, 23, 0, 1, 2):
                load += 14 + rng.uniform(-1, 1)
        rows.append({"timestamp": ts.isoformat(timespec="minutes"),
                     "power_kw": f"{max(load, 0):.2f}"})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["timestamp", "power_kw"])
        writer.writeheader()
        writer.writerows(rows)


def load_rows(path: Path) -> list[tuple[datetime, float]]:
    rows = []
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                rows.append((datetime.fromisoformat(row["timestamp"]),
                             float(row["power_kw"])))
            except (ValueError, KeyError):
                continue
    return rows


def analyze(rows: list[tuple[datetime, float]]) -> dict:
    if not rows:
        return {}
    energy = sum(p * INTERVAL_H for _, p in rows)
    powers = [p for _, p in rows]
    peak = max(powers)
    base = min(powers)
    avg = energy / (len(rows) * INTERVAL_H)
    load_factor = avg / peak if peak else 0
    daily: dict[str, float] = defaultdict(float)
    off_hours_energy = 0.0
    for ts, p in rows:
        daily[ts.date().isoformat()] += p * INTERVAL_H
        if not (WORK_START <= ts.hour < WORK_END):
            off_hours_energy += p * INTERVAL_H
    # Desperdicio = energia fuera de horario por encima de la carga base.
    base_off = BASE_LOAD_KW * sum(1 for ts, _ in rows if not (WORK_START <= ts.hour < WORK_END)) * INTERVAL_H
    waste = max(off_hours_energy - base_off, 0.0)
    return {
        "energy_kwh": round(energy, 1),
        "peak_kw": round(peak, 1),
        "base_kw": round(base, 1),
        "avg_kw": round(avg, 1),
        "load_factor": round(load_factor, 3),
        "off_hours_kwh": round(off_hours_energy, 1),
        "waste_kwh": round(waste, 1),
        "waste_usd": round(waste * TARIFF_USD_KWH, 2),
        "days": len(daily),
        "daily_kwh": {d: round(v, 1) for d, v in sorted(daily.items())},
    }


def render_svg(rows: list[tuple[datetime, float]], path: Path) -> None:
    w, h, pad = 900, 260, 30
    max_p = max((p for _, p in rows), default=1) or 1
    n = len(rows)
    pts = []
    for i, (_, p) in enumerate(rows):
        x = pad + (w - 2 * pad) * i / max(n - 1, 1)
        y = h - pad - (h - 2 * pad) * p / max_p
        pts.append(f"{x:.1f},{y:.1f}")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="sans-serif">\n'
        f'  <rect width="{w}" height="{h}" fill="#0d1117"/>\n'
        f'  <text x="{pad}" y="18" fill="#7ee787" font-size="13">'
        f'Curva de carga (kW) — pico {max_p:.0f} kW</text>\n'
        f'  <polyline fill="none" stroke="#58a6ff" stroke-width="1.5" points="{" ".join(pts)}"/>\n'
        f'  <line x1="{pad}" y1="{h - pad}" x2="{w - pad}" y2="{h - pad}" stroke="#30363d"/>\n'
        f'</svg>\n'
    )
    path.write_text(svg, encoding="utf-8")


def render_report(a: dict) -> str:
    lines = [
        "# Auditoria energetica",
        "",
        f"- Dias analizados: **{a['days']}**",
        f"- Consumo total: **{a['energy_kwh']} kWh**",
        f"- Demanda punta: **{a['peak_kw']} kW**",
        f"- Carga base (minimo): **{a['base_kw']} kW**",
        f"- Carga media: **{a['avg_kw']} kW**",
        f"- Factor de carga: **{a['load_factor']}**",
        f"- Consumo fuera de horario: **{a['off_hours_kwh']} kWh**",
        f"- Desperdicio estimado: **{a['waste_kwh']} kWh** (~{a['waste_usd']} USD)",
        "",
        "## Consumo diario (kWh)",
        "",
        "| Dia | kWh |",
        "| --- | --- |",
    ]
    for day, value in a["daily_kwh"].items():
        lines.append(f"| {day} | {value} |")
    lines += [
        "",
        "## Recomendaciones",
        "",
        "1. Programar la desconexion de la linea ociosa en horario nocturno.",
        "2. Instalar temporizadores o sensores de presencia en zonas de baja ocupacion.",
        "3. Revisar la correccion del factor de potencia si se factura reactiva.",
        "4. Verificar la curva contra la produccion para separar carga util de fuga.",
        "",
        "> Grafico: `load_profile.svg`. Evidencia reproducible: `python energy_audit.py --demo`.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Auditoria energetica de un medidor")
    parser.add_argument("--input", type=Path, default=Path("data/meter_15min.csv"))
    parser.add_argument("--out", type=Path, default=Path("report.md"))
    parser.add_argument("--svg", type=Path, default=Path("load_profile.svg"))
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.demo:
        make_sample(args.input)
        print(f"[ok] datos de ejemplo en {args.input}")

    rows = load_rows(args.input)
    a = analyze(rows)

    if args.json:
        import json
        print(json.dumps(a, ensure_ascii=False, indent=2))
        return 0

    render_svg(rows, args.svg)
    args.out.write_text(render_report(a), encoding="utf-8")
    print(f"[ok] consumo {a['energy_kwh']} kWh, desperdicio {a['waste_kwh']} kWh "
          f"(~{a['waste_usd']} USD) -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
