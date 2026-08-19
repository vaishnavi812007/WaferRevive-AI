import os
import csv
import matplotlib.pyplot as plt


# ============================================================
# WAFERREVIVE-AI
# STEP 29 - QUALITY VISUALIZATION
# ============================================================

print("============================================================")
print("WAFERREVIVE-AI - STEP 29")
print("QUALITY VISUALIZATION")
print("============================================================")


# ============================================================
# PATHS
# ============================================================

INPUT_CSV = (
    r"D:\WaferRevive-AI\results\wafer_quality"
    r"\wafer_quality_score_002850.csv"
)

OUTPUT_DIR = (
    r"D:\WaferRevive-AI\results\quality_visualization"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

OUTPUT_IMAGE = os.path.join(
    OUTPUT_DIR,
    "wafer_quality_visualization_002850.png"
)


# ============================================================
# STEP 1 - LOAD QUALITY DATA
# ============================================================

print()
print("1. Loading Step 28 quality data...")

data = {}

with open(
    INPUT_CSV,
    "r",
    newline=""
) as csv_file:

    reader = csv.DictReader(csv_file)

    for row in reader:

        data[row["Parameter"]] = row["Value"]


quality_score = float(
    data["Quality_Score"]
)

quality_grade = data[
    "Quality_Grade"
]

quality_status = data[
    "Quality_Status"
]

total_defects = int(
    float(data["Total_Defects"])
)

high_count = int(
    float(data["High_Defects"])
)

medium_count = int(
    float(data["Medium_Defects"])
)

low_count = int(
    float(data["Low_Defects"])
)

total_area = int(
    float(data["Total_Defect_Area"])
)

area_percentage = float(
    data["Defect_Area_Percentage"]
)


print(
    "Quality score :",
    quality_score
)

print(
    "Quality grade :",
    quality_grade
)

print(
    "Quality status:",
    quality_status
)


# ============================================================
# STEP 2 - CREATE VISUALIZATION
# ============================================================

print()
print("2. Creating quality visualization...")

fig = plt.figure(
    figsize=(12, 8)
)

fig.suptitle(
    "WaferRevive-AI - Final Wafer Quality Assessment",
    fontsize=20,
    fontweight="bold"
)


# ============================================================
# QUALITY SCORE
# ============================================================

ax1 = fig.add_axes(
    [0.08, 0.55, 0.38, 0.30]
)

ax1.set_xlim(
    0,
    100
)

ax1.set_ylim(
    0,
    1
)

ax1.barh(
    [0.5],
    [100],
    height=0.25
)

ax1.barh(
    [0.5],
    [quality_score],
    height=0.25
)

ax1.text(
    quality_score / 2,
    0.5,
    "%.2f / 100" % quality_score,
    ha="center",
    va="center",
    fontsize=18,
    fontweight="bold"
)

ax1.set_title(
    "Overall Quality Score",
    fontweight="bold"
)

ax1.set_yticks([])

ax1.set_xlabel(
    "Quality Score"
)


# ============================================================
# QUALITY INFORMATION
# ============================================================

ax2 = fig.add_axes(
    [0.55, 0.55, 0.37, 0.30]
)

ax2.axis("off")

ax2.text(
    0.05,
    0.78,
    "FINAL STATUS",
    fontsize=12,
    fontweight="bold"
)

ax2.text(
    0.05,
    0.58,
    quality_status,
    fontsize=22,
    fontweight="bold"
)

ax2.text(
    0.05,
    0.38,
    "QUALITY GRADE",
    fontsize=12,
    fontweight="bold"
)

ax2.text(
    0.05,
    0.18,
    quality_grade,
    fontsize=22,
    fontweight="bold"
)


# ============================================================
# DEFECT SEVERITY
# ============================================================

ax3 = fig.add_axes(
    [0.08, 0.12, 0.38, 0.28]
)

severity_names = [
    "HIGH",
    "MEDIUM",
    "LOW"
]

severity_values = [
    high_count,
    medium_count,
    low_count
]

ax3.bar(
    severity_names,
    severity_values
)

ax3.set_title(
    "Defect Severity Distribution",
    fontweight="bold"
)

ax3.set_ylabel(
    "Number of Defects"
)


# ============================================================
# INSPECTION STATISTICS
# ============================================================

ax4 = fig.add_axes(
    [0.55, 0.12, 0.37, 0.28]
)

ax4.axis("off")

ax4.text(
    0.05,
    0.85,
    "INSPECTION STATISTICS",
    fontsize=12,
    fontweight="bold"
)

ax4.text(
    0.05,
    0.65,
    "Total defects : %d"
    % total_defects,
    fontsize=14
)

ax4.text(
    0.05,
    0.50,
    "Defect area   : %d pixels"
    % total_area,
    fontsize=14
)

ax4.text(
    0.05,
    0.35,
    "Area ratio    : %.4f%%"
    % area_percentage,
    fontsize=14
)

ax4.text(
    0.05,
    0.20,
    "HIGH defects  : %d"
    % high_count,
    fontsize=14
)


# ============================================================
# SAVE
# ============================================================

print()
print("3. Saving quality visualization...")

plt.savefig(
    OUTPUT_IMAGE,
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("============================================================")
print("STEP 29 - QUALITY VISUALIZATION RESULT")
print("============================================================")

print(
    "Quality score :",
    "%.2f / 100"
    % quality_score
)

print(
    "Quality grade :",
    quality_grade
)

print(
    "Quality status:",
    quality_status
)

print(
    "Total defects :",
    total_defects
)

print()
print("Visualization saved:")
print(OUTPUT_IMAGE)

print()
print("============================================================")
print("STEP 29 COMPLETED SUCCESSFULLY")
print("============================================================")