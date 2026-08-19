import os
import io
import json
import zipfile
import base64
from datetime import datetime

import streamlit as st
import pandas as pd


# ============================================================
# WAFERREVIVE-AI
# STEP 39 - PROFESSIONAL REPORT & EXPORT CENTER
# ============================================================

st.set_page_config(
    page_title="WaferRevive-AI - Reports",
    page_icon="📋",
    layout="wide"
)


# ============================================================
# PATHS
# ============================================================

BASE = r"D:\WaferRevive-AI"

RESULTS_DIR = os.path.join(
    BASE,
    "results"
)

HISTORY_DIR = os.path.join(
    RESULTS_DIR,
    "inspection_history"
)

REPORT_DIR = os.path.join(
    RESULTS_DIR,
    "professional_reports"
)

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "📋 WaferRevive-AI"
)

st.subheader(
    "Professional Inspection Report & Export Center"
)

st.caption(
    "Step 39"
)


# ============================================================
# LOAD HISTORY
# ============================================================

def get_history_files():

    if not os.path.exists(
        HISTORY_DIR
    ):
        return []

    return sorted(
        [
            os.path.join(
                HISTORY_DIR,
                filename
            )
            for filename in os.listdir(
                HISTORY_DIR
            )
            if filename.lower().endswith(
                ".json"
            )
        ],
        reverse=True
    )


def load_record(path):

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )

    except Exception:

        return None


history_files = get_history_files()


# ============================================================
# NO HISTORY
# ============================================================

if not history_files:

    st.warning(
        "No saved inspections were found."
    )

    st.info(
        "Run Step 38 and complete at least one inspection first."
    )

    st.code(
        "python -m streamlit run step38_unified_dashboard.py"
    )

    st.stop()


# ============================================================
# LOAD VALID RECORDS
# ============================================================

records = []

for path in history_files:

    record = load_record(
        path
    )

    if record is not None:

        records.append(
            {
                "path": path,
                "record": record
            }
        )


if not records:

    st.error(
        "Inspection history files could not be read."
    )

    st.stop()


# ============================================================
# SELECT INSPECTION
# ============================================================

st.header(
    "🔎 Select Inspection"
)

labels = []

for item in records:

    record = item["record"]

    filename = record.get(
        "input_file",
        "Unknown"
    )

    timestamp = record.get(
        "timestamp",
        "Unknown"
    )

    decision = record.get(
        "decision",
        "Unknown"
    )

    labels.append(
        f"{timestamp} | {filename} | {decision}"
    )


selected_index = st.selectbox(
    "Choose an inspection",
    range(
        len(labels)
    ),
    format_func=lambda index:
        labels[index]
)


selected = records[
    selected_index
]

record = selected[
    "record"
]


# ============================================================
# REPORT DATA
# ============================================================

input_file = record.get(
    "input_file",
    "Unknown"
)

timestamp = record.get(
    "timestamp",
    "Unknown"
)

quality_score = float(
    record.get(
        "quality_score",
        0
    )
)

grade = record.get(
    "grade",
    "N/A"
)

decision = record.get(
    "decision",
    "N/A"
)

reason = record.get(
    "reason",
    "N/A"
)

total_defects = int(
    record.get(
        "total_defects",
        0
    )
)

high = int(
    record.get(
        "high",
        0
    )
)

medium = int(
    record.get(
        "medium",
        0
    )
)

low = int(
    record.get(
        "low",
        0
    )
)

defect_area = float(
    record.get(
        "defect_area_percent",
        0
    )
)

height = record.get(
    "height",
    "N/A"
)

width = record.get(
    "width",
    "N/A"
)

threshold = record.get(
    "threshold",
    "N/A"
)


# ============================================================
# TOP SUMMARY
# ============================================================

st.divider()

st.header(
    "🎯 Inspection Summary"
)


if decision == "DEFECTIVE":

    st.error(
        "🔴 FINAL DECISION: DEFECTIVE"
    )

elif decision == "REVIEW":

    st.warning(
        "🟡 FINAL DECISION: REVIEW REQUIRED"
    )

else:

    st.success(
        "🟢 FINAL DECISION: ACCEPTABLE"
    )


st.write(
    "**Reason:**",
    reason
)


# ============================================================
# METRICS
# ============================================================

c1, c2, c3, c4, c5 = st.columns(5)

