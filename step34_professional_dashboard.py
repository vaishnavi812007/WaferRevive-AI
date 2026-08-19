import os
import sys
import csv
import re

import numpy as np
import torch
import streamlit as st
import matplotlib.pyplot as plt

from PIL import Image
from scipy import ndimage


# ============================================================
# WAFERREVIVE-AI
# STEP 32 - FULL NEW-WAFER INSPECTION
# ADAPTIVE DEFECT DETECTION
# ============================================================

st.set_page_config(
    page_title="WaferRevive-AI - Full Inspection",
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
    "full_inspection"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

sys.path.insert(
    0,
    os.path.join(BASE, "experiments")
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
# PREPARE INPUT IMAGE
# ============================================================

def prepare_image(uploaded_file):

    file_name = uploaded_file.name.lower()

    # --------------------------------------------------------
    # NUMPY INPUT
    # --------------------------------------------------------

    if file_name.endswith(".npy"):

        array = np.load(
            uploaded_file
        ).astype(
            np.float32
        )

    # --------------------------------------------------------
    # IMAGE INPUT
    # --------------------------------------------------------

    else:

        image = Image.open(
            uploaded_file
        ).convert("L")

        array = np.asarray(
            image,
            dtype=np.float32
        )

    # --------------------------------------------------------
    # REMOVE EXTRA CHANNELS
    # --------------------------------------------------------

    if array.ndim == 3:

        array = np.mean(
            array,
            axis=2
        )

    # --------------------------------------------------------
    # NORMALIZE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # MODEL INPUT SIZE
    # --------------------------------------------------------

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
# ADAPTIVE DEFECT ANALYSIS
# ============================================================

def analyze_defects(
    input_image,
    restored
):

    # --------------------------------------------------------
    # RESIZE RESTORED IMAGE TO INPUT SIZE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # RESIDUAL
    # --------------------------------------------------------

    residual = np.abs(
        restored_resized
        -
        input_image
    )

    residual = np.nan_to_num(
        residual
    )

    # --------------------------------------------------------
    # RESIDUAL STATISTICS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # MAD - MEDIAN ABSOLUTE DEVIATION
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ADAPTIVE THRESHOLD
    #
    # The detector no longer depends only on 0.08.
    # It adapts to the actual residual distribution.
    # --------------------------------------------------------

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

    # Prevent an excessively high threshold
    threshold = min(
        threshold,
        0.12
    )

    # --------------------------------------------------------
    # INITIAL MASK
    # --------------------------------------------------------

    initial_mask = (
        residual >= threshold
    )

    initial_pixels = int(
        np.sum(initial_mask)
    )

    # --------------------------------------------------------
    # MORPHOLOGICAL CLEANING
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CONNECTED COMPONENTS
    # --------------------------------------------------------

    labels, number = ndimage.label(
        cleaned_mask,
        structure=structure
    )

    defects = []

    refined_mask = np.zeros_like(
        cleaned_mask,
        dtype=bool
    )

    # --------------------------------------------------------
    # MINIMUM REGION AREA
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # FALLBACK DETECTION
    #
    # If morphology removed everything, use the strongest
    # residual regions so we can inspect what the AI sees.
    # --------------------------------------------------------

    if len(defects) == 0:

        fallback_threshold = max(
            0.025,
            p99
        )

        fallback_mask = (
            residual >=
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

    # --------------------------------------------------------
    # PRIORITY SCORING
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # RANKING
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # FINAL STATISTICS
    # --------------------------------------------------------

    final_pixels = int(
        np.sum(refined_mask)
    )

    return {

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
# DASHBOARD HEADER
# ============================================================

st.title(
    "🔬 WaferRevive-AI"
)

st.subheader(
    "Full New-Wafer Inspection"
)

st.caption(
    "AI Restoration • Adaptive Defect Detection • "
    "Defect Ranking • Automated Decision"
)


# ============================================================
# UPLOAD
# ============================================================

st.divider()

st.header(
    "📤 Upload New Wafer"
)

uploaded_file = st.file_uploader(
    "Choose a wafer image",
    type=[
        "png",
        "jpg",
        "jpeg",
        "npy"
    ]
)

if uploaded_file is None:

    st.info(
        "Upload a wafer image to begin inspection."
    )

    st.stop()


# ============================================================
# PREPARE INPUT
# ============================================================

try:

    input_image = prepare_image(
        uploaded_file
    )

except Exception as e:

    st.error(
        "Unable to read the uploaded wafer."
    )

    st.exception(e)

    st.stop()


st.success(
    "Uploaded: %s"
    % uploaded_file.name
)

st.image(
    input_image,
    caption="Input Wafer",
    clamp=True,
    width=500
)


# ============================================================
# RUN FULL INSPECTION
# ============================================================

run_button = st.button(
    "🚀 RUN FULL INSPECTION",
    type="primary",
    use_container_width=True
)


if run_button:

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------

    with st.spinner(
        "Loading AI model..."
    ):

        try:

            model = load_model()

        except Exception as e:

            st.error(
                "AI model could not be loaded."
            )

            st.exception(e)

            st.stop()

    # --------------------------------------------------------
    # RESTORATION
    # --------------------------------------------------------

    with st.spinner(
        "Running AI restoration..."
    ):

        try:

            restored = restore_image(
                model,
                input_image
            )

        except Exception as e:

            st.error(
                "AI restoration failed."
            )

            st.exception(e)

            st.stop()

    # --------------------------------------------------------
    # DEFECT ANALYSIS
    # --------------------------------------------------------

    with st.spinner(
        "Running adaptive defect analysis..."
    ):

        try:

            analysis = analyze_defects(
                input_image,
                restored
            )

        except Exception as e:

            st.error(
                "Defect analysis failed."
            )

            st.exception(e)

            st.stop()

    # --------------------------------------------------------
    # GET RESULTS
    # --------------------------------------------------------

    residual = analysis[
        "residual"
    ]

    initial_mask = analysis[
        "initial_mask"
    ]

    refined_mask = analysis[
        "refined_mask"
    ]

    defects = analysis[
        "defects"
    ]

    mean_residual = analysis[
        "mean_residual"
    ]

    median_residual = analysis[
        "median_residual"
    ]

    max_residual = analysis[
        "max_residual"
    ]

    p95 = analysis[
        "p95"
    ]

    p98 = analysis[
        "p98"
    ]

    p99 = analysis[
        "p99"
    ]

    mad = analysis[
        "mad"
    ]

    threshold = analysis[
        "threshold"
    ]

    initial_pixels = analysis[
        "initial_pixels"
    ]

    final_pixels = analysis[
        "final_pixels"
    ]

    minimum_area = analysis[
        "minimum_area"
    ]

    # --------------------------------------------------------
    # DEFECT COUNTS
    # --------------------------------------------------------

    total_defects = len(
        defects
    )

    total_area = sum(
        d["Area_pixels"]
        for d in defects
    )

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

    suspicious_area = (
        final_pixels
        /
        refined_mask.size
        *
        100.0
    )

    # --------------------------------------------------------
    # FINAL DECISION
    # --------------------------------------------------------

    if high > 0:

        decision = "DEFECTIVE"

        reason = (
            "One or more HIGH severity "
            "anomalies were detected."
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
            "No significant anomaly regions "
            "were detected."
        )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    st.divider()

    st.header(
        "📊 FINAL INSPECTION RESULT"
    )

    if decision == "DEFECTIVE":

        st.error(
            "🔴 DEFECTIVE"
        )

    elif decision == "REVIEW":

        st.warning(
            "🟡 REVIEW REQUIRED"
        )

    else:

        st.success(
            "🟢 ACCEPTABLE"
        )

    st.write(
        "**Reason:** %s"
        % reason
    )

    # --------------------------------------------------------
    # MAIN METRICS
    # --------------------------------------------------------

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        st.metric(
            "Defects",
            total_defects
        )

    with c2:

        st.metric(
            "HIGH",
            high
        )

    with c3:

        st.metric(
            "MEDIUM",
            medium
        )

    with c4:

        st.metric(
            "LOW",
            low
        )

    with c5:

        st.metric(
            "Defect Area",
            "%d px"
            % total_area
        )

    # --------------------------------------------------------
    # RESIDUAL STATISTICS
    # --------------------------------------------------------

    st.divider()

    st.header(
        "🔍 Adaptive Detection Statistics"
    )

    s1, s2, s3 = st.columns(3)

    with s1:

        st.metric(
            "Mean Residual",
            "%.6f"
            % mean_residual
        )

    with s2:

        st.metric(
            "Maximum Residual",
            "%.6f"
            % max_residual
        )

    with s3:

        st.metric(
            "Adaptive Threshold",
            "%.6f"
            % threshold
        )

    s4, s5, s6 = st.columns(3)

    with s4:

        st.metric(
            "Initial Suspicious Pixels",
            initial_pixels
        )

    with s5:

        st.metric(
            "Final Defect Pixels",
            final_pixels
        )

    with s6:

        st.metric(
            "Suspicious Area",
            "%.2f%%"
            % suspicious_area
        )

    st.caption(
        "Detection threshold is calculated from "
        "the residual distribution of the uploaded wafer."
    )

    # --------------------------------------------------------
    # DETAILED STATISTICS
    # --------------------------------------------------------

    with st.expander(
        "📈 Detailed residual statistics"
    ):

        st.write(
            "Median residual: %.6f"
            % median_residual
        )

        st.write(
            "95th percentile: %.6f"
            % p95
        )

        st.write(
            "98th percentile: %.6f"
            % p98
        )

        st.write(
            "99th percentile: %.6f"
            % p99
        )

        st.write(
            "Median absolute deviation: %.6f"
            % mad
        )

        st.write(
            "Minimum region area: %d pixels"
            % minimum_area
        )

    # --------------------------------------------------------
    # VISUALIZATION
    # --------------------------------------------------------

    st.divider()

    st.header(
        "🖼️ Inspection Visualization"
    )

    fig = plt.figure(
        figsize=(14, 10)
    )

    plt.subplot(
        2,
        3,
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
        3,
        2
    )

    plt.imshow(
        restored,
        cmap="gray"
    )

    plt.title(
        "AI Restored Wafer"
    )

    plt.axis(
        "off"
    )

    plt.subplot(
        2,
        3,
        3
    )

    plt.imshow(
        residual,
        cmap="hot"
    )

    plt.title(
        "Residual / Anomaly Map"
    )

    plt.axis(
        "off"
    )

    plt.subplot(
        2,
        3,
        4
    )

    plt.imshow(
        initial_mask,
        cmap="hot"
    )

    plt.title(
        "Initial Anomaly Mask"
    )

    plt.axis(
        "off"
    )

    plt.subplot(
        2,
        3,
        5
    )

    plt.imshow(
        refined_mask,
        cmap="hot"
    )

    plt.title(
        "Refined Defect Mask"
    )

    plt.axis(
        "off"
    )

    plt.subplot(
        2,
        3,
        6
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
        "Detected Defect Regions"
    )

    plt.axis(
        "off"
    )

    plt.tight_layout()

    # --------------------------------------------------------
    # SAVE VISUALIZATION
    # --------------------------------------------------------

    base_name = safe_name(
        uploaded_file.name
    )

    output_image = os.path.join(
        OUTPUT_DIR,
        base_name
        + "_full_inspection.png"
    )

    plt.savefig(
        output_image,
        dpi=200,
        bbox_inches="tight"
    )

    st.pyplot(
        fig
    )

    plt.close()

    # --------------------------------------------------------
    # DEFECT RANKING
    # --------------------------------------------------------

    st.divider()

    st.header(
        "🚨 DEFECT PRIORITY RANKING"
    )

    if defects:

        table_data = []

        for defect in defects:

            table_data.append({

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

                "Area (pixels)":
                    defect[
                        "Area_pixels"
                    ],

                "Max Error":
                    round(
                        defect[
                            "Maximum_Error"
                        ],
                        6
                    ),

                "Mean Error":
                    round(
                        defect[
                            "Mean_Error"
                        ],
                        6
                    )
            })

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No significant defect regions detected."
        )

    # --------------------------------------------------------
    # SAVE CSV
    # --------------------------------------------------------

    csv_path = os.path.join(
        OUTPUT_DIR,
        base_name
        + "_defect_analysis.csv"
    )

    with open(
        csv_path,
        "w",
        newline=""
    ) as file:

        fieldnames = [
            "Rank",
            "Defect_ID",
            "Severity",
            "Priority_Score",
            "Area_pixels",
            "Maximum_Error",
            "Mean_Error"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for defect in defects:

            writer.writerow({

                "Rank":
                    defect["Rank"],

                "Defect_ID":
                    defect["Defect_ID"],

                "Severity":
                    defect["Severity"],

                "Priority_Score":
                    "%.6f"
                    % defect[
                        "Priority_Score"
                    ],

                "Area_pixels":
                    defect[
                        "Area_pixels"
                    ],

                "Maximum_Error":
                    "%.6f"
                    % defect[
                        "Maximum_Error"
                    ],

                "Mean_Error":
                    "%.6f"
                    % defect[
                        "Mean_Error"
                    ]
            })

    # --------------------------------------------------------
    # SAVE FINAL REPORT
    # --------------------------------------------------------

    report_path = os.path.join(
        OUTPUT_DIR,
        base_name
        + "_final_inspection_report.txt"
    )

    with open(
        report_path,
        "w"
    ) as file:

        file.write(
            "============================================================\n"
        )

        file.write(
            "WAFERREVIVE-AI - FULL NEW-WAFER INSPECTION REPORT\n"
        )

        file.write(
            "============================================================\n\n"
        )

        file.write(
            "Input image          : %s\n"
            % uploaded_file.name
        )

        file.write(
            "Final decision       : %s\n"
            % decision
        )

        file.write(
            "Reason               : %s\n"
            % reason
        )

        file.write(
            "Total defects        : %d\n"
            % total_defects
        )

        file.write(
            "HIGH                 : %d\n"
            % high
        )

        file.write(
            "MEDIUM               : %d\n"
            % medium
        )

        file.write(
            "LOW                  : %d\n"
            % low
        )

        file.write(
            "Total defect area    : %d pixels\n"
            % total_area
        )

        file.write(
            "Suspicious area      : %.2f%%\n"
            % suspicious_area
        )

        file.write(
            "\n"
        )

        file.write(
            "RESIDUAL STATISTICS\n"
        )

        file.write(
            "------------------------------------------------------------\n"
        )

        file.write(
            "Mean residual        : %.6f\n"
            % mean_residual
        )

        file.write(
            "Median residual      : %.6f\n"
            % median_residual
        )

        file.write(
            "Maximum residual     : %.6f\n"
            % max_residual
        )

        file.write(
            "95th percentile      : %.6f\n"
            % p95
        )

        file.write(
            "98th percentile      : %.6f\n"
            % p98
        )

        file.write(
            "99th percentile      : %.6f\n"
            % p99
        )

        file.write(
            "MAD                  : %.6f\n"
            % mad
        )

        file.write(
            "Adaptive threshold   : %.6f\n"
            % threshold
        )

        file.write(
            "Initial suspicious   : %d pixels\n"
            % initial_pixels
        )

        file.write(
            "Final defect pixels  : %d pixels\n"
            % final_pixels
        )

        file.write(
            "\n"
        )

        file.write(
            "DEFECT PRIORITY RANKING\n"
        )

        file.write(
            "------------------------------------------------------------\n"
        )

        if defects:

            for defect in defects:

                file.write(
                    "Rank %d | Defect %d | %s | "
                    "Score %.4f | Area %d | "
                    "Max Error %.6f | Mean Error %.6f\n"
                    % (

                        defect["Rank"],

                        defect["Defect_ID"],

                        defect["Severity"],

                        defect["Priority_Score"],

                        defect["Area_pixels"],

                        defect["Maximum_Error"],

                        defect["Mean_Error"]
                    )
                )

        else:

            file.write(
                "No significant defect regions detected.\n"
            )

        file.write(
            "\n"
        )

        file.write(
            "============================================================\n"
        )

        file.write(
            "WAFERREVIVE-AI INSPECTION COMPLETE\n"
        )

        file.write(
            "============================================================\n"
        )

    # --------------------------------------------------------
    # SAVE MACHINE-READABLE SUMMARY
    # --------------------------------------------------------

    summary_path = os.path.join(
        OUTPUT_DIR,
        base_name
        + "_inspection_summary.csv"
    )

    with open(
        summary_path,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow(
            [
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
                "Initial_Suspicious_Pixels",
                "Final_Defect_Pixels",
                "Suspicious_Area_Percent"
            ]
        )

        writer.writerow(
            [
                uploaded_file.name,
                decision,
                total_defects,
                high,
                medium,
                low,
                total_area,
                "%.6f"
                % mean_residual,
                "%.6f"
                % max_residual,
                "%.6f"
                % threshold,
                initial_pixels,
                final_pixels,
                "%.4f"
                % suspicious_area
            ]
        )

    # --------------------------------------------------------
    # OUTPUT FILES
    # --------------------------------------------------------

    st.divider()

    st.header(
        "💾 Saved Inspection Results"
    )

    st.write(
        "Visualization:"
    )

    st.code(
        output_image
    )

    st.write(
        "Defect analysis:"
    )

    st.code(
        csv_path
    )

    st.write(
        "Final report:"
    )

    st.code(
        report_path
    )

    st.write(
        "Machine-readable summary:"
    )

    st.code(
        summary_path
    )

    # --------------------------------------------------------
    # COMPLETION
    # --------------------------------------------------------

# ============================================================
# DOWNLOAD RESULTS
# ============================================================

st.divider()

st.header("💾 Download Results")

st.write(
    "Download the files generated by the latest inspection."
)

# Find the latest inspection files
import glob

full_inspection_dir = r"D:\WaferRevive-AI\results\full_inspection"

if os.path.exists(full_inspection_dir):

    inspection_files = sorted(
        glob.glob(
            os.path.join(
                full_inspection_dir,
                "*"
            )
        ),
        key=os.path.getmtime,
        reverse=True
    )

    if inspection_files:

        st.subheader("📁 Latest Inspection Files")

        for file_path in inspection_files[:10]:

            if not os.path.isfile(file_path):
                continue

            file_name = os.path.basename(
                file_path
            )

            try:

                with open(
                    file_path,
                    "rb"
                ) as download_file:

                    file_data = download_file.read()

                st.download_button(
                    label="⬇️ Download " + file_name,
                    data=file_data,
                    file_name=file_name,
                    key="download_" + file_name,
                    use_container_width=True
                )

            except Exception as error:

                st.warning(
                    "Could not prepare " +
                    file_name +
                    ": " +
                    str(error)
                )

    else:

        st.info(
            "No inspection result files found yet."
        )

else:

    st.info(
        "The inspection results folder does not exist yet."
    )
    st.success(
        "✅ STEP 32 COMPLETED SUCCESSFULLY"
    )