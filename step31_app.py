import os
import sys
import numpy as np
import streamlit as st
import torch
import matplotlib.pyplot as plt

from PIL import Image

# ============================================================
# WAFERREVIVE-AI
# STEP 31B - NEW WAFER INSPECTION APPLICATION
# ============================================================

st.set_page_config(
    page_title="WaferRevive-AI",
    page_icon="🔬",
    layout="wide"
)

BASE = r"D:\WaferRevive-AI"

MODEL_PATH = os.path.join(
    BASE,
    "models",
    "best_model.pth"
)

OUTPUT_DIR = os.path.join(
    BASE,
    "results",
    "new_inspections"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

# ============================================================
# LOAD MODEL
# ============================================================

sys.path.insert(
    0,
    os.path.join(BASE, "experiments")
)

from step7_model import WaferRestorationNet


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
# IMAGE PREPARATION
# ============================================================

def prepare_image(uploaded_file):

    name = uploaded_file.name.lower()

    if name.endswith(".npy"):

        array = np.load(
            uploaded_file
        ).astype(
            np.float32
        )

    else:

        image = Image.open(
            uploaded_file
        ).convert("L")

        image = image.resize(
            (128, 128),
            Image.Resampling.BILINEAR
        )

        array = np.asarray(
            image,
            dtype=np.float32
        )

        if array.max() > 1.0:

            array = array / 255.0

    if array.ndim == 3:

        array = np.mean(
            array,
            axis=2
        )

    if array.shape != (128, 128):

        image = Image.fromarray(
            np.clip(
                array * 255.0,
                0,
                255
            ).astype(np.uint8)
        )

        image = image.resize(
            (128, 128),
            Image.Resampling.BILINEAR
        )

        array = np.asarray(
            image,
            dtype=np.float32
        ) / 255.0

    array = np.nan_to_num(
        array
    )

    minimum = array.min()
    maximum = array.max()

    if maximum > 1.0:

        array = (
            array - minimum
        ) / (
            maximum - minimum + 1e-8
        )

    return array.astype(
        np.float32
    )


# ============================================================
# AI RESTORATION
# ============================================================

def restore_image(
    model,
    image_array
):

    tensor = torch.from_numpy(
        image_array
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
        restored
    )

    return restored


# ============================================================
# RESIZE ARRAY
# ============================================================

def resize_array(
    array,
    width,
    height
):

    minimum = array.min()
    maximum = array.max()

    if maximum <= 1.0:

        temp = (
            array * 255.0
        )

    else:

        temp = (
            array - minimum
        ) / (
            maximum - minimum + 1e-8
        ) * 255.0

    temp = np.clip(
        temp,
        0,
        255
    ).astype(
        np.uint8
    )

    image = Image.fromarray(
        temp
    )

    image = image.resize(
        (width, height),
        Image.Resampling.BILINEAR
    )

    return (
        np.asarray(
            image,
            dtype=np.float32
        ) / 255.0
    )


# ============================================================
# HEADER
# ============================================================

st.title(
    "🔬 WaferRevive-AI"
)

st.subheader(
    "Automated Wafer Inspection System"
)

st.caption(
    "Upload a new wafer image and run AI restoration"
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
        "Upload a PNG, JPG, JPEG, or NPY wafer image to begin inspection."
    )

    st.stop()


# ============================================================
# SHOW INPUT
# ============================================================

st.success(
    "Image uploaded: %s"
    % uploaded_file.name
)

image_array = prepare_image(
    uploaded_file
)

left, right = st.columns(2)

with left:

    st.subheader(
        "Uploaded Wafer"
    )

    st.image(
        image_array,
        clamp=True,
        use_container_width=True
    )

with right:

    st.subheader(
        "Input Information"
    )

    st.write(
        "**Filename:**",
        uploaded_file.name
    )

    st.write(
        "**Input size:**",
        "%d × %d"
        % (
            image_array.shape[1],
            image_array.shape[0]
        )
    )

    st.write(
        "**Model input:**",
        "128 × 128 grayscale"
    )


# ============================================================
# RUN BUTTON
# ============================================================

st.divider()

run_button = st.button(
    "🚀 RUN AI INSPECTION",
    type="primary",
    use_container_width=True
)


if run_button:

    with st.spinner(
        "Running WaferRevive-AI..."
    ):

        try:

            # ------------------------------------------------
            # LOAD MODEL
            # ------------------------------------------------

            model = load_model()

            # ------------------------------------------------
            # RESTORATION
            # ------------------------------------------------

            restored = restore_image(
                model,
                image_array
            )

            # ------------------------------------------------
            # RESIZE RESTORATION TO INPUT
            # ------------------------------------------------

            restored_for_comparison = resize_array(
                restored,
                image_array.shape[1],
                image_array.shape[0]
            )

            # ------------------------------------------------
            # RESIDUAL / ANOMALY ANALYSIS
            # ------------------------------------------------

            residual = np.abs(
                restored_for_comparison
                - image_array
            )

            mean_residual = float(
                np.mean(residual)
            )

            maximum_residual = float(
                np.max(residual)
            )

            threshold = 0.08

            anomaly_mask = (
                residual > threshold
            )

            anomaly_pixels = int(
                np.sum(anomaly_mask)
            )

            total_pixels = int(
                anomaly_mask.size
            )

            suspicious_area = (
                anomaly_pixels
                / total_pixels
                * 100.0
            )

            # ------------------------------------------------
            # SAVE RESULT
            # ------------------------------------------------

            safe_name = os.path.splitext(
                uploaded_file.name
            )[0]

            output_path = os.path.join(
                OUTPUT_DIR,
                safe_name
                + "_inspection.png"
            )

            # ------------------------------------------------
            # VISUALIZATION
            # ------------------------------------------------

            fig = plt.figure(
                figsize=(12, 8)
            )

            plt.subplot(
                2,
                2,
                1
            )

            plt.imshow(
                image_array,
                cmap="gray"
            )

            plt.title(
                "Uploaded Wafer"
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
                "AI Restored Wafer"
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
                "Residual / Anomaly Map"
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
                anomaly_mask,
                cmap="hot"
            )

            plt.title(
                "Suspicious Regions: %.2f%%"
                % suspicious_area
            )

            plt.axis(
                "off"
            )

            plt.tight_layout()

            plt.savefig(
                output_path,
                dpi=200,
                bbox_inches="tight"
            )

            plt.close()
        except Exception as e:
            st.error("AI inspection failed.")
            st.exception(e)
            st.stop()

    # ========================================================
    # RESULTS
    # ========================================================

    st.divider()

    st.header(
        "📊 AI Inspection Result"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Mean Residual",
            "%.6f"
            % mean_residual
        )

    with col2:

        st.metric(
            "Maximum Residual",
            "%.6f"
            % maximum_residual
        )

    with col3:

        st.metric(
            "Suspicious Pixels",
            anomaly_pixels
        )

    with col4:

        st.metric(
            "Suspicious Area",
            "%.2f%%"
            % suspicious_area
        )

    # ========================================================
    # SHOW RESTORED IMAGE
    # ========================================================

    st.divider()

    st.header(
        "🧠 AI Restoration"
    )

    st.image(
        restored,
        clamp=True,
        caption="AI Restored Wafer",
        use_container_width=True
    )

    # ========================================================
    # SHOW ANALYSIS
    # ========================================================

    st.divider()

    st.header(
        "🔎 Residual Analysis"
    )

    result_left, result_right = st.columns(2)

    with result_left:

        st.image(
            residual,
            clamp=True,
            caption="Residual / Anomaly Map",
            use_container_width=True
        )

    with result_right:

        st.image(
            anomaly_mask,
            clamp=True,
            caption="Suspicious Region Mask",
            use_container_width=True
        )

    # ========================================================
    # STATUS
    # ========================================================

    st.divider()

    st.header(
        "🏭 Inspection Status"
    )

    if suspicious_area > 1.0:

        st.error(
            "⚠️ HIGH SUSPICIOUS AREA"
        )

    elif suspicious_area > 0.2:

        st.warning(
            "⚠️ SUSPICIOUS WAFER"
        )

    else:

        st.success(
            "✅ LOW SUSPICIOUS AREA"
        )

    st.caption(
        "Note: For a newly uploaded wafer, this stage uses "
        "restoration residual analysis because no ground-truth "
        "image is available. It is not the same as the "
        "ground-truth error calculation used in Steps 23–30."
    )

    # ========================================================
    # OUTPUT
    # ========================================================

    st.divider()

    st.header(
        "💾 Inspection Output"
    )

    st.write(
        "Result saved to:"
    )

    st.code(
        output_path
    )

    st.image(
        output_path,
        caption="Complete New-Wafer Inspection Visualization",
        use_container_width=True
    )

    st.success(
        "New wafer inspection completed successfully."
    )