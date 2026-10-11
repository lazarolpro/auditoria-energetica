# Auditoria energetica

- Dias analizados: **7**
- Consumo total: **6296.2 kWh**
- Demanda punta: **63.9 kW**
- Carga base (minimo): **17.0 kW**
- Carga media: **37.5 kW**
- Factor de carga: **0.586**
- Consumo fuera de horario: **2257.1 kWh**
- Desperdicio estimado: **493.1 kWh** (~73.96 USD)

## Consumo diario (kWh)

| Dia | kWh |
| --- | --- |
| 2026-05-04 | 903.7 |
| 2026-05-05 | 901.1 |
| 2026-05-06 | 896.5 |
| 2026-05-07 | 901.4 |
| 2026-05-08 | 889.3 |
| 2026-05-09 | 904.2 |
| 2026-05-10 | 900.0 |

## Recomendaciones

1. Programar la desconexion de la linea ociosa en horario nocturno.
2. Instalar temporizadores o sensores de presencia en zonas de baja ocupacion.
3. Revisar la correccion del factor de potencia si se factura reactiva.
4. Verificar la curva contra la produccion para separar carga util de fuga.

> Grafico: `load_profile.svg`. Evidencia reproducible: `python energy_audit.py --demo`.
