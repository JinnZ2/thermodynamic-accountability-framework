# app.py
"""
Bias Autopsy Lab – Streamlit Interface
Extended with Sensitivity Analysis to quantify assumption impact.
"""

import streamlit as st
import pandas as pd
import numpy as np
from bias_analyzer import BiasDetectionPipeline
from sensitivity_analyzer import SensitivityIntegrator

# ------------------------------ Initialization ------------------------------
@st.cache_resource
def load_pipeline():
    return BiasDetectionPipeline("bias_dictionary.json")

pipeline = load_pipeline()

st.set_page_config(page_title="Bias Autopsy Lab", layout="wide")
st.title("🧬 Bias Autopsy Lab")
st.markdown(
    "**Detect assumption‑based bias in scientific claims, then quantify "
    "how much those assumptions distort a quantitative model.**"
)

# ------------------------------ Sidebar Settings ------------------------------
with st.sidebar:
    st.header("Detection Settings")
    threshold = st.slider(
        "Semantic similarity threshold",
        min_value=0.3, max_value=0.9, value=0.55,
        help="Higher = stricter matching. 0.55 works well for most texts."
    )
    st.markdown("---")
    st.info(
        "The pipeline combines semantic bias matching, structural pattern "
        "checks, recursive falsification analysis, and optional institutional "
        "context flags."
    )

# ------------------------------ Main Input Form ------------------------------
with st.form("input_form"):
    st.subheader("📝 Enter Text & Metadata")
    text = st.text_area(
        "Paste a paragraph containing a hypothesis and (optionally) its falsification condition:",
        height=200,
        value=(
            "We hypothesize that the Ross Ice Shelf will inevitably collapse "
            "by 2100, driving at least 1 meter of sea‑level rise. The latest "
            "models show this is an unavoidable tipping point. We would falsify "
            "this if the shelf stabilizes or sea‑level rise stays below 50 cm "
            "— but that seems unlikely given current trends."
        ),
        help="The system will automatically extract the hypothesis and falsification."
    )
    with st.expander("Optional: Institutional Metadata"):
        funding = st.text_input("Funding source", "")
        journal = st.text_input("Journal", "")
        career_stage = st.selectbox(
            "Lead author career stage", ["", "early", "mid", "senior"]
        )
    submitted = st.form_submit_button("🔍 Run Bias Autopsy")

