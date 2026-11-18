import importlib.util
from pathlib import Path
import sys
import streamlit as st

st.set_page_config(
    page_title="Drug Interaction & Duplicate Therapy Guard",
    page_icon="💊",
    layout="centered",
)

ROOT_DIR = Path(__file__).resolve().parent
SOLUTION_FILE = ROOT_DIR / "solution" / "reference-solution.py"


@st.cache_resource
def load_guard_module():
    spec = importlib.util.spec_from_file_location("reference_solution", SOLUTION_FILE)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {SOLUTION_FILE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


guard = load_guard_module()

st.title("Drug Interaction & Duplicate Therapy Guard")
st.caption(
    "Deterministic medication safety & rule-validation prototype checking active lists "
    "for exact duplicates, same-class therapy overlap, and known drug-drug interactions."
)

if "med_input" not in st.session_state:
    st.session_state.med_input = (
        "Warfarin\nIbuprofen\nNaproxen\nwarfarin\nLisinopril\nPotassium Chloride"
    )

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Load High-Risk Example", use_container_width=True):
        st.session_state.med_input = (
            "Warfarin\nIbuprofen\nNaproxen\nwarfarin\nLisinopril\nPotassium Chloride"
        )
        st.rerun()
with col2:
    if st.button("Load Clean List Example", use_container_width=True):
        st.session_state.med_input = "Metformin\nAtorvastatin\nRamipril"
        st.rerun()
with col3:
    if st.button("Clear List", use_container_width=True):
        st.session_state.med_input = ""
        st.rerun()

raw_text = st.text_area(
    "Active Medication List (one medication per line)",
    key="med_input",
    height=170,
    placeholder="e.g.\nWarfarin\nIbuprofen\nNaproxen",
)

med_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

if st.button("Run Safety & Rule Check", type="primary", use_container_width=True):
    if not med_lines:
        st.warning("Please enter at least one medication name to run the check.")
    else:
        try:
            alerts = guard.evaluate_active_med_list(med_lines)
            records = guard.build_med_records(med_lines)

            st.subheader("Normalized Active Medications")
            st.dataframe(
                [
                    {
                        "Normalized Name": r.name,
                        "Therapeutic Class": r.therapeutic_class,
                    }
                    for r in records
                ],
                use_container_width=True,
                hide_index=True,
            )

            st.subheader(f"Alerts Detected ({len(alerts)})")
            if not alerts:
                st.success("No duplicate therapies or known drug-drug interactions flagged.")
            else:
                for alert in alerts:
                    meds_display = ", ".join(alert.medications)
                    header = f"**[{alert.severity}] {alert.alert_type}** — `{meds_display}`"
                    if alert.severity == "HIGH":
                        st.error(f"{header}\n\n{alert.message}")
                    else:
                        st.warning(f"{header}\n\n{alert.message}")
        except ValueError as exc:
            st.error(f"Input validation error: {exc}")

with st.expander("Supported Demo Medications & Rules"):
    st.write(
        "Known classes include NSAIDs (`ibuprofen`, `naproxen`, `diclofenac`, `celecoxib`), "
        "SSRIs (`sertraline`, `fluoxetine`, `escitalopram`), ACE inhibitors (`lisinopril`, `ramipril`), "
        "ARBs (`losartan`), K-sparing diuretics (`spironolactone`), anticoagulants (`warfarin`), "
        "antiplatelets (`clopidogrel`), statins (`simvastatin`, `atorvastatin`), and potassium supplements."
    )
