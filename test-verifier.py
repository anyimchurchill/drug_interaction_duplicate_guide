import importlib.util
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
SOLUTION_FILE = ROOT_DIR / "solution" / "reference-solution.py"

spec = importlib.util.spec_from_file_location("reference_solution", SOLUTION_FILE)
if spec is None or spec.loader is None:
    raise ImportError(f"Could not load module from {SOLUTION_FILE}")

reference_solution = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = reference_solution
spec.loader.exec_module(reference_solution)

evaluate_active_med_list = reference_solution.evaluate_active_med_list


def run_tests() -> None:
    clean_alerts = evaluate_active_med_list(["Metformin", "Atorvastatin"])
    assert clean_alerts == [], f"Expected no alerts, got {clean_alerts}"

    complex_alerts = evaluate_active_med_list(
        ["Warfarin", "warfarin ", "Ibuprofen", "Naproxen"]
    )
    alert_types = {a.alert_type for a in complex_alerts}
    assert "DUPLICATE_DRUG" in alert_types
    assert "DUPLICATE_CLASS" in alert_types
    assert "DRUG_INTERACTION" in alert_types

    order_1 = evaluate_active_med_list(["Naproxen", "Warfarin", "Ibuprofen"])
    order_2 = evaluate_active_med_list(["Ibuprofen", "Warfarin", "Naproxen"])
    assert order_1 == order_2, "Alerts should be deterministic regardless of input order"

    try:
        evaluate_active_med_list(["   "])
        raise AssertionError("Expected ValueError for blank medication name")
    except ValueError:
        pass

    print("ALL VERIFIER CHECKS PASSED!")


if __name__ == "__main__":
    run_tests()
