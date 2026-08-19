import os
import json
import glob

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ============================================================
# WAFERREVIVE-AI
# STEP 42 - FINAL ANALYTICS DASHBOARD
# ============================================================

st.set_page_config(
    page_title="WaferRevive-AI - Analytics",
    page_icon="📊",
    layout="wide"
)


BASE = r"D:\WaferRevive-AI"

RESULTS_DIR = os.path.join(
    BASE,
    "results"
)

HISTORY_DIR = os.path.join(
    RESULTS_DIR,
    "inspection_history"
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 WaferRevive-AI Analytics"
)

st.subheader(
    "Inspection Statistics & Quality Analytics"
)

st.caption(
    "Step 42 — Analytics only"
)


# ============================================================
# LOAD JSON RECORDS
# ============================================================

def find_json_files():

    paths = []

    search_locations = [
        HISTORY_DIR,
        RESULTS_DIR
    ]

    for location in search_locations:

        if not os.path.exists(location):
            continue

        pattern = os.path.join(
            location,
            "**",
            "*.json"
        )

        paths.extend(
            glob.glob(
                pattern,
                recursive=True
            )
        )

    return sorted(
        list(set(paths))
    )


def load_records():

    records = []

    for path in find_json_files():

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            if not isinstance(
                data,
                dict
            ):
                continue

            record = dict(
                data
            )

            record["_source"] = path

            records.append(
                record
            )

        except Exception:

            continue

    return records


records = load_records()


# ============================================================
# ALSO SEARCH CSV SUMMARY FILES
# ============================================================

def load_csv_records():

    rows = []

    pattern = os.path.join(
        RESULTS_DIR,
        "**",
        "*.csv"
    )

    csv_files = glob.glob(
        pattern,
        recursive=True
    )

    for path in csv_files:

        try:

            df = pd.read_csv(
                path
            )

            if df.empty:
                continue

            columns = {
                str(column).lower()
                for column in df.columns
            }

            useful = (
                "quality_score" in columns
                or "score" in columns
                or "defect_area_percent" in columns
                or "total_defects" in columns
            )

            if not useful:
                continue

            for _, row in df.iterrows():

                item = {}

                for column in df.columns:

                    value = row[column]

                    if pd.isna(value):
                        value = None

                    item[
                        str(column)
                    ] = value

                item[
                    "_source"
                ] = path

                rows.append(
                    item
                )

        except Exception:

            continue

    return rows


csv_records = load_csv_records()


# ============================================================
# NORMALIZE RECORDS
# ============================================================

all_records = records + csv_records


def number(
    record,
    keys,
    default=0.0
):

    for key in keys:

        if key in record:

            try:

                return float(
                    record[key]
                )

            except Exception:

                pass

    return float(
        default
    )


def text(
    record,
    keys,
    default="N/A"
):

    for key in keys:

        if key in record:

            value = record[key]

            if value is not None:

                return str(
                    value
                )

    return default


normalized = []


for record in all_records:

    normalized.append(
        {
            "input_file": text(
                record,
                [
                    "input_file",
                    "filename",
                    "file_name",
                    "image"
                ]
            ),

            "timestamp": text(
                record,
                [
                    "timestamp",
                    "date",
                    "datetime"
                ]
            ),

            "quality_score": number(
                record,
                [
                    "quality_score",
                    "score"
                ]
            ),

            "total_defects": int(
                number(
                    record,
                    [
                        "total_defects",
                        "defects",
                        "defect_count"
                    ]
                )
            ),

            "high": int(
                number(
                    record,
                    [
                        "high",
                        "high_defects",
                        "high_count"
                    ]
                )
            ),

            "medium": int(
                number(
                    record,
                    [
                        "medium",
                        "medium_defects",
                        "medium_count"
                    ]
                )
            ),

            "low": int(
                number(
                    record,
                    [
                        "low",
                        "low_defects",
                        "low_count"
                    ]
                )
            ),

            "defect_area": number(
                record,
                [
                    "defect_area_percent",
                    "defect_area",
                    "suspicious_area"
                ]
            ),

            "decision": text(
                record,
                [
                    "decision",
                    "status",
                    "result"
                ]
            ),

            "grade": text(
                record,
                [
                    "grade"
                ]
            ),

            "_source": text(
                record,
                [
                    "_source"
                ]
            )
        }
    )


