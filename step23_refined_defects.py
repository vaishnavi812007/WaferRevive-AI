import os
import csv
import numpy as np
import torch
import matplotlib.pyplot as plt

from skimage.measure import label, regionprops
from step7_model import WaferRestorationNet


# ============================================================
# WAFERREVIVE-AI
# STEP 23 - REFINED DEFECT DETECTION
# ============================================================

print("============================================================")
print("WAFERREVIVE-AI - STEP 23")
print("REFINED DEFECT DETECTION")
print("============================================================")


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = r"D:\WaferRevive-AI\models\best_model.pth"

NOISY_PATH = r"D:\wafer\train\train\NoisyLR\002850.npy"

GT_PATH = r"D:\wafer\train\train\GT\002850.npy"

OUTPUT_DIR = r"D:\WaferRevive-AI\results\refined_defects"

os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_IMAGE = os.path.join(
    OUTPUT_DIR,
    "refined_defects_002850.png"
)

OUTPUT_MASK = os.path.join(
    OUTPUT_DIR,
    "refined_defect_mask_002850.png"
)

OUTPUT_CSV = os.path.join(
    OUTPUT_DIR,
    "defect_regions_002850.csv"
)


# ============================================================
# SETTINGS
# ============================================================

THRESHOLD = 0.08

# Ignore extremely small isolated regions
MINIMUM_AREA = 20


# ============================================================
# DEVICE
# ============================================================

device = torch.device("cpu")


# ============================================================
# STEP 1 - LOAD MODEL
# ============================================================

print()
print("1. Loading AI model...")

model = WaferRestorationNet()

model.load_state_dict(
    torch.load(
        MODEL_PATH,
        map_location=device
    )
)

model.eval()

print("Model loaded successfully!")


# ============================================================
# STEP 2 - LOAD DATA
# ============================================================

print()
print("2. Loading wafer data...")

noisy = np.load(
    NOISY_PATH
).astype(np.float32)

gt = np.load(
    GT_PATH
).astype(np.float32
)

print("Noisy image shape :", noisy.shape)
print("GT image shape    :", gt.shape)


# ============================================================
# STEP 3 - PREPARE INPUT
# ============================================================

print()
print("3. Preparing input...")

input_tensor = torch.from_numpy(noisy)

input_tensor = input_tensor.unsqueeze(0).unsqueeze(0)


# ============================================================
# STEP 4 - AI RESTORATION
# ============================================================

print()
print("4. Running AI restoration...")

with torch.no_grad():

    restored = model(input_tensor)

restored = restored.squeeze().numpy()

print("Restoration completed!")


# ============================================================
# STEP 5 - CALCULATE ERROR MAP
# ============================================================

print()
print("5. Calculating restoration error...")

error_map = np.abs(
    restored - gt
)

mean_error = np.mean(error_map)

maximum_error = np.max(error_map)

print(
    "Mean absolute error : %.6f"
    % mean_error
)

print(
    "Maximum error       : %.6f"
    % maximum_error
)


# ============================================================
# STEP 6 - INITIAL DEFECT MASK
# ============================================================

print()
print("6. Creating initial defect mask...")

initial_mask = error_map > THRESHOLD

initial_pixels = np.sum(initial_mask)

print(
    "Initial defect pixels :",
    int(initial_pixels)
)


# ============================================================
# STEP 7 - REMOVE SMALL REGIONS
# ============================================================

print()
print("7. Removing small isolated regions...")

labeled_mask = label(
    initial_mask,
    connectivity=2
)

clean_mask = np.zeros_like(
    initial_mask,
    dtype=bool
)

for region in regionprops(labeled_mask):

    if region.area >= MINIMUM_AREA:

        clean_mask[
            labeled_mask == region.label
        ] = True


# ============================================================
# STEP 8 - CALCULATE FINAL STATISTICS
# ============================================================

print()
print("8. Calculating refined defect statistics...")

total_pixels = clean_mask.size

defect_pixels = np.sum(clean_mask)

suspicious_area = (
    defect_pixels /
    total_pixels
) * 100


# ============================================================
# STEP 9 - IDENTIFY INDIVIDUAL DEFECT REGIONS
# ============================================================

print()
print("9. Identifying individual defect regions...")

final_labels = label(
    clean_mask,
    connectivity=2
)

regions = regionprops(
    final_labels,
    intensity_image=error_map
)

print(
    "Detected defect regions :",
    len(regions)
)


# ============================================================
# STEP 10 - SAVE DEFECT INFORMATION
# ============================================================

print()
print("10. Saving defect information...")

