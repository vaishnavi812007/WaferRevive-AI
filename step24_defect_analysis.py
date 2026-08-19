import os
import csv
import matplotlib.pyplot as plt


# ============================================================
# WAFERREVIVE-AI
# STEP 24 - DEFECT ANALYSIS & RANKING
# ============================================================

print("============================================================")
print("WAFERREVIVE-AI - STEP 24")
print("DEFECT ANALYSIS & RANKING")
print("============================================================")


# ============================================================
# PATHS
# ============================================================

INPUT_CSV = (
    r"D:\WaferRevive-AI\results\refined_defects"
    r"\defect_regions_002850.csv"
)

OUTPUT_DIR = (
    r"D:\WaferRevive-AI\results\defect_analysis"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

RANKED_CSV = os.path.join(
    OUTPUT_DIR,
    "ranked_defects_002850.csv"
)

SUMMARY_TXT = os.path.join(
    OUTPUT_DIR,
    "defect_analysis_summary_002850.txt"
)

CHART_PNG = os.path.join(
    OUTPUT_DIR,
    "defect_severity_chart_002850.png"
)


# ============================================================
# STEP 1 - LOAD STEP 23 CSV
# ============================================================

print()
print("1. Loading Step 23 defect data...")

defects = []

with open(INPUT_CSV, "r", newline="") as csv_file:

    reader = csv.DictReader(csv_file)

    for row in reader:

        defects.append({
            "Defect_ID": int(float(row["Defect_ID"])),
            "Area_pixels": int(float(row["Area_pixels"])),
            "Min_Row": int(float(row["Min_Row"])),
            "Min_Column": int(float(row["Min_Column"])),
            "Max_Row": int(float(row["Max_Row"])),
            "Max_Column": int(float(row["Max_Column"])),
            "Centroid_Row": float(row["Centroid_Row"]),
            "Centroid_Column": float(row["Centroid_Column"]),
            "Mean_Error": float(row["Mean_Error"]),
            "Maximum_Error": float(row["Maximum_Error"]),
            "Severity": row["Severity"]
        })


print("Defects loaded :", len(defects))


# ============================================================
# STEP 2 - BASIC STATISTICS
# ============================================================

print()
print("2. Calculating defect statistics...")

total_defect_area = sum(
    d["Area_pixels"]
    for d in defects
)

largest_area = max(
    (d["Area_pixels"] for d in defects),
    default=0
)

largest_error = max(
    (d["Maximum_Error"] for d in defects),
    default=0
)


# ============================================================
# STEP 3 - PRIORITY SCORE
# ============================================================

print()
print("3. Calculating defect priority scores...")

for defect in defects:

    if largest_area > 0:
        area_score = (
            defect["Area_pixels"] /
            largest_area
        )
    else:
        area_score = 0

    if largest_error > 0:
        error_score = (
            defect["Maximum_Error"] /
            largest_error
        )
    else:
        error_score = 0

    defect["Priority_Score"] = (
        0.4 * area_score +
        0.6 * error_score
    )


# ============================================================
# STEP 4 - RANK DEFECTS
# ============================================================

print()
print("4. Ranking defects...")

defects.sort(
    key=lambda x: x["Priority_Score"],
    reverse=True
)

for rank, defect in enumerate(defects, start=1):

    defect["Rank"] = rank


# ============================================================
# STEP 5 - SEVERITY DISTRIBUTION
# ============================================================

print()
print("5. Calculating severity distribution...")

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


# ============================================================
# STEP 6 - SAVE RANKED CSV
# ============================================================

print()
print("6. Saving ranked defect report...")

with open(
    RANKED_CSV,
    "w",
    newline=""
) as csv_file:

    fieldnames = [
        "Rank",
        "Defect_ID",
        "Severity",
        "Priority_Score",
        "Area_pixels",
        "Mean_Error",
        "Maximum_Error",
        "Centroid_Row",
        "Centroid_Column",
        "Min_Row",
        "Min_Column",
        "Max_Row",
        "Max_Column"
    ]

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    for defect in defects:

        writer.writerow({
            "Rank": defect["Rank"],
            "Defect_ID": defect["Defect_ID"],
            "Severity": defect["Severity"],
            "Priority_Score":
                "%.4f" %
                defect["Priority_Score"],
            "Area_pixels":
                defect["Area_pixels"],
            "Mean_Error":
                "%.6f" %
                defect["Mean_Error"],
            "Maximum_Error":
                "%.6f" %
                defect["Maximum_Error"],
            "Centroid_Row":
                "%.2f" %
                defect["Centroid_Row"],
            "Centroid_Column":
                "%.2f" %
                defect["Centroid_Column"],
            "Min_Row":
                defect["Min_Row"],
            "Min_Column":
                defect["Min_Column"],
            "Max_Row":
                defect["Max_Row"],
            "Max_Column":
                defect["Max_Column"]
        })


# ============================================================
# STEP 7 - CREATE TEXT SUMMARY
# ============================================================

print()
print("7. Creating analysis summary...")

with open(
    SUMMARY_TXT,
    "w"
) as file:

    file.write(
        "WAFERREVIVE-AI - STEP 24\n"
    )

    file.write(
        "DEFECT ANALYSIS & RANKING\n"
    )

    file.write(
        "========================================\n\n"
    )

    file.write(
        "Total defects detected : %d\n"
        % len(defects)
    )

    file.write(
        "Total defect area      : %d pixels\n"
        % total_defect_area
    )

    file.write(
        "HIGH severity          : %d\n"
        % high_count
    )

    file.write(
        "MEDIUM severity        : %d\n"
        % medium_count
    )

    file.write(
        "LOW severity           : %d\n\n"
        % low_count
    )

    file.write(
        "DEFECT PRIORITY RANKING\n"
    )

    file.write(
        "----------------------------------------\n"
    )

    for defect in defects:

        file.write(
            "Rank %d | Defect %d | %s | "
            "Score %.4f | Area %d | "
            "Max Error %.6f\n"
            % (
                defect["Rank"],
                defect["Defect_ID"],
                defect["Severity"],
                defect["Priority_Score"],
                defect["Area_pixels"],
                defect["Maximum_Error"]
            )
        )


# ============================================================
# STEP 8 - CREATE SEVERITY CHART
# ============================================================

print()
print("8. Creating severity chart...")

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

plt.figure(figsize=(8, 5))

plt.bar(
    severity_names,
    severity_values
)

plt.title(
    "WaferRevive-AI - Defect Severity Distribution"
)

plt.xlabel("Severity")

plt.ylabel("Number of Defects")

plt.tight_layout()

plt.savefig(
    CHART_PNG,
    dpi=200
)

plt.close()


# ============================================================
# STEP 9 - FINAL REPORT
# ============================================================

print()
print("============================================================")
print("STEP 24 - DEFECT ANALYSIS RESULT")
print("============================================================")

print(
    "Total defects     :",
    len(defects)
)

print(
    "Total defect area :",
    total_defect_area,
    "pixels"
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

print()
print("DEFECT PRIORITY RANKING")
print("-----------------------")

for defect in defects:

    print(
        "Rank %d | Defect %d | %s | "
        "Score %.4f | Area %d | Max Error %.6f"
        % (
            defect["Rank"],
            defect["Defect_ID"],
            defect["Severity"],
            defect["Priority_Score"],
            defect["Area_pixels"],
            defect["Maximum_Error"]
        )
    )

print()
print("Output files:")
print(RANKED_CSV)
print(SUMMARY_TXT)
print(CHART_PNG)

print()
print("============================================================")
print("STEP 24 COMPLETED SUCCESSFULLY")
print("============================================================")