with c1:

    st.metric(
        "Quality Score",
        f"{quality_score:.2f}/100"
    )

with c2:

    st.metric(
        "Grade",
        grade
    )

with c3:

    st.metric(
        "Total Defects",
        total_defects
    )

with c4:

    st.metric(
        "HIGH",
        high
    )

with c5:

    st.metric(
        "Defect Area",
        f"{defect_area:.2f}%"
    )


# ============================================================
# INSPECTION INFORMATION
# ============================================================

st.divider()

st.header(
    "📋 Inspection Information"
)

info1, info2 = st.columns(2)

with info1:

    st.write(
        "**Input File:**",
        input_file
    )

    st.write(
        "**Inspection Time:**",
        timestamp
    )

    st.write(
        "**Image Height:**",
        height
    )

with info2:

    st.write(
        "**Image Width:**",
        width
    )

    st.write(
        "**Detection Threshold:**",
        threshold
    )

    st.write(
        "**Decision:**",
        decision
    )


# ============================================================
# DEFECT TABLE
# ============================================================

st.divider()

st.header(
    "🔍 Defect Severity Analysis"
)

defect_df = pd.DataFrame(
    {
        "Severity": [
            "HIGH",
            "MEDIUM",
            "LOW",
            "TOTAL"
        ],
        "Count": [
            high,
            medium,
            low,
            total_defects
        ]
    }
)

