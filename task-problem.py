from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GuardAlert:
    code: str
    severity: str
    drugs: tuple[str, ...]
    detail: str


CLASS_MAP: dict[str, str] = {
    "ibuprofen": "NSAID",
    "naproxen": "NSAID",
    "sertraline": "SSRI",
    "fluoxetine": "SSRI",
    "lisinopril": "ACE_INHIBITOR",
    "potassium chloride": "POTASSIUM_SUPPLEMENT",
}

PAIR_INTERACTIONS: dict[tuple[str, str], tuple[str, str]] = {
    ("ibuprofen", "warfarin"): ("HIGH", "Increased bleeding risk with concurrent NSAID and warfarin."),
    ("lisinopril", "potassium chloride"): ("HIGH", "Elevated risk of hyperkalemia."),
}


def clean_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Medication name must be a non-empty string.")
    return " ".join(name.strip().lower().split())


def check_med_list(medications: list[str]) -> list[GuardAlert]:
    cleaned = [clean_name(m) for m in medications]
    alerts: list[GuardAlert] = []

    # TODO 1: Flag exact duplicate medications (case-insensitive)
    # TODO 2: Flag multiple distinct drugs sharing the same therapeutic class in CLASS_MAP
    # TODO 3: Flag any unordered pair of distinct drugs present in PAIR_INTERACTIONS

    return alerts


if __name__ == "__main__":
    test_list = ["Warfarin", "Ibuprofen", "Naproxen", "warfarin"]
    print(check_med_list(test_list))
