import importlib.util
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("energy", ROOT / "energy_audit.py")
energy = importlib.util.module_from_spec(spec)
sys.modules["energy"] = energy
spec.loader.exec_module(energy)


def _flat_rows(power: float, hours: int = 24):
    start = datetime(2026, 5, 4)
    return [(start + timedelta(hours=i * 0.25), power) for i in range(int(hours / 0.25))]


def test_energy_and_load_factor_flat_load():
    a = energy.analyze(_flat_rows(40.0))
    assert a["energy_kwh"] == 40.0 * 24
    assert a["peak_kw"] == 40.0
    assert a["load_factor"] == 1.0


def test_detects_off_hours_waste():
    start = datetime(2026, 5, 4)
    rows = []
    for i in range(96):
        ts = start + timedelta(hours=i * 0.25)
        rows.append((ts, 60.0 if 8 <= ts.hour < 18 else 35.0))
    a = energy.analyze(rows)
    assert a["waste_kwh"] > 0
    assert a["off_hours_kwh"] > 0


def test_empty_input_is_safe():
    assert energy.analyze([]) == {}
