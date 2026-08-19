import os
import csv
from datetime import datetime

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ============================================================
# WAFERREVIVE-AI
# STEP 36 - BATCH REPORT & EXPORT
# ============================================================

st.set_page_config(
    page_title="WaferRevive-AI - Batch Report",
    page_icon="📋",
    layout="wide"
)


# ============================================================
# PATHS
# ============================================================

BASE = r"D:\WaferRevive-AI"

BATCH_DIR = os.path.join(
    BASE,
    "results",
    "batch_inspection"
)

REPORT_DIR = os.path.join(
    BASE,
    "results",
    "batch_reports"
)

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)


# ============================================================
# HEADER
# ============================================================

st.title("🔬 WaferRevive-AI")

st.subheader(
    "Step 36 — Batch Report & Export"
)

st.caption(
    "Professional reporting and export of "
    "WaferRevive-AI batch inspection results."
)


# ============================================================
# FIND BATCH CSV
# ============================================================

csv_path = os.path.join(
    BATCH_DIR,
    "batch_inspection_results.csv"
)


if not os.path.exists(csv_path):

    st.warning(
        "No Step 35 batch results were found."
    )

    st.write(
        "Run Step 35 batch inspection first."
    )

    st.code(
        "python -m streamlit run step35_batch_inspection.py"
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

try:

    df = pd.read_csv(
        csv_path
    )

except Exception as error:

    st.error(
        "Could not load the batch results."
    )

    st.exception(
        error
    )

    st.stop()


if df.empty:

    st.warning(
        "The batch results file contains no records."
    )

    st.stop()


# ============================================================
# NORMALIZE NUMERIC COLUMNS
# ============================================================

numeric_columns = [

    "Total_Defects",

    "HIGH",

    "MEDIUM",

    "LOW",

    "Defect_Area",

    "Mean_Residual",

    "Maximum_Residual",

    "Adaptive_Threshold",

    "Final_Defect_Pixels",

    "Suspicious_Area_Percent"
]


for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)


# ============================================================
# BATCH STATISTICS
# ============================================================

total_wafers = len(df)

defective_count = int(
    (
        df["Decision"]
        ==
        "DEFECTIVE"
    ).sum()
)

review_count = int(
    (
        df["Decision"]
        ==
        "REVIEW"
    ).sum()
)

acceptable_count = int(
    (
        df["Decision"]
        ==
        "ACCEPTABLE"
    ).sum()
)

total_defects = int(
    df["Total_Defects"].sum()
)

total_high = int(
    df["HIGH"].sum()
)

total_medium = int(
    df["MEDIUM"].sum()
)

total_low = int(
    df["LOW"].sum()
)

total_area = int(
    df["Defect_Area"].sum()
)

average_residual = float(
    df["Mean_Residual"].mean()
)

maximum_residual = float(
    df["Maximum_Residual"].max()
)

average_suspicious_area = float(
    df["Suspicious_Area_Percent"].mean()
)

maximum_suspicious_area = float(
    df["Suspicious_Area_Percent"].max()
)


# ============================================================
# OVERALL STATUS
# ============================================================

if defective_count > 0:

    overall_status = "DEFECTIVE"

elif review_count > 0:

    overall_status = "REVIEW"

else:

    overall_status = "ACCEPTABLE"


if overall_status == "DEFECTIVE":

    status_reason = (
        "One or more wafers contain "
        "HIGH severity defects."
    )

elif overall_status == "REVIEW":

    status_reason = (
        "One or more wafers require "
        "additional inspection."
    )

else:

    status_reason = (
        "No wafer requires immediate "
        "defect rejection."
    )


# ============================================================
# REPORT TITLE
# ============================================================

st.divider()

st.header(
    "📋 Batch Inspection Report"
)

st.write(
    "**Generated:** "
    +
    datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
)

st.write(
    "**Source:** Step 35 Batch Inspection"
)


# ============================================================
# OVERALL STATUS
# ============================================================

st.divider()

st.header(
    "🚦 Overall Batch Status"
)

