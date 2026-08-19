import os
import csv
import matplotlib.pyplot as plt


# ============================================================
# WAFERREVIVE-AI
# STEP 27 - INSPECTION DASHBOARD
# ============================================================

print("============================================================")
print("WAFERREVIVE-AI - STEP 27")
print("INSPECTION DASHBOARD")
print("============================================================")


# ============================================================
# PATHS
# ============================================================

INPUT_CSV = (
    r"D:\WaferRevive-AI\results\defect_analysis"
    r"\ranked_defects_002850.csv"
)

OUTPUT_DIR = (
    r"D:\WaferRevive-AI\results\inspection_dashboard"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

OUTPUT_IMAGE = os.path.join(
    OUTPUT_DIR,
    "inspection_dashboard_002850.png"
)


# ============================================================
# STEP 1 - LOAD DEFECT DATA
# ============================================================

print()
print("1. Loading defect analysis...")

defects = []

with open(
    INPUT_CSV,
    "r",
    newline=""
) as csv_file:

    reader = csv.DictReader(csv_file)

    for row in reader:

        defects.append({
            "Rank": int(float(row["Rank"])),
            "Defect_ID": int(float(row["Defect_ID"])),
            "Severity": row["Severity"],
            "Priority_Score":
                float(row["Priority_Score"]),
            "Area_pixels":
                int(float(row["Area_pixels"])),
            "Maximum_Error":
                float(row["Maximum_Error"])
        })


print(
    "Defects loaded :",
    len(defects)
)


# ============================================================
# STEP 2 - STATISTICS
# ============================================================

print()
print("2. Preparing dashboard statistics...")

total_defects = len(defects)

total_area = sum(
    d["Area_pixels"]
    for d in defects
)

high_count = sum(
    1
    for d in defects
    if d["Severity"] == "HIGH"
)

medium_count = sum(
    1
    for d in defects
    if d["Severity"] == "MEDIUM"
)

low_count = sum(
    1
    for d in defects
    if d["Severity"] == "LOW"
)

highest = (
    defects[0]
    if defects
    else None
)

inspection_status = (
    "DEFECTIVE"
    if high_count > 0
    else
    "REVIEW REQUIRED"
    if medium_count > 0
    else
    "MINOR DEFECTS"
    if low_count > 0
    else
    "PASS"
)


# ============================================================
# STEP 3 - CREATE DASHBOARD
# ============================================================

print()
print("3. Creating inspection dashboard...")

fig = plt.figure(
    figsize=(14, 9)
)

fig.suptitle(
    "WaferRevive-AI - Automated Wafer Inspection Dashboard",
    fontsize=20,
    fontweight="bold"
)


# ============================================================
# TOP SUMMARY
# ============================================================

ax1 = fig.add_axes(
    [0.05, 0.70, 0.90, 0.18]
)

ax1.axis("off")

ax1.text(
    0.02,
    0.70,
    "INSPECTION STATUS",
    fontsize=12,
    fontweight="bold"
)

ax1.text(
    0.02,
    0.35,
    inspection_status,
    fontsize=22,
    fontweight="bold"
)

ax1.text(
    0.30,
    0.70,
    "TOTAL DEFECTS",
    fontsize=12,
    fontweight="bold"
)

ax1.text(
    0.30,
    0.35,
    str(total_defects),
    fontsize=22,
    fontweight="bold"
)

ax1.text(
    0.50,
    0.70,
    "DEFECT AREA",
    fontsize=12,
    fontweight="bold"
)

ax1.text(
    0.50,
    0.35,
    str(total_area) + " pixels",
    fontsize=22,
    fontweight="bold"
)

ax1.text(
    0.73,
    0.70,
    "TOP DEFECT",
    fontsize=12,
    fontweight="bold"
)

ax1.text(
    0.73,
    0.35,
    "Defect " +
    str(
        highest["Defect_ID"]
        if highest
        else "None"
    ),
    fontsize=22,
    fontweight="bold"
)


# ============================================================
# SEVERITY CHART
# ============================================================

ax2 = fig.add_axes(
    [0.08, 0.38, 0.38, 0.25]
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

ax2.bar(
    severity_names,
    severity_values
)

ax2.set_title(
    "Defect Severity Distribution",
    fontweight="bold"
)

ax2.set_ylabel(
    "Number of Defects"
)


# ============================================================
# PRIORITY CHART
# ============================================================

ax3 = fig.add_axes(
    [0.55, 0.38, 0.38, 0.25]
)

ranks = [
    d["Rank"]
    for d in defects
]

scores = [
    d["Priority_Score"]
    for d in defects
]

ax3.bar(
    ranks,
    scores
)

ax3.set_title(
    "Defect Priority Ranking",
    fontweight="bold"
)

ax3.set_xlabel(
    "Rank"
)

ax3.set_ylabel(
    "Priority Score"
)

ax3.set_xticks(
    ranks
)


# ============================================================
# DEFECT TABLE
# ============================================================

ax4 = fig.add_axes(
    [0.08, 0.06, 0.84, 0.24]
)

ax4.axis("off")

table_data = []

for defect in defects:

    table_data.append([
        defect["Rank"],
        defect["Defect_ID"],
        defect["Severity"],
        "%.4f" % defect["Priority_Score"],
        defect["Area_pixels"],
        "%.6f" % defect["Maximum_Error"]
    ])


table = ax4.table(
    cellText=table_data,
    colLabels=[
        "Rank",
        "Defect",
        "Severity",
        "Priority",
        "Area",
        "Max Error"
    ],
    loc="center",
    cellLoc="center"
)

table.auto_set_font_size(
    False
)

table.set_fontsize(
    10
)

table.scale(
    1,
    1.5
)

ax4.set_title(
    "Detected Defects",
    fontweight="bold",
    pad=10
)


# ============================================================
# SAVE DASHBOARD
# ============================================================

print()
print("4. Saving dashboard image...")

plt.savefig(
    OUTPUT_IMAGE,
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FINAL OUTPUT
# ============================================================

print()
print("============================================================")
print("STEP 27 - INSPECTION DASHBOARD RESULT")
print("============================================================")

print(
    "Inspection status :",
    inspection_status
)

print(
    "Total defects     :",
    total_defects
)

print(
    "HIGH              :",
    high_count
)

print(
    "MEDIUM            :",
    medium_count
)

print(
    "LOW               :",
    low_count
)

print(
    "Total defect area :",
    total_area,
    "pixels"
)

if highest:

    print(
        "Top defect        :",
        highest["Defect_ID"]
    )

    print(
        "Top priority      :",
        "%.4f"
        % highest["Priority_Score"]
    )

print()
print("Dashboard saved:")
print(OUTPUT_IMAGE)

print()
print("============================================================")
print("STEP 27 COMPLETED SUCCESSFULLY")
print("============================================================")