st.dataframe(
    defect_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# QUALITY INTERPRETATION
# ============================================================

st.header(
    "📊 Quality Assessment"
)

if quality_score >= 90:

    assessment = (
        "Excellent wafer quality. "
        "No significant inspection concerns."
    )

elif quality_score >= 80:

    assessment = (
        "Good wafer quality with "
        "minor inspection concerns."
    )

elif quality_score >= 70:

    assessment = (
        "Moderate quality. "
        "Further inspection is recommended."
    )

elif quality_score >= 60:

    assessment = (
        "Low quality. "
        "Review detected regions carefully."
    )

else:

    assessment = (
        "Poor wafer quality. "
        "Significant inspection concerns detected."
    )


st.info(
    assessment
)


# ============================================================
# REPORT GENERATOR
# ============================================================

def generate_html_report(record):

    score = float(
        record.get(
            "quality_score",
            0
        )
    )

    decision_value = record.get(
        "decision",
        "N/A"
    )

    if decision_value == "DEFECTIVE":

        status_color = "#c62828"

    elif decision_value == "REVIEW":

        status_color = "#ef6c00"

    else:

        status_color = "#2e7d32"


    html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>
WaferRevive-AI Inspection Report
</title>

<style>

body {{
    font-family: Arial, sans-serif;
    margin: 40px;
    background: #f5f7fa;
    color: #222;
}}

.header {{
    background: #111827;
    color: white;
    padding: 30px;
    border-radius: 12px;
}}

h1 {{
    margin: 0;
}}

h2 {{
    margin-top: 35px;
}}

.status {{
    padding: 18px;
    color: white;
    background: {status_color};
    border-radius: 10px;
    font-size: 22px;
    font-weight: bold;
}}

.metrics {{
    display: grid;
    grid-template-columns:
        repeat(4, 1fr);
    gap: 15px;
}}

.metric {{
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow:
        0 2px 8px
        rgba(0,0,0,0.08);
}}

.value {{
    font-size: 28px;
    font-weight: bold;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
}}

th, td {{
    padding: 12px;
    border: 1px solid #ddd;
    text-align: left;
}}

.footer {{
    margin-top: 50px;
    color: #777;
}}

</style>

</head>

<body>

<div class="header">

<h1>
🔬 WaferRevive-AI
</h1>

<p>
Professional Semiconductor Wafer Inspection Report
</p>

</div>

<h2>
Inspection Status
</h2>

<div class="status">

{decision_value}

</div>

<p>
<strong>Reason:</strong>
{record.get("reason", "N/A")}
</p>

<h2>
Quality Metrics
</h2>

<div class="metrics">

<div class="metric">

Quality Score

<div class="value">
{score:.2f}
</div>

</div>

<div class="metric">

Grade

<div class="value">
{record.get("grade", "N/A")}
</div>

</div>

<div class="metric">

Total Defects

<div class="value">
{record.get("total_defects", 0)}
</div>

</div>

<div class="metric">

Defect Area

<div class="value">
{float(record.get("defect_area_percent", 0)):.2f}%
</div>

</div>

</div>

<h2>
Inspection Information
</h2>

<table>

<tr>
<th>Input File</th>
<td>{record.get("input_file", "N/A")}</td>
</tr>

<tr>
<th>Timestamp</th>
<td>{record.get("timestamp", "N/A")}</td>
</tr>

<tr>
<th>Image Size</th>
<td>
{record.get("height", "N/A")}
×
{record.get("width", "N/A")}
</td>
</tr>

<tr>
<th>Threshold</th>
<td>{record.get("threshold", "N/A")}</td>
</tr>

</table>

<h2>
Defect Severity
</h2>

<table>

<tr>
<th>Severity</th>
<th>Count</th>
</tr>

<tr>
<td>HIGH</td>
<td>{record.get("high", 0)}</td>
</tr>

<tr>
<td>MEDIUM</td>
<td>{record.get("medium", 0)}</td>
</tr>

<tr>
<td>LOW</td>
<td>{record.get("low", 0)}</td>
</tr>

<tr>
<th>TOTAL</th>
<th>{record.get("total_defects", 0)}</th>
</tr>

</table>

<h2>
Quality Assessment
</h2>

<p>
{assessment}
</p>

<div class="footer">

Generated by WaferRevive-AI<br>

{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

</div>

</body>

</html>
"""

    return html


# ============================================================
# CREATE REPORT
# ============================================================

st.divider()

st.header(
    "📄 Generate Professional Report"
)

if st.button(
    "🚀 GENERATE PROFESSIONAL REPORT",
    type="primary",
    use_container_width=True
):

    html_report = generate_html_report(
        record
    )

    safe_name = os.path.splitext(
        input_file
    )[0]

    report_name = (
        safe_name
        +
        "_professional_report.html"
    )

    report_path = os.path.join(
        REPORT_DIR,
        report_name
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            html_report
        )


    # ========================================================
    # JSON
    # ========================================================

    json_data = json.dumps(
        record,
        indent=4
    )


    # ========================================================
    # ZIP
    # ========================================================

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as archive:

        archive.writestr(
            "inspection_report.html",
            html_report
        )

        archive.writestr(
            "inspection_data.json",
            json_data
        )

        archive.writestr(
            "defect_summary.csv",
            defect_df.to_csv(
                index=False
            )
        )

    zip_buffer.seek(0)


    # ========================================================
    # SESSION
    # ========================================================

    st.session_state[
        "html_report"
    ] = html_report

    st.session_state[
        "json_report"
    ] = json_data

    st.session_state[
        "zip_report"
    ] = zip_buffer.getvalue()

    st.session_state[
        "report_path"
    ] = report_path

    st.success(
        "✅ Professional report generated successfully."
    )


# ============================================================
# DOWNLOADS
# ============================================================

if "html_report" in st.session_state:

    st.divider()

    st.header(
        "📥 Download Report Package"
    )

    d1, d2, d3 = st.columns(3)

    with d1:

        st.download_button(
            "🌐 Download HTML Report",
            data=st.session_state[
                "html_report"
            ],
            file_name=(
                os.path.splitext(
                    input_file
                )[0]
                +
                "_professional_report.html"
            ),
            mime="text/html",
            use_container_width=True
        )

    with d2:

        st.download_button(
            "📄 Download JSON",
            data=st.session_state[
                "json_report"
            ],
            file_name=(
                os.path.splitext(
                    input_file
                )[0]
                +
                "_inspection.json"
            ),
            mime="application/json",
            use_container_width=True
        )

    with d3:

        st.download_button(
            "📦 DOWNLOAD COMPLETE PACKAGE",
            data=st.session_state[
                "zip_report"
            ],
            file_name=(
                os.path.splitext(
                    input_file
                )[0]
                +
                "_professional_package.zip"
            ),
            mime="application/zip",
            use_container_width=True
        )


    st.success(
        "📦 Complete package contains HTML report, "
        "JSON inspection data and defect summary CSV."
    )


# ============================================================
# REPORT PREVIEW
# ============================================================

if "html_report" in st.session_state:

    st.divider()

    st.header(
        "👁️ Report Preview"
    )

    st.components.v1.html(
        st.session_state[
            "html_report"
        ],
        height=850,
        scrolling=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "WaferRevive-AI | Step 39 | Professional Inspection Reporting"
)