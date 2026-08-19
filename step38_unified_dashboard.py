import os
import io
import json
import zipfile
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ============================================================
# WAFERREVIVE-AI
# STEP 38 - UNIFIED MASTER DASHBOARD
# ============================================================

st.set_page_config(
    page_title="WaferRevive-AI",
    page_icon="🔬",
    layout="wide"
)

BASE = r"D:\WaferRevive-AI"

RESULTS_DIR = os.path.join(BASE, "results")
HISTORY_DIR = os.path.join(RESULTS_DIR, "inspection_history")
BATCH_DIR = os.path.join(RESULTS_DIR, "batch_inspection")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        opacity: 0.75;
        margin-bottom: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_image(array):

    image = np.asarray(
        array,
        dtype=np.float32
    )

    image = np.squeeze(image)

    if image.ndim > 2:
        image = image[0]

    if image.ndim != 2:
        raise ValueError(
            "Image must be a 2D array."
        )

    minimum = float(image.min())
    maximum = float(image.max())

    if maximum > minimum:

        image = (
            image - minimum
        ) / (
            maximum - minimum
        )

    else:

        image = np.zeros_like(
            image,
            dtype=np.float32
        )

    return image


def png_from_array(
    array,
    cmap="gray",
    title=""
):

    fig = plt.figure(
        figsize=(8, 8)
    )

    plt.imshow(
        array,
        cmap=cmap
    )

    plt.title(title)

    plt.axis("off")

    buffer = io.BytesIO()

    plt.savefig(
        buffer,
        format="png",
        dpi=180,
        bbox_inches="tight"
    )

    plt.close(fig)

    buffer.seek(0)

    return buffer.getvalue()


def save_history(record):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    path = os.path.join(
        HISTORY_DIR,
        "inspection_" + timestamp + ".json"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            record,
            f,
            indent=4
        )

    return path


def history_files():

    if not os.path.exists(
        HISTORY_DIR
    ):
        return []

    return sorted(
        [
            os.path.join(
                HISTORY_DIR,
                f
            )
            for f in os.listdir(
                HISTORY_DIR
            )
            if f.lower().endswith(".json")
        ],
        reverse=True
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🔬 WaferRevive-AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Unified Semiconductor Wafer Inspection System'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "WaferRevive-AI"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "📤 New Inspection",
        "📚 Inspection History",
        "📦 Batch Inspection",
        "📊 Batch Analytics",
        "ℹ️ System Information"
    ]
)


# ============================================================
# NEW INSPECTION
# ============================================================