if overall_status == "DEFECTIVE":

    st.error(
        "🔴 BATCH STATUS: DEFECTIVE"
    )

elif overall_status == "REVIEW":

    st.warning(
        "🟡 BATCH STATUS: REVIEW"
    )

else:

    st.success(
        "🟢 BATCH STATUS: ACCEPTABLE"
    )

st.write(
    status_reason
)


# ============================================================
# MAIN METRICS
# ============================================================

st.subheader(
    "Batch Statistics"
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:

    st.metric(
        "Wafers",
        total_wafers
    )

with c2:

    st.metric(
        "Defective",
        defective_count
    )

with c3:

    st.metric(
        "Review",
        review_count
    )

with c4:

    st.metric(
        "Acceptable",
        acceptable_count
    )

with c5:

    st.metric(
        "Total Defects",
        total_defects
    )


# ============================================================
# SEVERITY
# ============================================================

st.subheader(
    "Defect Severity"
)

s1, s2, s3, s4 = st.columns(4)

with s1:

    st.metric(
        "HIGH",
        total_high
    )

with s2:

    st.metric(
        "MEDIUM",
        total_medium
    )

with s3:

    st.metric(
        "LOW",
        total_low
    )

with s4:

    st.metric(
        "Total Area",
        "%d pixels"
        %
        total_area
    )


# ============================================================
# QUALITY STATISTICS
# ============================================================

st.subheader(
    "Residual / Quality Statistics"
)

q1, q2, q3, q4 = st.columns(4)

with q1:

    st.metric(
        "Average Residual",
        "%.6f"
        %
        average_residual
    )

with q2:

    st.metric(
        "Maximum Residual",
        "%.6f"
        %
        maximum_residual
    )

with q3:

    st.metric(
        "Avg Suspicious Area",
        "%.3f%%"
        %
        average_suspicious_area
    )

with q4:

    st.metric(
        "Max Suspicious Area",
        "%.3f%%"
        %
        maximum_suspicious_area
    )


# ============================================================
# RESULTS TABLE
# ============================================================

st.divider()

st.header(
    "📊 Complete Batch Results"
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DEFECTIVE WAFERS
# ============================================================

st.divider()

st.header(
    "🔴 Defective Wafers"
)

defective_df = df[
    df["Decision"] == "DEFECTIVE"
].copy()


if defective_df.empty:

    st.success(
        "No defective wafers were detected."
    )

else:

    st.dataframe(
        defective_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# REVIEW WAFERS
# ============================================================

st.header(
    "🟡 Wafers Requiring Review"
)

review_df = df[
    df["Decision"] == "REVIEW"
].copy()


if review_df.empty:

    st.info(
        "No wafers require review."
    )

else:

    st.dataframe(
        review_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# WORST WAFERS
# ============================================================

st.divider()

st.header(
    "🏆 Highest Priority Wafers"
)

ranking_df = df.sort_values(
    by=[
        "HIGH",
        "Total_Defects",
        "Defect_Area",
        "Maximum_Residual"
    ],
    ascending=False
).copy()

top_count = min(
    10,
    len(ranking_df)
)

top_df = ranking_df.head(
    top_count
)

st.dataframe(
    top_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DEFECT COUNT CHART
# ============================================================

st.divider()

st.header(
    "📈 Defects by Wafer"
)

fig1 = plt.figure(
    figsize=(10, 4)
)

plt.bar(
    df["Input"],
    df["Total_Defects"]
)

plt.title(
    "Total Defects per Wafer"
)

plt.xlabel(
    "Wafer"
)

plt.ylabel(
    "Defect Count"
)

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

st.pyplot(
    fig1,
    use_container_width=False
)

chart1_path = os.path.join(
    REPORT_DIR,
    "batch_defects_chart.png"
)

fig1.savefig(
    chart1_path,
    dpi=180,
    bbox_inches="tight"
)

plt.close(
    fig1
)


# ============================================================
# SEVERITY CHART
# ============================================================

st.header(
    "📊 Severity Distribution"
)

severity_names = [
    "HIGH",
    "MEDIUM",
    "LOW"
]

severity_values = [
    total_high,
    total_medium,
    total_low
]

fig2 = plt.figure(
    figsize=(7, 4)
)

plt.bar(
    severity_names,
    severity_values
)

plt.title(
    "Batch Defect Severity"
)

plt.xlabel(
    "Severity"
)

plt.ylabel(
    "Count"
)

plt.tight_layout()

st.pyplot(
    fig2,
    use_container_width=False
)

chart2_path = os.path.join(
    REPORT_DIR,
    "batch_severity_chart.png"
)

fig2.savefig(
    chart2_path,
    dpi=180,
    bbox_inches="tight"
)

plt.close(
    fig2
)


# ============================================================
# RESIDUAL CHART
# ============================================================

st.header(
    "📉 Residual Comparison"
)

fig3 = plt.figure(
    figsize=(10, 4)
)

plt.plot(
    df["Input"],
    df["Mean_Residual"],
    marker="o",
    label="Mean Residual"
)

plt.plot(
    df["Input"],
    df["Maximum_Residual"],
    marker="o",
    label="Maximum Residual"
)

plt.title(
    "Residual Comparison"
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
    fig3,
    use_container_width=False
)

chart3_path = os.path.join(
    REPORT_DIR,
    "batch_residual_chart.png"
)

fig3.savefig(
    chart3_path,
    dpi=180,
    bbox_inches="tight"
)

plt.close(
    fig3
)


# ============================================================
# GENERATE TEXT REPORT
# ============================================================

timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

report_path = os.path.join(
    REPORT_DIR,
    "batch_inspection_report_"
    +
    timestamp
    +
    ".txt"
)


with open(
    report_path,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "============================================================\n"
    )

    report.write(
        "WAFERREVIVE-AI\n"
    )

    report.write(
        "STEP 36 - BATCH INSPECTION REPORT\n"
    )

    report.write(
        "============================================================\n\n"
    )

    report.write(
        "Generated : "
        +
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        +
        "\n"
    )

    report.write(
        "Source    : Step 35 Batch Inspection\n\n"
    )

    report.write(
        "OVERALL STATUS\n"
    )

    report.write(
        "--------------\n"
    )

    report.write(
        "Status : "
        +
        overall_status
        +
        "\n"
    )

    report.write(
        "Reason : "
        +
        status_reason
        +
        "\n\n"
    )

    report.write(
        "BATCH STATISTICS\n"
    )

    report.write(
        "----------------\n"
    )

    report.write(
        "Total wafers       : "
        +
        str(total_wafers)
        +
        "\n"
    )

    report.write(
        "Defective wafers   : "
        +
        str(defective_count)
        +
        "\n"
    )

    report.write(
        "Review wafers      : "
        +
        str(review_count)
        +
        "\n"
    )

    report.write(
        "Acceptable wafers  : "
        +
        str(acceptable_count)
        +
        "\n"
    )

    report.write(
        "Total defects      : "
        +
        str(total_defects)
        +
        "\n"
    )

    report.write(
        "Total defect area  : "
        +
        str(total_area)
        +
        " pixels\n\n"
    )

    report.write(
        "SEVERITY\n"
    )

    report.write(
        "--------\n"
    )

    report.write(
        "HIGH   : "
        +
        str(total_high)
        +
        "\n"
    )

    report.write(
        "MEDIUM : "
        +
        str(total_medium)
        +
        "\n"
    )

    report.write(
        "LOW    : "
        +
        str(total_low)
        +
        "\n\n"
    )

    report.write(
        "QUALITY STATISTICS\n"
    )

    report.write(
        "------------------\n"
    )

    report.write(
        "Average residual       : %.6f\n"
        %
        average_residual
    )

    report.write(
        "Maximum residual       : %.6f\n"
        %
        maximum_residual
    )

    report.write(
        "Average suspicious area: %.4f%%\n"
        %
        average_suspicious_area
    )

    report.write(
        "Maximum suspicious area: %.4f%%\n\n"
        %
        maximum_suspicious_area
    )

    report.write(
        "WAFER RESULTS\n"
    )

    report.write(
        "-------------\n\n"
    )

    for _, row in df.iterrows():

        report.write(
            "Wafer: "
            +
            str(row["Input"])
            +
            "\n"
        )

        report.write(
            "Decision: "
            +
            str(row["Decision"])
            +
            "\n"
        )

        report.write(
            "Defects: "
            +
            str(int(row["Total_Defects"]))
            +
            "\n"
        )

        report.write(
            "HIGH: "
            +
            str(int(row["HIGH"]))
            +
            "\n"
        )

        report.write(
            "MEDIUM: "
            +
            str(int(row["MEDIUM"]))
            +
            "\n"
        )

        report.write(
            "LOW: "
            +
            str(int(row["LOW"]))
            +
            "\n"
        )

        report.write(
            "Defect area: "
            +
            str(int(row["Defect_Area"]))
            +
            " pixels\n"
        )

        report.write(
            "Mean residual: %.6f\n"
            %
            float(
                row["Mean_Residual"]
            )
        )

        report.write(
            "Maximum residual: %.6f\n"
            %
            float(
                row["Maximum_Residual"]
            )
        )

        report.write(
            "Suspicious area: %.4f%%\n\n"
            %
            float(
                row[
                    "Suspicious_Area_Percent"
                ]
            )
        )

    report.write(
        "============================================================\n"
    )

    report.write(
        "STEP 36 REPORT COMPLETED\n"
    )

    report.write(
        "============================================================\n"
    )


# ============================================================
# EXPORT SECTION
# ============================================================

st.divider()

st.header(
    "💾 Export & Download"
)

st.write(
    "Download the complete batch inspection package."
)


# ------------------------------------------------------------
# CSV
# ------------------------------------------------------------

with open(
    csv_path,
    "rb"
) as file:

    st.download_button(
        "⬇️ Download Batch CSV",
        data=file.read(),
        file_name="batch_inspection_results.csv",
        mime="text/csv",
        use_container_width=True
    )


# ------------------------------------------------------------
# TEXT REPORT
# ------------------------------------------------------------

with open(
    report_path,
    "rb"
) as file:

    st.download_button(
        "📄 Download Professional Report",
        data=file.read(),
        file_name=os.path.basename(
            report_path
        ),
        mime="text/plain",
        use_container_width=True
    )


# ------------------------------------------------------------
# CHARTS
# ------------------------------------------------------------

col1, col2, col3 = st.columns(3)


with col1:

    with open(
        chart1_path,
        "rb"
    ) as file:

        st.download_button(
            "📊 Download Defect Chart",
            data=file.read(),
            file_name="batch_defects_chart.png",
            mime="image/png",
            use_container_width=True
        )


with col2:

    with open(
        chart2_path,
        "rb"
    ) as file:

        st.download_button(
            "📊 Download Severity Chart",
            data=file.read(),
            file_name="batch_severity_chart.png",
            mime="image/png",
            use_container_width=True
        )


with col3:

    with open(
        chart3_path,
        "rb"
    ) as file:

        st.download_button(
            "📈 Download Residual Chart",
            data=file.read(),
            file_name="batch_residual_chart.png",
            mime="image/png",
            use_container_width=True
        )


# ============================================================
# FILE LOCATIONS
# ============================================================

st.divider()

st.header(
    "📁 Saved Report Files"
)

st.code(
    REPORT_DIR
)

st.write(
    "Generated report:"
)

st.code(
    report_path
)


# ============================================================
# FINAL
# ============================================================

st.divider()

if overall_status == "DEFECTIVE":

    st.error(
        "🔴 STEP 36 COMPLETE — BATCH STATUS: DEFECTIVE"
    )

elif overall_status == "REVIEW":

    st.warning(
        "🟡 STEP 36 COMPLETE — BATCH STATUS: REVIEW"
    )

else:

    st.success(
        "🟢 STEP 36 COMPLETE — BATCH STATUS: ACCEPTABLE"
    )

st.caption(
    "WaferRevive-AI — Batch Inspection Reporting"
)