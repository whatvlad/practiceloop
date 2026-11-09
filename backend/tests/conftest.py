from seed_sweep import seed_cap


def pytest_report_header() -> str:
    cap = seed_cap()
    if cap is None:
        return "generator seed sweeps: full (CI)"
    hint = "set MATHLOOP_SEEDS=1000 for the full CI sweep"
    return f"generator seed sweeps: capped at {cap} ({hint})"
