import os
import sys
import csv
import re

import numpy as np
import pandas as pd
import torch
import streamlit as st
import matplotlib.pyplot as plt

from PIL import Image
from scipy import ndimage


# ============================================================
# WAFERREVIVE-AI
# STEP 35 - BATCH WAFER INSPECTION
# ============================================================

st.set_page_config(
    page_title="WaferRevive-AI - Batch Inspection",
    page_icon="🔬",
    layout="wide"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE = r"D:\WaferRevive-AI"

MODEL_PATH = os.path.join(
    BASE,
    "models",
    "best_model.pth"
)

OUTPUT_DIR = os.path.join(
    BASE,
    "results",
    "batch_inspection"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# IMPORT MODEL
# ============================================================

sys.path.insert(
    0,
    os.path.join(
        BASE,
        "experiments"
    )
)

from step7_model import WaferRestorationNet


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():

    model = WaferRestorationNet()

    model.load_state_dict(
        torch.load(
            MODEL_PATH,
            map_location="cpu"
        )
    )

    model.eval()

    return model


# ============================================================
# SAFE FILE NAME
# ============================================================

def safe_name(name):

    name = os.path.splitext(
        name
    )[0]

    name = re.sub(
        r"[^A-Za-z0-9_-]",
        "_",
        name
    )

    return name


# ============================================================
# PREPARE IMAGE
# SAME BASIC PIPELINE AS STEP 32
# ============================================================

def prepare_image(uploaded_file):

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".npy"):

        uploaded_file.seek(0)

        array = np.load(
            uploaded_file
        ).astype(
            np.float32
        )

    else:

        uploaded_file.seek(0)

        image = Image.open(
            uploaded_file
        ).convert(
            "L"
        )

        array = np.asarray(
            image,
            dtype=np.float32
        )

    # Remove extra channels

    if array.ndim == 3:

        array = np.mean(
            array,
            axis=2
        )

    # Normalize

    minimum = float(
        np.min(array)
    )

    maximum = float(
        np.max(array)
    )

    if maximum > 1.0 or minimum < 0.0:

        if maximum > minimum:

            array = (
                array - minimum
            ) / (
                maximum - minimum
            )

        else:

            array = np.zeros_like(
                array
            )

    array = np.nan_to_num(
        array,
        nan=0.0,
        posinf=1.0,
        neginf=0.0
    )

    array = np.clip(
        array,
        0.0,
        1.0
    )

    # Model input = 128 x 128

    image = Image.fromarray(
        (
            array * 255.0
        ).astype(
            np.uint8
        )
    )

    image = image.resize(
        (128, 128),
        Image.Resampling.BILINEAR
    )

    array = np.asarray(
        image,
        dtype=np.float32
    ) / 255.0

    return array


# ============================================================
# AI RESTORATION
# ============================================================

def restore_image(
    model,
    image
):

    tensor = torch.from_numpy(
        image
    )

    tensor = tensor.unsqueeze(
        0
    ).unsqueeze(
        0
    )

    with torch.no_grad():

        restored = model(
            tensor
        )

    restored = (
        restored
        .squeeze()
        .cpu()
        .numpy()
    )

    restored = np.nan_to_num(
        restored,
        nan=0.0,
        posinf=1.0,
        neginf=0.0
    )

    restored = np.clip(
        restored,
        0.0,
        1.0
    )

    return restored


# ============================================================
# DEFECT ANALYSIS
# SAME LOGIC AS STEP 32
# ============================================================

def analyze_defects(
    input_image,
    restored
):

    # Resize restored image back to input size

    restored_uint8 = (
        np.clip(
            restored,
            0.0,
            1.0
        ) * 255.0
    ).astype(
        np.uint8
    )

    restored_resized = np.asarray(
        Image.fromarray(
            restored_uint8
        ).resize(
            (
                input_image.shape[1],
                input_image.shape[0]
            ),
            Image.Resampling.BILINEAR
        ),
        dtype=np.float32
    ) / 255.0

    # Residual

    residual = np.abs(
        restored_resized
        -
        input_image
    )

    residual = np.nan_to_num(
        residual
    )

    # Statistics

    mean_residual = float(
        np.mean(residual)
    )

    median_residual = float(
        np.median(residual)
    )

    max_residual = float(
        np.max(residual)
    )

    p95 = float(
        np.percentile(
            residual,
            95
        )
    )

    p98 = float(
        np.percentile(
            residual,
            98
        )
    )

    p99 = float(
        np.percentile(
            residual,
            99
        )
    )

    # MAD

    absolute_deviation = np.abs(
        residual
        -
        median_residual
    )

    mad = float(
        np.median(
            absolute_deviation
        )
    )

    # Adaptive threshold

    mad_threshold = (
        median_residual
        +
        4.0 * mad
    )

    percentile_threshold = (
        p98 * 0.75
    )

    threshold = max(
        0.025,
        mad_threshold,
        percentile_threshold
    )

    threshold = min(
        threshold,
        0.12
    )

    # Initial mask

    initial_mask = (
        residual >= threshold
    )

    initial_pixels = int(
        np.sum(initial_mask)
    )

    # Morphological cleaning

    structure = np.ones(
        (3, 3),
        dtype=np.uint8
    )

    cleaned_mask = ndimage.binary_opening(
        initial_mask,
        structure=structure
    )

    cleaned_mask = ndimage.binary_closing(
        cleaned_mask,
        structure=structure
    )

    # Connected components

    labels, number = ndimage.label(
        cleaned_mask,
        structure=structure
    )

    defects = []

    refined_mask = np.zeros_like(
        cleaned_mask,
        dtype=bool
    )

    minimum_area = 8

    for region_id in range(
        1,
        number + 1
    ):

        region = (
            labels == region_id
        )

        area = int(
            np.sum(region)
        )

        if area < minimum_area:

            continue

        values = residual[
            region
        ]

        max_error = float(
            np.max(values)
        )

        mean_error = float(
            np.mean(values)
        )

        refined_mask[
            region
        ] = True

        defects.append({

            "Defect_ID":
                len(defects) + 1,

            "Area_pixels":
                area,

            "Maximum_Error":
                max_error,

            "Mean_Error":
                mean_error
        })

    # Fallback detection

    if len(defects) == 0:

        fallback_threshold = max(
            0.025,
            p99
        )

        fallback_mask = (
            residual
            >=
            fallback_threshold
        )

        labels2, number2 = ndimage.label(
            fallback_mask,
            structure=structure
        )

        for region_id in range(
            1,
            number2 + 1
        ):

            region = (
                labels2 == region_id
            )

            area = int(
                np.sum(region)
            )

            if area < 5:

                continue

            values = residual[
                region
            ]

            max_error = float(
                np.max(values)
            )

            mean_error = float(
                np.mean(values)
            )

            refined_mask[
                region
            ] = True

            defects.append({

                "Defect_ID":
                    len(defects) + 1,

                "Area_pixels":
                    area,

                "Maximum_Error":
                    max_error,

                "Mean_Error":
                    mean_error
            })

    # Priority scoring

    if defects:

        max_area = max(
            d["Area_pixels"]
            for d in defects
        )

        max_error = max(
            d["Maximum_Error"]
            for d in defects
        )

    else:

        max_area = 1
        max_error = 1

    for defect in defects:

        area_score = (
            defect["Area_pixels"]
            /
            max_area
        )

        error_score = (
            defect["Maximum_Error"]
            /
            max_error
        )

        priority = (
            0.50 * area_score
            +
            0.50 * error_score
        )

        defect[
            "Priority_Score"
        ] = float(
            priority
        )

        if priority >= 0.70:

            severity = "HIGH"

        elif priority >= 0.40:

            severity = "MEDIUM"

        else:

            severity = "LOW"

        defect[
            "Severity"
        ] = severity

    # Ranking

    defects.sort(
        key=lambda d:
            d["Priority_Score"],
        reverse=True
    )

    for rank, defect in enumerate(
        defects,
        start=1
    ):

        defect[
            "Rank"
        ] = rank

    final_pixels = int(
        np.sum(refined_mask)
    )

    return {

        "restored":
            restored,

        "residual":
            residual,

        "initial_mask":
            initial_mask,

        "refined_mask":
            refined_mask,

        "defects":
            defects,

        "mean_residual":
            mean_residual,

        "median_residual":
            median_residual,

        "max_residual":
            max_residual,

        "p95":
            p95,

        "p98":
            p98,

        "p99":
            p99,

        "mad":
            mad,

        "threshold":
            threshold,

        "initial_pixels":
            initial_pixels,

        "final_pixels":
            final_pixels,

        "minimum_area":
            minimum_area
    }


# ============================================================
# PROCESS ONE WAFER
# ============================================================

def inspect_wafer(
    model,
    uploaded_file
):

    input_image = prepare_image(
        uploaded_file
    )

    restored = restore_image(
        model,
        input_image
    )

    analysis = analyze_defects(
        input_image,
        restored
    )

    defects = analysis[
        "defects"
    ]

    high = sum(
        1
        for d in defects
        if d["Severity"] == "HIGH"
    )

    medium = sum(
        1
        for d in defects
        if d["Severity"] == "MEDIUM"
    )

    low = sum(
        1
        for d in defects
        if d["Severity"] == "LOW"
    )

    total_area = sum(
        d["Area_pixels"]
        for d in defects
    )

    total_defects = len(
        defects
    )

    final_pixels = analysis[
        "final_pixels"
    ]

    suspicious_area = (
        final_pixels
        /
        analysis[
            "refined_mask"
        ].size
        *
        100.0
    )

    # Final decision

    if high > 0:

        decision = "DEFECTIVE"

        reason = (
            "One or more HIGH "
            "severity anomalies "
            "were detected."
        )

    elif medium > 0:

        decision = "REVIEW"

        reason = (
            "MEDIUM severity anomalies "
            "require inspection review."
        )

    elif low > 0:

        decision = "ACCEPTABLE"

        reason = (
            "Only LOW severity anomalies "
            "were detected."
        )

    else:

        decision = "ACCEPTABLE"

        reason = (
            "No significant anomaly "
            "regions were detected."
        )

    analysis[
        "total_defects"
    ] = total_defects

    analysis[
        "high"
    ] = high

    analysis[
        "medium"
    ] = medium

    analysis[
        "low"
    ] = low

    analysis[
        "total_area"
    ] = total_area

    analysis[
        "suspicious_area"
    ] = suspicious_area

    analysis[
        "decision"
    ] = decision

    analysis[
        "reason"
    ] = reason

    return (
        input_image,
        analysis
    )


# ============================================================
# SAVE BATCH RESULT IMAGE
# ============================================================

def save_visualization(
    input_image,
    analysis,
    base_name
):

    restored = analysis[
        "restored"
    ]

    residual = analysis[
        "residual"
    ]

    refined_mask = analysis[
        "refined_mask"
    ]

    output_path = os.path.join(
        OUTPUT_DIR,
        base_name
        +
        "_batch_result.png"
    )

    fig = plt.figure(
        figsize=(10, 8)
    )

    plt.subplot(
        2,
        2,
        1
    )

    plt.imshow(
        input_image,
        cmap="gray"
    )

    plt.title(
        "Input Wafer"
    )

    plt.axis(
        "off"
    )

    plt.subplot(
        2,
        2,
        2
    )

    plt.imshow(
        restored,
        cmap="gray"
    )

    plt.title(
        "AI Restored"
    )

    plt.axis(
        "off"
    )

    plt.subplot(
        2,
        2,
        3
    )

    plt.imshow(
        residual,
        cmap="hot"
    )

    plt.title(
        "Residual Map"
    )

    plt.axis(
        "off"
    )

    plt.subplot(
        2,
        2,
        4
    )

    plt.imshow(
        input_image,
        cmap="gray"
    )

    if np.any(refined_mask):

        plt.contour(
            refined_mask,
            levels=[0.5],
            linewidths=1.5
        )

    plt.title(
        "Detected Defects"
    )

    plt.axis(
        "off"
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight"
    )

    plt.close()

    return output_path


# ============================================================
# SAVE BATCH CSV
# ============================================================

def save_batch_csv(
    results
):

    csv_path = os.path.join(
        OUTPUT_DIR,
        "batch_inspection_results.csv"
    )

    fieldnames = [

        "Input",

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

    with open(
        csv_path,
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for result in results:

            writer.writerow({

                "Input":
                    result["Input"],

                "Decision":
                    result["Decision"],

                "Total_Defects":
                    result["Total_Defects"],

                "HIGH":
                    result["HIGH"],

                "MEDIUM":
                    result["MEDIUM"],

                "LOW":
                    result["LOW"],

                "Defect_Area":
                    result["Defect_Area"],

                "Mean_Residual":
                    "%.6f"
                    %
                    result[
                        "Mean_Residual"
                    ],

                "Maximum_Residual":
                    "%.6f"
                    %
                    result[
                        "Maximum_Residual"
                    ],

                "Adaptive_Threshold":
                    "%.6f"
                    %
                    result[
                        "Adaptive_Threshold"
                    ],

                "Final_Defect_Pixels":
                    result[
                        "Final_Defect_Pixels"
                    ],

                "Suspicious_Area_Percent":
                    "%.4f"
                    %
                    result[
                        "Suspicious_Area_Percent"
                    ]
            })

    return csv_path


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.title(
    "🔬 WaferRevive-AI"
)

st.subheader(
    "Step 35 — Batch Wafer Inspection"
)

st.caption(
    "Inspect multiple wafers automatically "
    "using the WaferRevive-AI restoration "
    "and adaptive defect detection pipeline."
)


# ============================================================
# UPLOAD
# ============================================================

st.divider()

st.header(
    "📂 Upload Multiple Wafers"
)

uploaded_files = st.file_uploader(
    "Choose one or more wafer files",
    type=[
        "png",
        "jpg",
        "jpeg",
        "npy"
    ],
    accept_multiple_files=True
)


if not uploaded_files:

    st.info(
        "Upload multiple wafer images "
        "to begin batch inspection."
    )

    st.stop()


st.success(
    "Files selected: %d"
    %
    len(uploaded_files)
)


# ============================================================
# FILE LIST
# ============================================================

with st.expander(
    "📋 View selected wafers"
):

    for index, file in enumerate(
        uploaded_files,
        start=1
    ):

        st.write(
            "%d. %s"
            %
            (
                index,
                file.name
            )
        )


# ============================================================
# RUN BUTTON
# ============================================================

st.divider()

run_batch = st.button(
    "🚀 RUN BATCH INSPECTION",
    type="primary",
    use_container_width=True
)


# ============================================================
# RUN BATCH
# ============================================================

if run_batch:

    st.header(
        "⚙️ Batch Processing"
    )

    # Load model

    with st.spinner(
        "Loading AI model..."
    ):

        try:

            model = load_model()

        except Exception as error:

            st.error(
                "AI model could not be loaded."
            )

            st.exception(
                error
            )

            st.stop()


    progress = st.progress(
        0
    )

    status = st.empty()

    results = []

    detailed_results = []

    total_files = len(
        uploaded_files
    )


    # Process every wafer

    for index, uploaded_file in enumerate(
        uploaded_files
    ):

        status.write(
            "Inspecting %d/%d: %s"
            %
            (
                index + 1,
                total_files,
                uploaded_file.name
            )
        )

        try:

            input_image, analysis = inspect_wafer(
                model,
                uploaded_file
            )

            base_name = safe_name(
                uploaded_file.name
            )

            visualization_path = save_visualization(
                input_image,
                analysis,
                base_name
            )

            result = {

                "Input":
                    uploaded_file.name,

                "Decision":
                    analysis["decision"],

                "Total_Defects":
                    analysis["total_defects"],

                "HIGH":
                    analysis["high"],

                "MEDIUM":
                    analysis["medium"],

                "LOW":
                    analysis["low"],

                "Defect_Area":
                    analysis["total_area"],

                "Mean_Residual":
                    analysis["mean_residual"],

                "Maximum_Residual":
                    analysis["max_residual"],

                "Adaptive_Threshold":
                    analysis["threshold"],

                "Final_Defect_Pixels":
                    analysis["final_pixels"],

                "Suspicious_Area_Percent":
                    analysis["suspicious_area"],

                "Visualization":
                    visualization_path
            }

            results.append(
                result
            )

            detailed_results.append({

                "Input":
                    uploaded_file.name,

                "Input_Image":
                    input_image,

                "Analysis":
                    analysis,

                "Visualization":
                    visualization_path
            })

        except Exception as error:

            st.error(
                "Inspection failed for %s"
                %
                uploaded_file.name
            )

            st.exception(
                error
            )

        progress.progress(
            (index + 1)
            /
            total_files
        )


    status.success(
        "Batch inspection completed."
    )


    if not results:

        st.error(
            "No wafers were successfully inspected."
        )

        st.stop()


    # Save CSV

    csv_path = save_batch_csv(
        results
    )


    # ========================================================
    # BATCH SUMMARY
    # ========================================================

    st.divider()

    st.header(
        "📊 Batch Inspection Summary"
    )

    total_wafers = len(
        results
    )

    defective = sum(
        1
        for r in results
        if r["Decision"] == "DEFECTIVE"
    )

    review = sum(
        1
        for r in results
        if r["Decision"] == "REVIEW"
    )

    acceptable = sum(
        1
        for r in results
        if r["Decision"] == "ACCEPTABLE"
    )

    total_defects = sum(
        r["Total_Defects"]
        for r in results
    )

    total_high = sum(
        r["HIGH"]
        for r in results
    )

    total_medium = sum(
        r["MEDIUM"]
        for r in results
    )

    total_low = sum(
        r["LOW"]
        for r in results
    )

    total_area = sum(
        r["Defect_Area"]
        for r in results
    )


    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        st.metric(
            "Wafers",
            total_wafers
        )

    with c2:

        st.metric(
            "DEFECTIVE",
            defective
        )

    with c3:

        st.metric(
            "REVIEW",
            review
        )

    with c4:

        st.metric(
            "ACCEPTABLE",
            acceptable
        )

    with c5:

        st.metric(
            "Total Defects",
            total_defects
        )


    # ========================================================
    # SEVERITY SUMMARY
    # ========================================================

    st.subheader(
        "🚨 Batch Severity Summary"
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
            "Defect Area",
            "%d px"
            %
            total_area
        )


    # ========================================================
    # RESULTS TABLE
    # ========================================================

    st.divider()

    st.header(
        "📋 Batch Results"
    )

    dataframe = pd.DataFrame(
        results
    )

    display_columns = [

        "Input",

        "Decision",

        "Total_Defects",

        "HIGH",

        "MEDIUM",

        "LOW",

        "Defect_Area",

        "Mean_Residual",

        "Maximum_Residual",

        "Adaptive_Threshold",

        "Suspicious_Area_Percent"
    ]

    st.dataframe(
        dataframe[
            display_columns
        ],
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # WORST WAFER
    # ========================================================

    st.divider()

    st.header(
        "🏆 Highest Priority Wafer"
    )

    worst = max(
        results,
        key=lambda r: (
            r["HIGH"],
            r["Total_Defects"],
            r["Defect_Area"]
        )
    )

    w1, w2, w3, w4 = st.columns(4)

    with w1:

        st.write(
            "**Wafer**"
        )

        st.write(
            worst["Input"]
        )

    with w2:

        st.write(
            "**Decision**"
        )

        st.write(
            worst["Decision"]
        )

    with w3:

        st.write(
            "**Defects**"
        )

        st.write(
            worst["Total_Defects"]
        )

    with w4:

        st.write(
            "**HIGH**"
        )

        st.write(
            worst["HIGH"]
        )


    # ========================================================
    # DEFECT COUNT GRAPH
    # ========================================================

    st.divider()

    st.header(
        "📈 Defects by Wafer"
    )

    fig1 = plt.figure(
        figsize=(10, 4)
    )

    plt.bar(
        dataframe["Input"],
        dataframe["Total_Defects"]
    )

    plt.title(
        "Total Defects per Wafer"
    )

    plt.xlabel(
        "Wafer"
    )

    plt.ylabel(
        "Defects"
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

    plt.close(
        fig1
    )


    # ========================================================
    # SEVERITY GRAPH
    # ========================================================

    st.header(
        "📊 Batch Severity Distribution"
    )

    severity_values = [

        total_high,

        total_medium,

        total_low
    ]

    fig2 = plt.figure(
        figsize=(7, 4)
    )

    plt.bar(
        [
            "HIGH",
            "MEDIUM",
            "LOW"
        ],
        severity_values
    )

    plt.title(
        "Total Defect Severity"
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

    plt.close(
        fig2
    )


    # ========================================================
    # RESIDUAL GRAPH
    # ========================================================

    st.header(
        "📉 Residual Comparison"
    )

    fig3 = plt.figure(
        figsize=(10, 4)
    )

    plt.plot(
        dataframe["Input"],
        dataframe["Mean_Residual"],
        marker="o",
        label="Mean Residual"
    )

    plt.plot(
        dataframe["Input"],
        dataframe["Maximum_Residual"],
        marker="o",
        label="Maximum Residual"
    )

    plt.title(
        "Residual Measurements"
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

    plt.close(
        fig3
    )


    # ========================================================
    # INDIVIDUAL RESULTS
    # ========================================================

    st.divider()

    st.header(
        "🔍 Individual Wafer Results"
    )

    for item in detailed_results:

        analysis = item[
            "Analysis"
        ]

        with st.expander(
            "🔬 %s — %s"
            %
            (
                item["Input"],
                analysis["decision"]
            )
        ):

            a1, a2, a3, a4 = st.columns(4)

            with a1:

                st.metric(
                    "Defects",
                    analysis["total_defects"]
                )

            with a2:

                st.metric(
                    "HIGH",
                    analysis["high"]
                )

            with a3:

                st.metric(
                    "MEDIUM",
                    analysis["medium"]
                )

            with a4:

                st.metric(
                    "LOW",
                    analysis["low"]
                )

            st.write(
                "**Reason:** %s"
                %
                analysis["reason"]
            )

            st.image(
                item["Input_Image"],
                caption="Input Wafer",
                width=350
            )

            st.write(
                "### Residual Statistics"
            )

            r1, r2, r3 = st.columns(3)

            with r1:

                st.metric(
                    "Mean",
                    "%.6f"
                    %
                    analysis["mean_residual"]
                )

            with r2:

                st.metric(
                    "Maximum",
                    "%.6f"
                    %
                    analysis["max_residual"]
                )

            with r3:

                st.metric(
                    "Threshold",
                    "%.6f"
                    %
                    analysis["threshold"]
                )

            if analysis["defects"]:

                defect_table = []

                for defect in analysis[
                    "defects"
                ]:

                    defect_table.append({

                        "Rank":
                            defect["Rank"],

                        "Defect ID":
                            defect["Defect_ID"],

                        "Severity":
                            defect["Severity"],

                        "Priority Score":
                            round(
                                defect[
                                    "Priority_Score"
                                ],
                                4
                            ),

                        "Area":
                            defect[
                                "Area_pixels"
                            ],

                        "Maximum Error":
                            round(
                                defect[
                                    "Maximum_Error"
                                ],
                                6
                            )
                    })

                st.dataframe(
                    defect_table,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.success(
                    "No significant defects detected."
                )

            # Download individual visualization

            visualization_path = item[
                "Visualization"
            ]

            if os.path.exists(
                visualization_path
            ):

                with open(
                    visualization_path,
                    "rb"
                ) as file:

                    st.download_button(
                        "⬇️ Download Inspection Visualization",
                        data=file.read(),
                        file_name=os.path.basename(
                            visualization_path
                        ),
                        mime="image/png",
                        key="img_" + safe_name(
                            item["Input"]
                        )
                    )


    # ========================================================
    # DOWNLOAD BATCH CSV
    # ========================================================

    st.divider()

    st.header(
        "💾 Download Batch Results"
    )

    if os.path.exists(
        csv_path
    ):

        with open(
            csv_path,
            "rb"
        ) as file:

            st.download_button(
                "⬇️ Download Complete Batch CSV",
                data=file.read(),
                file_name="batch_inspection_results.csv",
                mime="text/csv",
                use_container_width=True
            )


    # ========================================================
    # DOWNLOAD VISUALIZATIONS
    # ========================================================

    st.subheader(
        "🖼️ Download Individual Results"
    )

    for result in results:

        visualization_path = result[
            "Visualization"
        ]

        if os.path.exists(
            visualization_path
        ):

            with open(
                visualization_path,
                "rb"
            ) as file:

                st.download_button(
                    "⬇️ " + result["Input"],
                    data=file.read(),
                    file_name=os.path.basename(
                        visualization_path
                    ),
                    mime="image/png",
                    key="download_result_" +
                    safe_name(
                        result["Input"]
                    )
                )


    # ========================================================
    # FINAL BATCH STATUS
    # ========================================================

    st.divider()

    if defective > 0:

        st.error(
            "🔴 BATCH STATUS: DEFECTIVE"
        )

        st.write(
            "%d of %d wafers contain HIGH severity defects."
            %
            (
                defective,
                total_wafers
            )
        )

    elif review > 0:

        st.warning(
            "🟡 BATCH STATUS: REVIEW REQUIRED"
        )

    else:

        st.success(
            "🟢 BATCH STATUS: ACCEPTABLE"
        )


    st.success(
        "✅ STEP 35 BATCH INSPECTION COMPLETED"
    )