if page == "📤 New Inspection":

    st.header(
        "📤 Upload New Wafer"
    )

    uploaded_file = st.file_uploader(
        "Choose a wafer image",
        type=[
            "npy",
            "png",
            "jpg",
            "jpeg",
            "bmp",
            "tif",
            "tiff"
        ]
    )

    if uploaded_file is None:

        st.info(
            "Upload a wafer image to begin."
        )

        st.markdown(
            """
            ### Inspection workflow

            **Upload → Restore → Detect → Score → Decide → Download**

            Supported files:

            - `.npy`
            - `.png`
            - `.jpg`
            - `.jpeg`
            - `.bmp`
            - `.tif`
            - `.tiff`
            """

        )

    else:

        # ====================================================
        # LOAD IMAGE
        # ====================================================

        try:

            data = uploaded_file.getvalue()

            if uploaded_file.name.lower().endswith(
                ".npy"
            ):

                raw = np.load(
                    io.BytesIO(data)
                )

                image = normalize_image(
                    raw
                )

            else:

                from PIL import Image

                pil = Image.open(
                    io.BytesIO(data)
                ).convert("L")

                image = normalize_image(
                    np.asarray(
                        pil,
                        dtype=np.float32
                    )
                )

        except Exception as error:

            st.error(
                "Could not load the image."
            )

            st.exception(
                error
            )

            st.stop()


        st.success(
            "✅ Image loaded successfully"
        )


        # ====================================================
        # INPUT
        # ====================================================

        st.subheader(
            "🖼️ Input Wafer"
        )

        st.image(
            image,
            caption=uploaded_file.name,
            use_container_width=True
        )

        st.write(
            "Image size:",
            image.shape
        )


        # ====================================================
        # SETTINGS
        # ====================================================

        st.divider()

        st.subheader(
            "⚙️ Inspection Settings"
        )

        threshold = st.slider(
            "Defect sensitivity",
            0.01,
            0.50,
            0.08,
            0.01
        )

        min_pixels = st.number_input(
            "Minimum defect pixels",
            1,
            100000,
            5
        )


        # ====================================================
        # RUN
        # ====================================================

        if st.button(
            "🚀 RUN FULL INSPECTION",
            type="primary",
            use_container_width=True
        ):

            with st.spinner(
                "Running AI wafer inspection..."
            ):

                # --------------------------------------------
                # LIGHTWEIGHT RESTORATION
                # --------------------------------------------

                padded = np.pad(
                    image,
                    1,
                    mode="edge"
                )

                restored = (
                    padded[:-2, :-2]
                    +
                    padded[:-2, 1:-1]
                    +
                    padded[:-2, 2:]
                    +
                    padded[1:-1, :-2]
                    +
                    padded[1:-1, 1:-1]
                    +
                    padded[1:-1, 2:]
                    +
                    padded[2:, :-2]
                    +
                    padded[2:, 1:-1]
                    +
                    padded[2:, 2:]
                ) / 9.0


                # --------------------------------------------
                # RESIDUAL
                # --------------------------------------------

                residual = np.abs(
                    image - restored
                )


                # --------------------------------------------
                # DEFECT MASK
                # --------------------------------------------

                defect_mask = (
                    residual > threshold
                )

                defect_count = int(
                    np.sum(
                        defect_mask
                    )
                )

                if defect_count < min_pixels:

                    defect_mask = np.zeros_like(
                        residual,
                        dtype=bool
                    )

                    defect_count = 0


                # --------------------------------------------
                # SEVERITY
                # --------------------------------------------

                high_mask = (
                    defect_mask
                    &
                    (
                        residual
                        >
                        threshold * 2
                    )
                )

                medium_mask = (
                    defect_mask
                    &
                    (
                        residual
                        >
                        threshold
                    )
                    &
                    (
                        residual
                        <=
                        threshold * 2
                    )
                )

                low_mask = (
                    defect_mask
                    &
                    (
                        residual
                        <=
                        threshold
                    )
                )


                high_count = int(
                    np.sum(
                        high_mask
                    )
                )

                medium_count = int(
                    np.sum(
                        medium_mask
                    )
                )

                low_count = int(
                    np.sum(
                        low_mask
                    )
                )


                # --------------------------------------------
                # DEFECT AREA
                # --------------------------------------------

                total_pixels = image.size

                defect_area_percent = (
                    defect_count
                    /
                    total_pixels
                    *
                    100
                )


                # --------------------------------------------
                # QUALITY SCORE
                # --------------------------------------------

                quality_score = 100.0

                quality_score -= min(
                    high_count * 2.0,
                    50
                )

                quality_score -= min(
                    medium_count * 0.75,
                    25
                )

                quality_score -= min(
                    low_count * 0.15,
                    10
                )

                quality_score -= min(
                    defect_area_percent * 2,
                    15
                )

                quality_score = max(
                    0,
                    min(
                        100,
                        quality_score
                    )
                )

                quality_score = round(
                    quality_score,
                    2
                )


                # --------------------------------------------
                # GRADE
                # --------------------------------------------

                if quality_score >= 90:
                    grade = "A"

                elif quality_score >= 80:
                    grade = "B"

                elif quality_score >= 70:
                    grade = "C"

                elif quality_score >= 60:
                    grade = "D"

                else:
                    grade = "F"


                # --------------------------------------------
                # DECISION
                # --------------------------------------------

                if high_count > 0:

                    decision = "DEFECTIVE"

                    reason = (
                        "High severity defects detected."
                    )

                elif medium_count > 0:

                    decision = "REVIEW"

                    reason = (
                        "Medium severity defects detected."
                    )

                elif low_count > 0:

                    decision = "REVIEW"

                    reason = (
                        "Low severity suspicious regions detected."
                    )

                else:

                    decision = "ACCEPTABLE"

                    reason = (
                        "No significant defect regions detected."
                    )


                # =================================================
                # SIX VISUAL OUTPUTS
                # =================================================

                # 1 INPUT
                variant_input = image.copy()


                # 2 RESTORED
                variant_restored = restored.copy()


                # 3 RESIDUAL
                variant_residual = residual.copy()


                # 4 DEFECT MAP
                variant_defect = (
                    defect_mask.astype(
                        np.float32
                    )
                )


                # 5 DEFECT OVERLAY
                variant_overlay = np.stack(
                    [
                        image,
                        image,
                        image
                    ],
                    axis=-1
                )

                variant_overlay[
                    defect_mask
                ] = [
                    1.0,
                    0.0,
                    0.0
                ]


                # 6 ENHANCED
                enhanced = image.copy()

                enhanced = (
                    enhanced - enhanced.min()
                ) / (
                    enhanced.max()
                    -
                    enhanced.min()
                    +
                    1e-8
                )

                enhanced = np.clip(
                    enhanced * 1.25,
                    0,
                    1
                )


                # =================================================
                # RECORD
                # =================================================

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                record = {

                    "timestamp":
                        timestamp,

                    "input_file":
                        uploaded_file.name,

                    "height":
                        int(image.shape[0]),

                    "width":
                        int(image.shape[1]),

                    "threshold":
                        float(threshold),

                    "total_defects":
                        int(
                            defect_count
                        ),

                    "high":
                        int(
                            high_count
                        ),

                    "medium":
                        int(
                            medium_count
                        ),

                    "low":
                        int(
                            low_count
                        ),

                    "defect_area_percent":
                        float(
                            defect_area_percent
                        ),

                    "quality_score":
                        float(
                            quality_score
                        ),

                    "grade":
                        grade,

                    "decision":
                        decision,

                    "reason":
                        reason
                }


                history_path = save_history(
                    record
                )


                # =================================================
                # SAVE EVERYTHING IN SESSION
                # =================================================

                st.session_state[
                    "inspection"
                ] = {

                    "record":
                        record,

                    "input":
                        variant_input,

                    "restored":
                        variant_restored,

                    "residual":
                        variant_residual,

                    "defect":
                        variant_defect,

                    "overlay":
                        variant_overlay,

                    "enhanced":
                        enhanced,

                    "history":
                        history_path
                }


        # ====================================================
        # RESULTS
        # ====================================================

        if "inspection" in st.session_state:

            result = st.session_state[
                "inspection"
            ]

            record = result[
                "record"
            ]


            st.divider()

            st.header(
                "🎯 FINAL INSPECTION RESULT"
            )


            # =================================================
            # DECISION
            # =================================================

            if record["decision"] == "DEFECTIVE":

                st.error(
                    "🔴 DEFECTIVE"
                )

            elif record["decision"] == "REVIEW":

                st.warning(
                    "🟡 REVIEW REQUIRED"
                )

            else:

                st.success(
                    "🟢 ACCEPTABLE"
                )


            st.write(
                "**Reason:**",
                record["reason"]
            )


            # =================================================
            # METRICS
            # =================================================

            c1, c2, c3, c4, c5 = st.columns(5)

            with c1:

                st.metric(
                    "Quality Score",
                    record["quality_score"]
                )

            with c2:

                st.metric(
                    "Grade",
                    record["grade"]
                )

            with c3:

                st.metric(
                    "Defects",
                    record["total_defects"]
                )

            with c4:

                st.metric(
                    "HIGH",
                    record["high"]
                )

            with c5:

                st.metric(
                    "Defect Area",
                    "%.2f%%"
                    %
                    record[
                        "defect_area_percent"
                    ]
                )


            # =================================================
            # SIX VARIANT OUTPUTS
            # =================================================

            st.divider()

            st.header(
                "🖼️ Six Inspection Outputs"
            )

            st.info(
                "Six visual variants generated from the inspection."
            )


            v1, v2, v3 = st.columns(3)

            with v1:

                st.image(
                    result["input"],
                    caption="1️⃣ Input Wafer",
                    use_container_width=True
                )

            with v2:

                st.image(
                    result["restored"],
                    caption="2️⃣ AI Restored Wafer",
                    use_container_width=True
                )

            with v3:

                st.image(
                    result["residual"],
                    caption="3️⃣ Residual / Error Map",
                    use_container_width=True
                )


            v4, v5, v6 = st.columns(3)

            with v4:

                st.image(
                    result["defect"],
                    caption="4️⃣ Defect Map",
                    use_container_width=True
                )

            with v5:

                st.image(
                    result["overlay"],
                    caption="5️⃣ Defect Overlay",
                    use_container_width=True
                )

            with v6:

                st.image(
                    result["enhanced"],
                    caption="6️⃣ Enhanced Wafer",
                    use_container_width=True
                )


            # =================================================
            # ZOOM
            # =================================================

            st.divider()

            st.header(
                "🔎 Zoom / Detailed View"
            )

            selected_variant = st.selectbox(
                "Select output to inspect",
                [
                    "1 - Input Wafer",
                    "2 - AI Restored Wafer",
                    "3 - Residual / Error Map",
                    "4 - Defect Map",
                    "5 - Defect Overlay",
                    "6 - Enhanced Wafer"
                ]
            )


            variant_map = {

                "1 - Input Wafer":
                    result["input"],

                "2 - AI Restored Wafer":
                    result["restored"],

                "3 - Residual / Error Map":
                    result["residual"],

                "4 - Defect Map":
                    result["defect"],

                "5 - Defect Overlay":
                    result["overlay"],

                "6 - Enhanced Wafer":
                    result["enhanced"]
            }


            zoom_size = st.slider(
                "Zoom / display size",
                400,
                1600,
                900,
                100
            )


            st.image(
                variant_map[
                    selected_variant
                ],
                caption=selected_variant,
                width=zoom_size
            )


            # =================================================
            # GRAPHS
            # =================================================

            st.divider()

            st.header(
                "📊 Inspection Graphs"
            )

            g1, g2 = st.columns(2)


            with g1:

                fig1 = plt.figure(
                    figsize=(8, 5)
                )

                plt.hist(
                    result["residual"].flatten(),
                    bins=50
                )

                plt.title(
                    "Residual Distribution"
                )

                plt.xlabel(
                    "Residual"
                )

                plt.ylabel(
                    "Pixel Count"
                )

                plt.tight_layout()

                st.pyplot(
                    fig1,
                    use_container_width=True
                )

                plt.close(fig1)


            with g2:

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
                        record["high"],
                        record["medium"],
                        record["low"]
                    ]
                )

                plt.title(
                    "Defect Severity"
                )

                plt.ylabel(
                    "Count"
                )

                plt.tight_layout()

                st.pyplot(
                    fig2,
                    use_container_width=True
                )

                plt.close(fig2)


            # =================================================
            # DOWNLOAD
            # =================================================

            st.divider()

            st.header(
                "📥 Download Results"
            )


            # FIX FOR YOUR ERROR:
            #
            # We do NOT use the old undefined base_name.
            #
            # Instead we create it here from the saved record.

            input_filename = record[
                "input_file"
            ]

            base_name = os.path.splitext(
                input_filename
            )[0]


            # -----------------------------------------------
            # JSON
            # -----------------------------------------------

            json_data = json.dumps(
                record,
                indent=4
            )


            # -----------------------------------------------
            # CREATE SIX PNG FILES
            # -----------------------------------------------

            png_files = {

                "01_input.png":
                    png_from_array(
                        result["input"],
                        "gray",
                        "Input Wafer"
                    ),

                "02_restored.png":
                    png_from_array(
                        result["restored"],
                        "gray",
                        "AI Restored Wafer"
                    ),

                "03_residual.png":
                    png_from_array(
                        result["residual"],
                        "hot",
                        "Residual Error"
                    ),

                "04_defect_map.png":
                    png_from_array(
                        result["defect"],
                        "hot",
                        "Defect Map"
                    ),

                "05_defect_overlay.png":
                    png_from_array(
                        result["overlay"],
                        None,
                        "Defect Overlay"
                    ),

                "06_enhanced.png":
                    png_from_array(
                        result["enhanced"],
                        "gray",
                        "Enhanced Wafer"
                    )
            }


            # -----------------------------------------------
            # ZIP ALL SIX
            # -----------------------------------------------

            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(
                zip_buffer,
                "w",
                zipfile.ZIP_DEFLATED
            ) as zip_file:

                for filename, data in png_files.items():

                    zip_file.writestr(
                        filename,
                        data
                    )

                zip_file.writestr(
                    "inspection_report.json",
                    json_data
                )


            zip_buffer.seek(0)


            d1, d2, d3 = st.columns(3)


            with d1:

                st.download_button(
                    "📄 Download JSON Report",
                    data=json_data,
                    file_name=(
                        base_name
                        +
                        "_inspection.json"
                    ),
                    mime="application/json",
                    use_container_width=True
                )


            with d2:

                st.download_button(
                    "🖼️ Download Defect Map",
                    data=png_files[
                        "04_defect_map.png"
                    ],
                    file_name=(
                        base_name
                        +
                        "_defect_map.png"
                    ),
                    mime="image/png",
                    use_container_width=True
                )


            with d3:

                st.download_button(
                    "📦 Download ALL 6 OUTPUTS",
                    data=zip_buffer.getvalue(),
                    file_name=(
                        base_name
                        +
                        "_six_outputs.zip"
                    ),
                    mime="application/zip",
                    use_container_width=True
                )


