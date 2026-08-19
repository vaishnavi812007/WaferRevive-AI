import os
import glob
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ============================================================
# WAFERREVIVE-AI
# STEP 33 - INSPECTION HISTORY & MULTI-WAFER TRACKING
# ============================================================

st.set_page_config(
    page_title="WaferRevive-AI - Inspection History",
    page_icon="📋",
    layout="wide"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE = r"D:\WaferRevive-AI"

RESULTS_DIR = os.path.join(
    BASE,
    "results",
    "full_inspection"
)

HISTORY_FILE = os.path.join(
    RESULTS_DIR,
    "inspection_history.csv"
)

os.makedirs(
    RESULTS_DIR,
    exist_ok=True
)


# ============================================================
# LOAD INSPECTION HISTORY
# ============================================================

def load_inspection_history():

    files = glob.glob(
        os.path.join(
            RESULTS_DIR,
            "*_inspection_summary.csv"
        )
    )

    records = []

    for file_path in files:

        try:

            df = pd.read_csv(
                file_path
            )

            if len(df) == 0:
                continue

            row = df.iloc[0]

            records.append({

                "Input":
                    str(
                        row.get(
                            "Input",
                            "Unknown"
                        )
                    ),

                "Decision":
                    str(
                        row.get(
                            "Decision",
                            "UNKNOWN"
                        )
                    ),

                "Total Defects":
                    int(
                        float(
                            row.get(
                                "Total_Defects",
                                0
                            )
                        )
                    ),

                "HIGH":
                    int(
                        float(
                            row.get(
                                "HIGH",
                                0
                            )
                        )
                    ),

                "MEDIUM":
                    int(
                        float(
                            row.get(
                                "MEDIUM",
                                0
                            )
                        )
                    ),

                "LOW":
                    int(
                        float(
                            row.get(
                                "LOW",
                                0
                            )
                        )
                    ),

                "Defect Area":
                    int(
                        float(
                            row.get(
                                "Defect_Area",
                                0
                            )
                        )
                    ),

                "Mean Residual":
                    float(
                        row.get(
                            "Mean_Residual",
                            0
                        )
                    ),

                "Maximum Residual":
                    float(
                        row.get(
                            "Maximum_Residual",
                            0
                        )
                    ),

                "Adaptive Threshold":
                    float(
                        row.get(
                            "Adaptive_Threshold",
                            0
                        )
                    ),

                "Initial Suspicious Pixels":
                    int(
                        float(
                            row.get(
                                "Initial_Suspicious_Pixels",
                                0
                            )
                        )
                    ),

                "Final Defect Pixels":
                    int(
                        float(
                            row.get(
                                "Final_Defect_Pixels",
                                0
                            )
                        )
                    ),

                "Suspicious Area %":
                    float(
                        row.get(
                            "Suspicious_Area_Percent",
                            0
                        )
                    ),

                "Source File":
                    os.path.basename(
                        file_path
                    )
            })

        except Exception as error:

            print(
                "Skipping:",
                file_path,
                error
            )

    if records:

        history = pd.DataFrame(
            records
        )

        history = history.sort_values(
            by="Input",
            ascending=True
        )

    else:

        history = pd.DataFrame(
            columns=[
                "Input",
                "Decision",
                "Total Defects",
                "HIGH",
                "MEDIUM",
                "LOW",
                "Defect Area",
                "Mean Residual",
                "Maximum Residual",
                "Adaptive Threshold",
                "Initial Suspicious Pixels",
                "Final Defect Pixels",
                "Suspicious Area %",
                "Source File"
            ]
        )

    return history


# ============================================================
# SAVE MASTER HISTORY
# ============================================================

def save_master_history(history):

    if len(history) == 0:

        return

    history.to_csv(
        HISTORY_FILE,
        index=False
    )


# ============================================================
# HEADER
# ============================================================

st.title(
    "📋 WaferRevive-AI"
)

st.subheader(
    "Inspection History & Multi-Wafer Tracking"
)

st.caption(
    "Track every wafer inspected by the AI system."
)


# ============================================================
# REFRESH BUTTON
# ============================================================

if st.button(
    "🔄 Refresh Inspection History"
):

    st.rerun()


# ============================================================
# LOAD HISTORY
# ============================================================

history = load_inspection_history()

save_master_history(
    history
)


# ============================================================
# NO DATA
# ============================================================

if len(history) == 0:

    st.warning(
        "No completed inspections found yet."
    )

    st.info(
        "Run Step 32 on one or more wafers, "
        "then return here and click Refresh."
    )

    st.stop()


# ============================================================
# SUMMARY STATISTICS
# ============================================================

total_wafers = len(
    history
)

defective_count = int(
    (
        history["Decision"]
        == "DEFECTIVE"
    ).sum()
)

review_count = int(
    (
        history["Decision"]
        == "REVIEW"
    ).sum()
)

acceptable_count = int(
    (
        history["Decision"]
        == "ACCEPTABLE"
    ).sum()
)

total_defects = int(
    history["Total Defects"].sum()
)

total_high = int(
    history["HIGH"].sum()
)

total_medium = int(
    history["MEDIUM"].sum()
)

total_low = int(
    history["LOW"].sum()
)

total_defect_area = int(
    history["Defect Area"].sum()
)


# ============================================================
# INSPECTION OVERVIEW
# ============================================================

st.divider()

st.header(
    "📊 Inspection Overview"
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:

    st.metric(
        "Wafers Inspected",
        total_wafers
    )

with c2:

    st.metric(
        "DEFECTIVE",
        defective_count
    )

with c3:

    st.metric(
        "REVIEW",
        review_count
    )

with c4:

    st.metric(
        "ACCEPTABLE",
        acceptable_count
    )

with c5:

    st.metric(
        "Total Defects",
        total_defects
    )


# ============================================================
# DEFECT SUMMARY
# ============================================================

st.divider()

st.header(
    "🚨 Defect Summary"
)

d1, d2, d3, d4 = st.columns(4)

with d1:

    st.metric(
        "HIGH",
        total_high
    )

with d2:

    st.metric(
        "MEDIUM",
        total_medium
    )

with d3:

    st.metric(
        "LOW",
        total_low
    )

with d4:

    st.metric(
        "Total Defect Area",
        "%d px" % total_defect_area
    )


# ============================================================
# SEARCH
# ============================================================

st.divider()

st.header(
    "🔎 Search & Filter"
)

search = st.text_input(
    "Search wafer name",
    placeholder="Example: 002850"
)

filtered = history.copy()

if search:

    filtered = filtered[
        filtered["Input"].str.contains(
            search,
            case=False,
            na=False
        )
    ]


# ============================================================
# DECISION FILTER
# ============================================================

decision_filter = st.selectbox(
    "Filter by decision",
    [
        "ALL",
        "DEFECTIVE",
        "REVIEW",
        "ACCEPTABLE"
    ]
)

if decision_filter != "ALL":

    filtered = filtered[
        filtered["Decision"]
        ==
        decision_filter
    ]


# ============================================================
# INSPECTION HISTORY TABLE
# ============================================================

st.divider()

st.header(
    "📋 Inspection History"
)

display_columns = [

    "Input",

    "Decision",

    "Total Defects",

    "HIGH",

    "MEDIUM",

    "LOW",

    "Defect Area",

    "Mean Residual",

    "Maximum Residual",

    "Adaptive Threshold",

    "Suspicious Area %"
]

st.dataframe(
    filtered[
        display_columns
    ],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# STATUS DISTRIBUTION
# ============================================================

st.divider()

st.header(
    "📈 Inspection Status Distribution"
)

status_counts = history[
    "Decision"
].value_counts()

fig1 = plt.figure(
    figsize=(8, 5)
)

plt.bar(
    status_counts.index,
    status_counts.values
)

plt.title(
    "Wafer Inspection Status"
)

plt.xlabel(
    "Decision"
)

plt.ylabel(
    "Number of Wafers"
)

plt.tight_layout()

st.pyplot(
    fig1
)

plt.close(
    fig1
)


# ============================================================
# DEFECT COUNT BY WAFER
# ============================================================

st.divider()

st.header(
    "📊 Defect Count by Wafer"
)

fig2 = plt.figure(
    figsize=(12, 5)
)

plt.bar(
    history["Input"],
    history["Total Defects"]
)

plt.title(
    "Total Defects per Inspected Wafer"
)

plt.xlabel(
    "Wafer"
)

plt.ylabel(
    "Total Defects"
)

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

st.pyplot(
    fig2
)

plt.close(
    fig2
)


# ============================================================
# RESIDUAL ANALYSIS
# ============================================================

st.divider()

st.header(
    "📉 Residual Analysis"
)

fig3 = plt.figure(
    figsize=(12, 5)
)

plt.plot(
    history["Input"],
    history["Mean Residual"],
    marker="o",
    label="Mean Residual"
)

plt.plot(
    history["Input"],
    history["Maximum Residual"],
    marker="o",
    label="Maximum Residual"
)

plt.title(
    "Residual Measurements Across Wafers"
)

plt.xlabel(
    "Wafer"
)

plt.ylabel(
    "Residual"
)

plt.xticks(
    rotation=45,
    ha="right"
)

plt.legend()

plt.tight_layout()

st.pyplot(
    fig3
)

plt.close(
    fig3
)


# ============================================================
# ADAPTIVE THRESHOLD ANALYSIS
# ============================================================

st.divider()

st.header(
    "🎯 Adaptive Threshold by Wafer"
)

fig4 = plt.figure(
    figsize=(12, 5)
)

plt.plot(
    history["Input"],
    history["Adaptive Threshold"],
    marker="o"
)

plt.title(
    "Adaptive Detection Threshold"
)

plt.xlabel(
    "Wafer"
)

plt.ylabel(
    "Threshold"
)

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

st.pyplot(
    fig4
)

plt.close(
    fig4
)


# ============================================================
# HIGHEST DEFECT WAFER
# ============================================================

st.divider()

st.header(
    "🏆 Highest Defect Wafer"
)

highest_index = history[
    "Total Defects"
].idxmax()

highest = history.loc[
    highest_index
]

h1, h2, h3, h4 = st.columns(4)

with h1:

    st.write(
        "**Wafer**"
    )

    st.write(
        highest["Input"]
    )

with h2:

    st.write(
        "**Decision**"
    )

    st.write(
        highest["Decision"]
    )

with h3:

    st.write(
        "**Total Defects**"
    )

    st.write(
        int(
            highest["Total Defects"]
        )
    )

with h4:

    st.write(
        "**HIGH Defects**"
    )

    st.write(
        int(
            highest["HIGH"]
        )
    )


# ============================================================
# HIGHEST DEFECT AREA
# ============================================================

highest_area_index = history[
    "Defect Area"
].idxmax()

highest_area = history.loc[
    highest_area_index
]

st.info(
    "Largest defect area: %s — %d pixels"
    % (
        highest_area["Input"],
        int(
            highest_area["Defect Area"]
        )
    )
)


# ============================================================
# EXPORT
# ============================================================

st.divider()

st.header(
    "💾 History Export"
)

st.write(
    "Master inspection history:"
)

st.code(
    HISTORY_FILE
)

with open(
    HISTORY_FILE,
    "rb"
) as file:

    st.download_button(
        label="⬇️ Download Inspection History CSV",
        data=file,
        file_name="inspection_history.csv",
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.success(
    "✅ STEP 33 COMPLETED SUCCESSFULLY"
)

st.caption(
    "WaferRevive-AI — Multi-Wafer Inspection History"
)