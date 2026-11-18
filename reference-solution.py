from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class MedicationRecord:
    name: str
    therapeutic_class: str


@dataclass(frozen=True)
class Alert:
    alert_type: str
    severity: str
    medications: tuple[str, ...]
    message: str


DRUG_CLASSES: dict[str, str] = {
    "ibuprofen": "NSAID",
    "naproxen": "NSAID",
    "diclofenac": "NSAID",
    "celecoxib": "NSAID",
    "sertraline": "SSRI",
    "fluoxetine": "SSRI",
    "escitalopram": "SSRI",
    "lisinopril": "ACE_INHIBITOR",
    "ramipril": "ACE_INHIBITOR",
    "losartan": "ARB",
    "spironolactone": "K_SPARING_DIURETIC",
    "warfarin": "ANTICOAGULANT",
    "clopidogrel": "ANTIPLATELET",
    "simvastatin": "STATIN",
    "atorvastatin": "STATIN",
    "clarithromycin": "MACROLIDE_CYP3A4",
    "metformin": "BIGUANIDE",
    "potassium chloride": "POTASSIUM_SUPPLEMENT",
}

INTERACTION_RULES: dict[tuple[str, str], tuple[str, str]] = {
    ("ibuprofen", "warfarin"): (
        "HIGH",
        "Concurrent NSAID and warfarin increases gastrointestinal bleeding risk.",
    ),
    ("naproxen", "warfarin"): (
        "HIGH",
        "Concurrent NSAID and warfarin increases bleeding risk.",
    ),
    ("diclofenac", "warfarin"): (
        "HIGH",
        "Concurrent NSAID and warfarin increases bleeding risk.",
    ),
    ("clopidogrel", "ibuprofen"): (
        "MODERATE",
        "Ibuprofen may blunt the antiplatelet effect of clopidogrel and raise GI bleed risk.",
    ),
    ("lisinopril", "potassium chloride"): (
        "HIGH",
        "ACE inhibitor plus potassium supplement increases risk of hyperkalemia.",
    ),
    ("potassium chloride", "spironolactone"): (
        "HIGH",
        "Potassium-sparing diuretic plus potassium supplement increases hyperkalemia risk.",
    ),
    ("clarithromycin", "simvastatin"): (
        "HIGH",
        "Clarithromycin inhibits CYP3A4 metabolism of simvastatin, raising myopathy/rhabdomyolysis risk.",
    ),
    ("atorvastatin", "clarithromycin"): (
        "MODERATE",
        "Clarithromycin may increase atorvastatin exposure; monitor for muscle symptoms.",
    ),
}

SEVERITY_RANK = {"HIGH": 0, "MODERATE": 1}


def normalize_med_name(raw_name: str) -> str:
    if not isinstance(raw_name, str) or not raw_name.strip():
        raise ValueError("Medication name must be a non-empty string.")
    return " ".join(raw_name.strip().lower().split())


def build_med_records(
    active_meds: Iterable[str],
    custom_classes: dict[str, str] | None = None,
) -> list[MedicationRecord]:
    class_map = dict(DRUG_CLASSES)
    if custom_classes:
        for k, v in custom_classes.items():
            class_map[normalize_med_name(k)] = v.strip().upper()

    records: list[MedicationRecord] = []
    for med in active_meds:
        norm = normalize_med_name(med)
        med_class = class_map.get(norm, "UNCLASSIFIED")
        records.append(MedicationRecord(name=norm, therapeutic_class=med_class))
    return records


def evaluate_active_med_list(
    active_meds: Iterable[str],
    custom_classes: dict[str, str] | None = None,
    custom_interactions: dict[tuple[str, str], tuple[str, str]] | None = None,
) -> list[Alert]:
    records = build_med_records(active_meds, custom_classes=custom_classes)
    alerts: list[Alert] = []

    seen_counts: dict[str, int] = {}
    for rec in records:
        seen_counts[rec.name] = seen_counts.get(rec.name, 0) + 1

    for med_name, count in sorted(seen_counts.items()):
        if count > 1:
            alerts.append(
                Alert(
                    alert_type="DUPLICATE_DRUG",
                    severity="HIGH",
                    medications=(med_name,),
                    message=f"Duplicate active medication detected: '{med_name}' appears {count} times.",
                )
            )

    class_to_unique_meds: dict[str, list[str]] = {}
    for rec in records:
        if rec.therapeutic_class == "UNCLASSIFIED":
            continue
        bucket = class_to_unique_meds.setdefault(rec.therapeutic_class, [])
        if rec.name not in bucket:
            bucket.append(rec.name)

    for med_class, meds_in_class in sorted(class_to_unique_meds.items()):
        if len(meds_in_class) > 1:
            sorted_meds = tuple(sorted(meds_in_class))
            alerts.append(
                Alert(
                    alert_type="DUPLICATE_CLASS",
                    severity="MODERATE",
                    medications=sorted_meds,
                    message=(
                        f"Duplicate therapy in class '{med_class}': "
                        f"{', '.join(sorted_meds)} are all on the active list."
                    ),
                )
            )

    rules = dict(INTERACTION_RULES)
    if custom_interactions:
        for (a, b), rule in custom_interactions.items():
            pair = tuple(sorted((normalize_med_name(a), normalize_med_name(b))))
            rules[pair] = rule

    unique_meds = sorted({rec.name for rec in records})
    for i in range(len(unique_meds)):
        for j in range(i + 1, len(unique_meds)):
            pair = (unique_meds[i], unique_meds[j])
            if pair in rules:
                severity, rationale = rules[pair]
                alerts.append(
                    Alert(
                        alert_type="DRUG_INTERACTION",
                        severity=severity,
                        medications=pair,
                        message=f"Interaction between {pair[0]} and {pair[1]}: {rationale}",
                    )
                )

    alerts.sort(
        key=lambda a: (
            SEVERITY_RANK.get(a.severity, 99),
            a.alert_type,
            a.medications,
        )
    )
    return alerts


if __name__ == "__main__":
    sample_med_list = [
        "Warfarin",
        "Ibuprofen",
        "Naproxen",
        "warfarin ",
        "Lisinopril",
        "Potassium Chloride",
    ]
    found_alerts = evaluate_active_med_list(sample_med_list)
    print(f"Total alerts found: {len(found_alerts)}")
    for alert in found_alerts:
        print(f"[{alert.severity}] ({alert.alert_type}) {alert.medications} -> {alert.message}")