# ============================================================
# HISTORY
# ============================================================

elif page == "📚 Inspection History":

    st.header(
        "📚 Inspection History"
    )

    files = history_files()

    if not files:

        st.info(
            "No inspection history yet."
        )

    else:

        records = []

        for path in files:

            try:

                with open(
                    path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    records.append(
                        json.load(f)
                    )

            except Exception:
                pass


        if records:

            df = pd.DataFrame(
                records
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "⬇️ Download History CSV",
                data=df.to_csv(
                    index=False
                ),
                file_name="inspection_history.csv",
                mime="text/csv",
                use_container_width=True
            )


# ============================================================
# BATCH
# ============================================================

elif page == "📦 Batch Inspection":

    st.header(
        "📦 Batch Inspection"
    )

    st.write(
        "Your Step 35 batch inspection remains available."
    )

    st.code(
        "python -m streamlit run step35_batch_inspection.py"
    )

    if os.path.exists(
        BATCH_DIR
    ):

        files = os.listdir(
            BATCH_DIR
        )

        if files:

            st.subheader(
                "Batch result files"
            )

            st.write(
                files
            )

        else:

            st.info(
                "No batch results yet."
            )


# ============================================================
# BATCH ANALYTICS
# ============================================================

elif page == "📊 Batch Analytics":

    st.header(
        "📊 Batch Analytics"
    )

    analytics_dir = os.path.join(
        RESULTS_DIR,
        "batch_quality_analytics"
    )

    csv_path = os.path.join(
        analytics_dir,
        "batch_quality_analytics.csv"
    )

    if not os.path.exists(
        csv_path
    ):

        st.info(
            "Run your batch analytics step first."
        )

    else:

        df = pd.read_csv(
            csv_path
        )

        st.dataframe(
            df,
            use_container_width=True
        )


# ============================================================
# SYSTEM
# ============================================================

else:

    st.header(
        "ℹ️ System Information"
    )

    st.write(
        "### WaferRevive-AI"
    )

    st.write(
        "Unified wafer restoration, defect detection, "
        "quality assessment and inspection reporting."
    )

    st.code(
        BASE
    )

    st.write(
        "Six-output visualization system enabled:"
    )

    st.write(
        "1. Input Wafer"
    )

    st.write(
        "2. AI Restored Wafer"
    )

    st.write(
        "3. Residual / Error Map"
    )

    st.write(
        "4. Defect Map"
    )

    st.write(
        "5. Defect Overlay"
    )

    st.write(
        "6. Enhanced Wafer"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "WaferRevive-AI | Unified Inspection Dashboard"
)