# ------------------------------ Run Analysis ------------------------------
if submitted and text.strip():
    metadata = {}
    if funding: metadata['funding'] = funding
    if journal: metadata['journal'] = journal
    if career_stage: metadata['career_stage'] = career_stage

    with st.spinner("Running recursive bias analysis..."):
        result = pipeline.run(
            text,
            metadata=metadata,
            semantic_threshold=threshold
        )

    claim = result['claim_analysis']
    context = result.get('context_analysis', {})

    # ---- Scores ----
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Claim Bias Score", f"{claim['claim_bias_score']:.2f}")
    with col2:
        fals_score = (
            claim.get('falsification_analysis', {}).get('score', 0)
            if claim.get('falsification_analysis') else 0
        )
        st.metric("Falsification Bias Score", f"{fals_score:.2f}")
    with col3:
        inst_score = context.get('institutional_bias_score', 0) if context else 0
        st.metric("Institutional Bias Score", f"{inst_score:.2f}")
    with col4:
        combined = claim['claim_bias_score'] + inst_score
        st.metric("Combined Bias Score", f"{combined:.2f}",
                  delta_color="inverse")

    # ---- Detected Biases in Hypothesis ----
    st.header("🔎 Biases Detected in Hypothesis")
    if claim.get('biases'):
        for b in claim['biases']:
            with st.expander(
                f"🚩 {b['bias_name']} (severity: {b.get('severity','N/A')})"
            ):
                st.write(f"**Trigger sentence**: {b.get('sentence', '')}")
                if 'similarity' in b:
                    st.write(f"Semantic similarity: {b['similarity']:.2f}")
                st.write(f"**Counter‑question**: {b.get('counter_question', '')}")
                if 'suggestion' in b:
                    st.write(f"**Suggestion**: {b['suggestion']}")
    else:
        st.success("No major semantic or structural biases detected in hypothesis.")

    # ---- Recursive Falsification Analysis ----
    if claim.get('falsification_analysis'):
        st.header("🔄 Recursive Falsification Analysis")
        f_analysis = claim['falsification_analysis']
        st.write(f"Falsification text: *{f_analysis['text']}*")
        if f_analysis.get('biases'):
            for b in f_analysis['biases']:
                st.markdown(
                    f"- **{b['bias_name']}** ({b.get('severity','N/A')}): "
                    f"{b.get('counter_question', b.get('suggestion',''))}"
                )
        else:
            st.success("Falsification condition appears structurally sound.")

    # ---- Institutional Context Flags ----
    if context and context.get('flags'):
        st.header("🏛️ Institutional Context Flags")
        for flag in context['flags']:
            st.warning(f"**{flag['bias_id']}**: {flag['reason']}")

    # ---- Iterative Refinement (Optional) ----
    st.markdown("---")
    with st.expander("✏️ Refine Your Hypothesis"):
        new_hypothesis = st.text_area(
            "Edit hypothesis:", value=claim['hypothesis'], height=80
        )
        fals_text = claim.get('falsification', '')
        new_falsification = st.text_area(
            "Edit falsification:", value=fals_text, height=80
        )
        if st.button("Re‑analyze with edits"):
            new_text = f"{new_hypothesis} {new_falsification}"
            st.session_state['reanalyze_text'] = new_text
            st.experimental_rerun()

    # ---- Sensitivity Analysis (Quantitative) ----
    st.markdown("---")
    st.header("📊 Sensitivity Analysis: Quantify Bias Impact on Model")
    st.markdown(
        "Upload a dataset and map the bias‑flagged variables to columns. "
        "The tool trains a baseline model (all variables) and a clean model "
        "(assumption variables removed) and measures the prediction drift."
    )
    with st.expander("Upload Dataset & Configure"):
        uploaded_file = st.file_uploader(
            "Upload CSV file (numeric features + target column)", type=["csv"]
        )
        if uploaded_file is not None:
            df_sens = pd.read_csv(uploaded_file)
            st.write("Data preview:", df_sens.head())
            target_col = st.selectbox("Select target column", df_sens.columns)
            numeric_cols = df_sens.select_dtypes(include=np.number).columns.tolist()
            # Pre-select variables whose names appear in detected biases
            bias_names = [b['bias_name'] for b in claim.get('biases', [])]
            # Simple heuristic: if a column name contains a word from a bias name,
            # mark it as suspicious (user can adjust)
            default_assumption = []
            for col in numeric_cols:
                for bias in bias_names:
                    # crude: check if any word of bias name appears in column name
                    if any(word.lower() in col.lower() for word in bias.split()):
                        default_assumption.append(col)
                        break
            assumption_cols = st.multiselect(
                "Columns that are assumption‑laden (use bias report above as guide)",
                numeric_cols,
                default=list(set(default_assumption))
            )
            if st.button("Run Sensitivity Analysis"):
                if not assumption_cols or not target_col:
                    st.error("Please select at least one assumption column and a target.")
                else:
                    control_cols = [c for c in numeric_cols
                                    if c not in assumption_cols and c != target_col]
                    integrator = SensitivityIntegrator(
                        df_sens, target_col, assumption_cols, control_cols
                    )
                    with st.spinner("Fitting models and computing drift..."):
                        report = integrator.sensitivity_report()
                    st.subheader("Sensitivity Report")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Prediction Drift (mean abs.)",
                                  f"{report['prediction_drift_mean']:.3f}")
                    with c2:
                        st.metric("Drift (% of target mean)",
                                  f"{report['drift_percent']:.2f}%")
                    with c3:
                        st.metric(
                            "MSE baseline / clean",
                            f"{report['baseline_mse']:.3f} / {report['clean_mse']:.3f}"
                        )
                    st.subheader("Feature Importance Shift")
                    imp_df = pd.DataFrame({
                        'Baseline Coef': report['feature_importance_shift']['baseline'],
                        'Clean Coef': report['feature_importance_shift']['clean']
                    }).fillna(0)
                    st.dataframe(imp_df.style.background_gradient(axis=0))
                    st.subheader("Prediction Drift Visualization")
                    fig = integrator.plot_prediction_drift()
                    st.pyplot(fig)

# ------------------------------ Handle Re-analysis ------------------------------
if 'reanalyze_text' in st.session_state and st.session_state.reanalyze_text:
    # In a full app you'd use a callback; here we simply show a button to rerun
    st.info("Click 'Run Bias Autopsy' again with the new text.")
    st.session_state.reanalyze_text = ''  # reset after notice