# ============================================================
# REMOVE DUPLICATES
# ============================================================

unique = {}

for record in normalized:

    key = (
        record["input_file"],
        record["timestamp"],
        record["quality_score"],
        record["total_defects"],
        record["decision"]
    )

    unique[key] = record


data = list(
    unique.values()
)


# ============================================================
# EMPTY DATA
# ============================================================

if not data:

    st.warning(
        "No inspection analytics data was found yet."
    )

    st.info(
        "Complete at least one inspection from New Inspection "
        "and save its results before using Analytics."
    )

    st.stop()


# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame(
    data
)


# ============================================================
# CLEAN DATA
# ============================================================

df["quality_score"] = pd.to_numeric(
    df["quality_score"],
    errors="coerce"
).fillna(0)

df["total_defects"] = pd.to_numeric(
    df["total_defects"],
    errors="coerce"
).fillna(0)

df["high"] = pd.to_numeric(
    df["high"],
    errors="coerce"
).fillna(0)

df["medium"] = pd.to_numeric(
    df["medium"],
    errors="coerce"
).fillna(0)

df["low"] = pd.to_numeric(
    df["low"],
    errors="coerce"
).fillna(0)

df["defect_area"] = pd.to_numeric(
    df["defect_area"],
    errors="coerce"
).fillna(0)


# ============================================================
# FILTERS
# ============================================================

st.sidebar.header(
    "🔎 Filters"
)

decisions = sorted(
    [
        str(x)
        for x in df["decision"].dropna().unique()
    ]
)

selected_decisions = st.sidebar.multiselect(
    "Decision",
    decisions,
    default=decisions
)


filtered = df[
    df["decision"].isin(
        selected_decisions
    )
].copy()


if filtered.empty:

    st.warning(
        "No inspections match the selected filters."
    )

    st.stop()


# ============================================================
# TOP METRICS
# ============================================================

st.divider()

st.header(
    "📌 Overall Inspection Statistics"
)

total_inspections = len(
    filtered
)

average_score = filtered[
    "quality_score"
].mean()

average_defect_area = filtered[
    "defect_area"
].mean()

total_detected_defects = int(
    filtered[
        "total_defects"
    ].sum()
)

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "Inspections",
        total_inspections
    )

with c2:

    st.metric(
        "Average Quality",
        f"{average_score:.2f}/100"
    )

with c3:

    st.metric(
        "Total Defects",
        total_detected_defects
    )

with c4:

    st.metric(
        "Avg Defect Area",
        f"{average_defect_area:.2f}%"
    )


# ============================================================
# DECISION COUNTS
# ============================================================

st.divider()

st.header(
    "🎯 Inspection Decisions"
)

decision_counts = (
    filtered[
        "decision"
    ]
    .value_counts()
)


chart_col, table_col = st.columns(
    [2, 1]
)


