import os
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ============================================================
# WAFERREVIVE-AI
# STEP 37 - BATCH QUALITY ANALYTICS
# ============================================================

st.set_page_config(
    page_title="WaferRevive-AI - Quality Analytics",
    page_icon="📊",
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

ANALYTICS_DIR = os.path.join(
    BASE,
    "results",
    "batch_quality_analytics"
)

os.makedirs(
    ANALYTICS_DIR,
    exist_ok=True
)

CSV_PATH = os.path.join(
    BATCH_DIR,
    "batch_inspection_results.csv"
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "🔬 WaferRevive-AI"
)

st.subheader(
    "Step 37 — Batch Quality Analytics"
)

st.caption(
    "Advanced quality scoring, ranking, defect analysis "
    "and batch-level wafer performance analytics."
)


# ============================================================
# CHECK INPUT
# ============================================================

if not os.path.exists(CSV_PATH):

    st.error(
        "Step 35 batch results were not found."
    )

    st.write(
        "Expected file:"
    )

    st.code(
        CSV_PATH
    )

    st.write(
        "Run Step 35 first:"
    )

    st.code(
        "python -m streamlit run step35_batch_inspection.py"
    )

    st.stop()


# ============================================================
# LOAD CSV
# ============================================================

try:

    df = pd.read_csv(
        CSV_PATH
    )

except Exception as error:

    st.error(
        "Unable to read the Step 35 CSV."
    )

    st.exception(
        error
    )

    st.stop()


if df.empty:

    st.warning(
        "The batch results contain no wafers."
    )

    st.stop()


# ============================================================
# NUMERIC CLEANUP
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
# MISSING COLUMNS SAFETY
# ============================================================

required_defaults = {

    "Total_Defects": 0,
    "HIGH": 0,
    "MEDIUM": 0,
    "LOW": 0,
    "Defect_Area": 0,
    "Mean_Residual": 0.0,
    "Maximum_Residual": 0.0,
    "Adaptive_Threshold": 0.0,
    "Final_Defect_Pixels": 0,
    "Suspicious_Area_Percent": 0.0
}


for column, default in required_defaults.items():

    if column not in df.columns:

        df[column] = default


# ============================================================
# QUALITY SCORE
# ============================================================
#
# Score starts at 100.
#
# HIGH defects:
#     strongest penalty
#
# MEDIUM:
#     moderate penalty
#
# LOW:
#     small penalty
#
# Suspicious area and residuals also influence score.
#
# Final score is clipped to 0-100.
# ============================================================

def calculate_quality_score(row):

    score = 100.0

    high_penalty = (
        float(row["HIGH"])
        *
        15.0
    )

    medium_penalty = (
        float(row["MEDIUM"])
        *
        7.0
    )

    low_penalty = (
        float(row["LOW"])
        *
        2.0
    )

    defect_area_penalty = min(
        float(row["Defect_Area"])
        /
        100.0
        *
        8.0,
        20.0
    )

    residual_penalty = min(
        float(row["Maximum_Residual"])
        *
        25.0,
        20.0
    )

    suspicious_penalty = min(
        float(row["Suspicious_Area_Percent"])
        *
        4.0,
        15.0
    )

    score -= high_penalty
    score -= medium_penalty
    score -= low_penalty
    score -= defect_area_penalty
    score -= residual_penalty
    score -= suspicious_penalty

    score = max(
        0.0,
        min(
            100.0,
            score
        )
    )

    return round(
        score,
        2
    )


df["Quality_Score"] = df.apply(
    calculate_quality_score,
    axis=1
)


# ============================================================
# QUALITY GRADE
# ============================================================

def quality_grade(score):

    if score >= 90:

        return "A"

    elif score >= 80:

        return "B"

    elif score >= 70:

        return "C"

    elif score >= 60:

        return "D"

    else:

        return "F"


df["Quality_Grade"] = df[
    "Quality_Score"
].apply(
    quality_grade
)


# ============================================================
# ANALYTICS RANK
# ============================================================

df = df.sort_values(
    by=[
        "Quality_Score",
        "Maximum_Residual"
    ],
    ascending=[
        False,
        True
    ]
).reset_index(
    drop=True
)

df["Quality_Rank"] = (
    df.index + 1
)


# ============================================================
# BATCH STATISTICS
# ============================================================

total_wafers = len(df)

average_score = float(
    df["Quality_Score"].mean()
)

best_score = float(
    df["Quality_Score"].max()
)

worst_score = float(
    df["Quality_Score"].min()
)

score_std = float(
    df["Quality_Score"].std()
)

if np.isnan(score_std):

    score_std = 0.0


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

average_suspicious = float(
    df["Suspicious_Area_Percent"].mean()
)

maximum_suspicious = float(
    df["Suspicious_Area_Percent"].max()
)

average_residual = float(
    df["Mean_Residual"].mean()
)

maximum_residual = float(
    df["Maximum_Residual"].max()
)


# ============================================================
# QUALITY CATEGORIES
# ============================================================

excellent_count = int(
    (
        df["Quality_Score"]
        >= 90
    ).sum()
)

good_count = int(
    (
        (df["Quality_Score"] >= 80)
        &
        (df["Quality_Score"] < 90)
    ).sum()
)

fair_count = int(
    (
        (df["Quality_Score"] >= 70)
        &
        (df["Quality_Score"] < 80)
    ).sum()
)

poor_count = int(
    (
        (df["Quality_Score"] >= 60)
        &
        (df["Quality_Score"] < 70)
    ).sum()
)

critical_count = int(
    (
        df["Quality_Score"]
        < 60
    ).sum()
)


# ============================================================
# OVERALL QUALITY STATUS
# ============================================================

if total_high > 0:

    overall_status = "DEFECTIVE"

    overall_reason = (
        "The batch contains HIGH severity defects."
    )

elif total_medium > 0:

    overall_status = "REVIEW"

    overall_reason = (
        "The batch contains MEDIUM severity defects."
    )

elif average_score < 70:

    overall_status = "REVIEW"

    overall_reason = (
        "The average quality score is below 70."
    )

else:

    overall_status = "ACCEPTABLE"

    overall_reason = (
        "The batch quality is within the acceptable range."
    )


# ============================================================
# DASHBOARD
# ============================================================

st.divider()

st.header(
    "🎯 Overall Batch Quality"
)

if overall_status == "DEFECTIVE":

    st.error(
        "🔴 BATCH QUALITY: DEFECTIVE"
    )

elif overall_status == "REVIEW":

    st.warning(
        "🟡 BATCH QUALITY: REVIEW"
    )

else:

    st.success(
        "🟢 BATCH QUALITY: ACCEPTABLE"
    )

st.write(
    overall_reason
)


# ============================================================
# MAIN SCORE
# ============================================================

score_col1, score_col2, score_col3 = st.columns(3)

with score_col1:

    st.metric(
        "Average Quality Score",
        "%.2f / 100"
        %
        average_score
    )

with score_col2:

    st.metric(
        "Best Wafer Score",
        "%.2f"
        %
        best_score
    )

with score_col3:

    st.metric(
        "Lowest Wafer Score",
        "%.2f"
        %
        worst_score
    )


# ============================================================
# BATCH METRICS
# ============================================================

st.subheader(
    "📊 Batch Metrics"
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:

    st.metric(
        "Wafers",
        total_wafers
    )

with c2:

    st.metric(
        "Total Defects",
        total_defects
    )

with c3:

    st.metric(
        "HIGH",
        total_high
    )

with c4:

    st.metric(
        "MEDIUM",
        total_medium
    )

with c5:

    st.metric(
        "LOW",
        total_low
    )


# ============================================================
# QUALITY DISTRIBUTION
# ============================================================

st.divider()

st.header(
    "📈 Quality Distribution"
)

g1, g2, g3, g4, g5 = st.columns(5)

with g1:

    st.metric(
        "A — Excellent",
        excellent_count
    )

with g2:

    st.metric(
        "B — Good",
        good_count
    )

with g3:

    st.metric(
        "C — Fair",
        fair_count
    )

with g4:

    st.metric(
        "D — Poor",
        poor_count
    )

with g5:

    st.metric(
        "F — Critical",
        critical_count
    )


# ============================================================
# QUALITY RANKING
# ============================================================

st.divider()

st.header(
    "🏆 Wafer Quality Ranking"
)

ranking_columns = [

    "Quality_Rank",
    "Input",
    "Quality_Score",
    "Quality_Grade",
    "Decision",
    "Total_Defects",
    "HIGH",
    "MEDIUM",
    "LOW",
    "Defect_Area",
    "Maximum_Residual",
    "Suspicious_Area_Percent"
]

ranking_columns = [
    c
    for c in ranking_columns
    if c in df.columns
]

st.dataframe(
    df[ranking_columns],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# BEST WAFER
# ============================================================

st.divider()

st.header(
    "🥇 Best Performing Wafer"
)

best_row = df.loc[
    df["Quality_Score"].idxmax()
]

b1, b2, b3, b4 = st.columns(4)

with b1:

    st.write(
        "**Wafer**"
    )

    st.write(
        str(best_row["Input"])
    )

with b2:

    st.write(
        "**Quality Score**"
    )

    st.write(
        "%.2f / 100"
        %
        float(
            best_row["Quality_Score"]
        )
    )

with b3:

    st.write(
        "**Grade**"
    )

    st.write(
        str(best_row["Quality_Grade"])
    )

with b4:

    st.write(
        "**Defects**"
    )

    st.write(
        int(
            best_row["Total_Defects"]
        )
    )


# ============================================================
# WORST WAFER
# ============================================================

st.header(
    "⚠️ Highest Risk Wafer"
)

worst_row = df.loc[
    df["Quality_Score"].idxmin()
]

w1, w2, w3, w4 = st.columns(4)

with w1:

    st.write(
        "**Wafer**"
    )

    st.write(
        str(worst_row["Input"])
    )

with w2:

    st.write(
        "**Quality Score**"
    )

    st.write(
        "%.2f / 100"
        %
        float(
            worst_row["Quality_Score"]
        )
    )

with w3:

    st.write(
        "**Grade**"
    )

    st.write(
        str(worst_row["Quality_Grade"])
    )

with w4:

    st.write(
        "**HIGH Defects**"
    )

    st.write(
        int(
            worst_row["HIGH"]
        )
    )


# ============================================================
# QUALITY SCORE CHART
# ============================================================

st.divider()

st.header(
    "📊 Quality Score by Wafer"
)

fig1 = plt.figure(
    figsize=(11, 5)
)

plt.bar(
    df["Input"],
    df["Quality_Score"]
)

plt.axhline(
    70,
    linestyle="--",
    linewidth=1
)

plt.axhline(
    90,
    linestyle="--",
    linewidth=1
)

plt.ylim(
    0,
    105
)

plt.title(
    "Wafer Quality Scores"
)

plt.xlabel(
    "Wafer"
)

plt.ylabel(
    "Quality Score"
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

quality_chart_path = os.path.join(
    ANALYTICS_DIR,
    "quality_scores.png"
)

fig1.savefig(
    quality_chart_path,
    dpi=180,
    bbox_inches="tight"
)

plt.close(
    fig1
)


# ============================================================
# DEFECT SEVERITY CHART
# ============================================================

st.header(
    "🚨 Defect Severity Distribution"
)

fig2 = plt.figure(
    figsize=(8, 5)
)

plt.bar(
    [
        "HIGH",
        "MEDIUM",
        "LOW"
    ],
    [
        total_high,
        total_medium,
        total_low
    ]
)

plt.title(
    "Batch Defect Severity"
)

plt.xlabel(
    "Severity"
)

plt.ylabel(
    "Defect Count"
)

plt.tight_layout()

st.pyplot(
    fig2,
    use_container_width=False
)

severity_chart_path = os.path.join(
    ANALYTICS_DIR,
    "severity_distribution.png"
)

fig2.savefig(
    severity_chart_path,
    dpi=180,
    bbox_inches="tight"
)

plt.close(
    fig2
)


# ============================================================
# QUALITY VS DEFECT AREA
# ============================================================

st.header(
    "🔎 Quality Score vs Defect Area"
)

fig3 = plt.figure(
    figsize=(9, 5)
)

plt.scatter(
    df["Defect_Area"],
    df["Quality_Score"]
)

plt.title(
    "Quality Score vs Defect Area"
)

plt.xlabel(
    "Defect Area (pixels)"
)

plt.ylabel(
    "Quality Score"
)

plt.tight_layout()

st.pyplot(
    fig3,
    use_container_width=False
)

scatter_path = os.path.join(
    ANALYTICS_DIR,
    "quality_vs_defect_area.png"
)

fig3.savefig(
    scatter_path,
    dpi=180,
    bbox_inches="tight"
)

plt.close(
    fig3
)


# ============================================================
# RESIDUAL ANALYSIS
# ============================================================

st.header(
    "📉 Residual Analysis"
)

fig4 = plt.figure(
    figsize=(11, 5)
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
    "Residual Analysis by Wafer"
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
    fig4,
    use_container_width=False
)

residual_chart_path = os.path.join(
    ANALYTICS_DIR,
    "residual_analysis.png"
)

fig4.savefig(
    residual_chart_path,
    dpi=180,
    bbox_inches="tight"
)

plt.close(
    fig4
)


# ============================================================
# ANALYTICS DATAFRAME
# ============================================================

st.divider()

st.header(
    "📋 Detailed Quality Analytics"
)

analytics_columns = [

    "Quality_Rank",
    "Input",
    "Quality_Score",
    "Quality_Grade",
    "Decision",
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

analytics_columns = [
    c
    for c in analytics_columns
    if c in df.columns
]

st.dataframe(
    df[analytics_columns],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# SAVE ANALYTICS CSV
# ============================================================

analytics_csv_path = os.path.join(
    ANALYTICS_DIR,
    "batch_quality_analytics.csv"
)

df.to_csv(
    analytics_csv_path,
    index=False
)


# ============================================================
# GENERATE TEXT REPORT
# ============================================================

timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

report_path = os.path.join(
    ANALYTICS_DIR,
    "batch_quality_analytics_report_"
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
        "STEP 37 - BATCH QUALITY ANALYTICS\n"
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
        "\n\n"
    )

    report.write(
        "OVERALL BATCH STATUS\n"
    )

    report.write(
        "---------------------\n"
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
        overall_reason
        +
        "\n\n"
    )

    report.write(
        "QUALITY SUMMARY\n"
    )

    report.write(
        "---------------\n"
    )

    report.write(
        "Total wafers          : "
        +
        str(total_wafers)
        +
        "\n"
    )

    report.write(
        "Average quality score : %.2f\n"
        %
        average_score
    )

    report.write(
        "Best quality score    : %.2f\n"
        %
        best_score
    )

    report.write(
        "Worst quality score   : %.2f\n"
        %
        worst_score
    )

    report.write(
        "Score standard dev.   : %.2f\n"
        %
        score_std
    )

    report.write(
        "Total defects         : "
        +
        str(total_defects)
        +
        "\n"
    )

    report.write(
        "Total defect area     : "
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
        "QUALITY GRADES\n"
    )

    report.write(
        "--------------\n"
    )

    report.write(
        "A - Excellent : "
        +
        str(excellent_count)
        +
        "\n"
    )

    report.write(
        "B - Good      : "
        +
        str(good_count)
        +
        "\n"
    )

    report.write(
        "C - Fair      : "
        +
        str(fair_count)
        +
        "\n"
    )

    report.write(
        "D - Poor      : "
        +
        str(poor_count)
        +
        "\n"
    )

    report.write(
        "F - Critical  : "
        +
        str(critical_count)
        +
        "\n\n"
    )

    report.write(
        "BEST WAFER\n"
    )

    report.write(
        "----------\n"
    )

    report.write(
        "Wafer : "
        +
        str(best_row["Input"])
        +
        "\n"
    )

    report.write(
        "Score : %.2f\n"
        %
        float(
            best_row["Quality_Score"]
        )
    )

    report.write(
        "Grade : "
        +
        str(best_row["Quality_Grade"])
        +
        "\n\n"
    )

    report.write(
        "HIGHEST RISK WAFER\n"
    )

    report.write(
        "------------------\n"
    )

    report.write(
        "Wafer : "
        +
        str(worst_row["Input"])
        +
        "\n"
    )

    report.write(
        "Score : %.2f\n"
        %
        float(
            worst_row["Quality_Score"]
        )
    )

    report.write(
        "Grade : "
        +
        str(worst_row["Quality_Grade"])
        +
        "\n\n"
    )

    report.write(
        "WAFER RANKING\n"
    )

    report.write(
        "-------------\n\n"
    )

    for _, row in df.iterrows():

        report.write(
            "Rank "
            +
            str(
                int(row["Quality_Rank"])
            )
            +
            " | "
            +
            str(row["Input"])
            +
            " | Score "
            +
            "%.2f"
            %
            float(
                row["Quality_Score"]
            )
            +
            " | Grade "
            +
            str(row["Quality_Grade"])
            +
            " | Defects "
            +
            str(
                int(
                    row["Total_Defects"]
                )
            )
            +
            "\n"
        )

    report.write(
        "\n============================================================\n"
    )

    report.write(
        "STEP 37 COMPLETED SUCCESSFULLY\n"
    )

    report.write(
        "============================================================\n"
    )


# ============================================================
# DOWNLOAD SECTION
# ============================================================

st.divider()

st.header(
    "💾 Download Analytics"
)


# CSV

with open(
    analytics_csv_path,
    "rb"
) as file:

    st.download_button(
        "⬇️ Download Quality Analytics CSV",
        data=file.read(),
        file_name="batch_quality_analytics.csv",
        mime="text/csv",
        use_container_width=True
    )


# Report

with open(
    report_path,
    "rb"
) as file:

    st.download_button(
        "📄 Download Quality Analytics Report",
        data=file.read(),
        file_name=os.path.basename(
            report_path
        ),
        mime="text/plain",
        use_container_width=True
    )


# Charts

d1, d2, d3, d4 = st.columns(4)


with d1:

    with open(
        quality_chart_path,
        "rb"
    ) as file:

        st.download_button(
            "📊 Quality Chart",
            data=file.read(),
            file_name="quality_scores.png",
            mime="image/png",
            use_container_width=True
        )


with d2:

    with open(
        severity_chart_path,
        "rb"
    ) as file:

        st.download_button(
            "📊 Severity Chart",
            data=file.read(),
            file_name="severity_distribution.png",
            mime="image/png",
            use_container_width=True
        )


with d3:

    with open(
        scatter_path,
        "rb"
    ) as file:

        st.download_button(
            "🔎 Quality/Area Chart",
            data=file.read(),
            file_name="quality_vs_defect_area.png",
            mime="image/png",
            use_container_width=True
        )


with d4:

    with open(
        residual_chart_path,
        "rb"
    ) as file:

        st.download_button(
            "📉 Residual Chart",
            data=file.read(),
            file_name="residual_analysis.png",
            mime="image/png",
            use_container_width=True
        )


# ============================================================
# SAVED FILES
# ============================================================

st.divider()

st.header(
    "📁 Saved Analytics Files"
)

st.code(
    ANALYTICS_DIR
)

st.write(
    "Quality analytics CSV:"
)

st.code(
    analytics_csv_path
)

st.write(
    "Quality analytics report:"
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
        "🔴 STEP 37 COMPLETED — BATCH QUALITY: DEFECTIVE"
    )

elif overall_status == "REVIEW":

    st.warning(
        "🟡 STEP 37 COMPLETED — BATCH QUALITY: REVIEW"
    )

else:

    st.success(
        "🟢 STEP 37 COMPLETED — BATCH QUALITY: ACCEPTABLE"
    )

st.caption(
    "WaferRevive-AI — Batch Quality Analytics"
)