with open(
    OUTPUT_CSV,
    "w",
    newline=""
) as csv_file:

    writer = csv.writer(csv_file)

    writer.writerow([
        "Defect_ID",
        "Area_pixels",
        "Min_Row",
        "Min_Column",
        "Max_Row",
        "Max_Column",
        "Centroid_Row",
        "Centroid_Column",
        "Mean_Error",
        "Maximum_Error",
        "Severity"
    ])

    for defect_id, region in enumerate(
        regions,
        start=1
    ):

        min_row, min_col, max_row, max_col = (
            region.bbox
        )

        mean_region_error = (
            region.mean_intensity
        )

        region_pixels = (
            error_map[
                final_labels == region.label
            ]
        )

        max_region_error = np.max(
            region_pixels
        )

        # ----------------------------------------
        # Severity classification
        # ----------------------------------------

        if max_region_error >= 0.20:

            severity = "HIGH"

        elif max_region_error >= 0.12:

            severity = "MEDIUM"

        else:

            severity = "LOW"

        writer.writerow([
            defect_id,
            region.area,
            min_row,
            min_col,
            max_row,
            max_col,
            "%.2f" % region.centroid[0],
            "%.2f" % region.centroid[1],
            "%.6f" % mean_region_error,
            "%.6f" % max_region_error,
            severity
        ])


print(
    "Defect CSV saved:"
)

print(
    OUTPUT_CSV
)


# ============================================================
# STEP 11 - SAVE REFINED MASK
# ============================================================

print()
print("11. Saving refined defect mask...")

plt.imsave(
    OUTPUT_MASK,
    clean_mask,
    cmap="gray"
)

print(
    "Mask saved:"
)

print(
    OUTPUT_MASK
)


# ============================================================
# STEP 12 - CREATE DEFECT VISUALIZATION
# ============================================================

print()
print("12. Creating refined defect visualization...")


fig, axes = plt.subplots(
    2,
    3,
    figsize=(16, 10)
)


# ------------------------------------------------------------
# Input
# ------------------------------------------------------------

axes[0, 0].imshow(
    noisy,
    cmap="gray"
)

axes[0, 0].set_title(
    "Input Noisy Wafer"
)

axes[0, 0].axis("off")


# ------------------------------------------------------------
# Ground Truth
# ------------------------------------------------------------

axes[0, 1].imshow(
    gt,
    cmap="gray"
)

axes[0, 1].set_title(
    "Ground Truth"
)

axes[0, 1].axis("off")


# ------------------------------------------------------------
# Restored
# ------------------------------------------------------------

axes[0, 2].imshow(
    restored,
    cmap="gray"
)

axes[0, 2].set_title(
    "AI Restored Wafer"
)

axes[0, 2].axis("off")


# ------------------------------------------------------------
# Error Map
# ------------------------------------------------------------

axes[1, 0].imshow(
    error_map,
    cmap="hot"
)

axes[1, 0].set_title(
    "Restoration Error Map"
)

axes[1, 0].axis("off")


# ------------------------------------------------------------
# Refined Mask
# ------------------------------------------------------------

axes[1, 1].imshow(
    clean_mask,
    cmap="gray"
)

axes[1, 1].set_title(
    "Refined Defect Mask"
)

axes[1, 1].axis("off")


# ------------------------------------------------------------
# Bounding Boxes
# ------------------------------------------------------------

axes[1, 2].imshow(
    gt,
    cmap="gray"
)

for defect_id, region in enumerate(
    regions,
    start=1
):

    min_row, min_col, max_row, max_col = (
        region.bbox
    )

    width = max_col - min_col
    height = max_row - min_row

    rectangle = plt.Rectangle(
        (min_col, min_row),
        width,
        height,
        fill=False,
        linewidth=2
    )

    axes[1, 2].add_patch(
        rectangle
    )

    axes[1, 2].text(
        min_col,
        min_row,
        str(defect_id),
        fontsize=10,
        backgroundcolor="white"
    )

axes[1, 2].set_title(
    "Detected Defects + Bounding Boxes"
)

axes[1, 2].axis("off")


# ============================================================
# MAIN TITLE
# ============================================================

fig.suptitle(
    "WaferRevive-AI - Refined Semiconductor Defect Detection",
    fontsize=16
)

plt.tight_layout()


# ============================================================
# SAVE FINAL IMAGE
# ============================================================

plt.savefig(
    OUTPUT_IMAGE,
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FINAL REPORT
# ============================================================

print()
print("============================================================")
print("STEP 23 - REFINED DEFECT DETECTION RESULT")
print("============================================================")

print(
    "Image                : 002850.npy"
)

print(
    "Threshold            : %.2f"
    % THRESHOLD
)

print(
    "Minimum region area  :",
    MINIMUM_AREA,
    "pixels"
)

print(
    "Mean error           : %.6f"
    % mean_error
)

print(
    "Maximum error        : %.6f"
    % maximum_error
)

print(
    "Defect pixels        :",
    int(defect_pixels)
)

print(
    "Total pixels         :",
    int(total_pixels)
)

print(
    "Suspicious area      : %.2f%%"
    % suspicious_area
)

print(
    "Defect regions       :",
    len(regions)
)

print()
print("Output files:")
print(OUTPUT_IMAGE)
print(OUTPUT_MASK)
print(OUTPUT_CSV)

print()
print("============================================================")
print("STEP 23 COMPLETED SUCCESSFULLY")
print("============================================================")