with chart_col:

    fig, ax = plt.subplots(
        figsize=(8, 4)
    )

    decision_counts.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Inspection Decision Distribution"
    )

    ax.set_xlabel(
        "Decision"
    )

    ax.set_ylabel(
        "Number of Inspections"
    )

    plt.xticks(
        rotation=0
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(
        fig
    )


with table_col:

    decision_table = (
        decision_counts
        .reset_index()
    )

    decision_table.columns = [
        "Decision",
        "Count"
    ]

    st.dataframe(
        decision_table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# QUALITY SCORE
# ============================================================

st.divider()

st.header(
    "📈 Quality Score Analytics"
)

quality_col1, quality_col2 = st.columns(
    2
)


with quality_col1:

    fig, ax = plt.subplots(
        figsize=(8, 4)
    )

    ax.hist(
        filtered[
            "quality_score"
        ],
        bins=10
    )

    ax.set_title(
        "Quality Score Distribution"
    )

    ax.set_xlabel(
        "Quality Score"
    )

    ax.set_ylabel(
        "Number of Inspections"
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(
        fig
    )


with quality_col2:

    score_values = filtered[
        "quality_score"
    ].reset_index(
        drop=True
    )

    fig, ax = plt.subplots(
        figsize=(8, 4)
    )

    ax.plot(
        range(
            1,
            len(score_values) + 1
        ),
        score_values,
        marker="o"
    )

    ax.set_title(
        "Inspection Quality Trend"
    )

    ax.set_xlabel(
        "Inspection Number"
    )

    ax.set_ylabel(
        "Quality Score"
    )

    ax.set_ylim(
        0,
        100
    )

    ax.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(
        fig
    )


# ============================================================
# SEVERITY ANALYSIS
# ============================================================

st.divider()

st.header(
    "🔴 Defect Severity Analytics"
)

severity_totals = pd.Series(
    {
        "HIGH": int(
            filtered["high"].sum()
        ),
        "MEDIUM": int(
            filtered["medium"].sum()
        ),
        "LOW": int(
            filtered["low"].sum()
        )
    }
)


severity_col1, severity_col2 = st.columns(
    2
)


with severity_col1:

    fig, ax = plt.subplots(
        figsize=(8, 4)
    )

    severity_totals.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Defect Severity Distribution"
    )

    ax.set_xlabel(
        "Severity"
    )

    ax.set_ylabel(
        "Defect Count"
    )

    plt.xticks(
        rotation=0
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(
        fig
    )


with severity_col2:

    st.dataframe(
        severity_totals
        .reset_index()
        .rename(
            columns={
                "index": "Severity",
                0: "Count"
            }
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# DEFECT AREA
# ============================================================

st.divider()

st.header(
    "📐 Defect Area Analytics"
)

fig, ax = plt.subplots(
    figsize=(12, 4)
)

ax.plot(
    range(
        1,
        len(filtered) + 1
    ),
    filtered[
        "defect_area"
    ].values,
    marker="o"
)

ax.set_title(
    "Defect Area by Inspection"
)

ax.set_xlabel(
    "Inspection Number"
)

ax.set_ylabel(
    "Defect Area (%)"
)

ax.grid(
    True,
    alpha=0.3
)

plt.tight_layout()

st.pyplot(
    fig,
    use_container_width=True
)

plt.close(
    fig
)


# ============================================================
# INSPECTION TABLE
# ============================================================

st.divider()

st.header(
    "📋 Inspection Dataset"
)

display_df = filtered[
    [
        "input_file",
        "timestamp",
        "quality_score",
        "grade",
        "total_defects",
        "high",
        "medium",
        "low",
        "defect_area",
        "decision"
    ]
].copy()

display_df.columns = [
    "Input File",
    "Timestamp",
    "Quality Score",
    "Grade",
    "Total Defects",
    "HIGH",
    "MEDIUM",
    "LOW",
    "Defect Area %",
    "Decision"
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# SELECTED INSPECTION
# ============================================================

st.divider()

st.header(
    "🔎 Selected Inspection Details"
)

selected_row = st.selectbox(
    "Select an inspection",
    range(
        len(filtered)
    ),
    format_func=lambda i:
        str(
            filtered.iloc[i][
                "input_file"
            ]
        )
)


selected = filtered.iloc[
    selected_row
]


d1, d2, d3 = st.columns(3)

with d1:

    st.write(
        "**Input:**",
        selected[
            "input_file"
        ]
    )

    st.write(
        "**Timestamp:**",
        selected[
            "timestamp"
        ]
    )

with d2:

    st.write(
        "**Quality Score:**",
        f'{selected["quality_score"]:.2f}/100'
    )

    st.write(
        "**Grade:**",
        selected[
            "grade"
        ]
    )

with d3:

    st.write(
        "**Decision:**",
        selected[
            "decision"
        ]
    )

    st.write(
        "**Defect Area:**",
        f'{selected["defect_area"]:.2f}%'
    )


# ============================================================
# DOWNLOAD ANALYTICS
# ============================================================

st.divider()

st.header(
    "📥 Export Analytics"
)

csv_data = filtered.to_csv(
    index=False
)

st.download_button(
    "⬇️ Download Analytics CSV",
    data=csv_data,
    file_name="waferrevive_ai_analytics.csv",
    mime="text/csv",
    use_container_width=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.success(
    "✅ Analytics module ready"
)

st.caption(
    "WaferRevive-AI | Step 42 | Analytics"
)