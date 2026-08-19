import os
import csv


# ============================================================
# WAFERREVIVE-AI
# STEP 28 - FINAL WAFER QUALITY SCORE
# ============================================================

print("============================================================")
print("WAFERREVIVE-AI - STEP 28")
print("FINAL WAFER QUALITY SCORE")
print("============================================================")


# ============================================================
# PATHS
# ============================================================

INPUT_CSV = (
    r"D:\WaferRevive-AI\results\defect_analysis"
    r"\ranked_defects_002850.csv"
)

OUTPUT_DIR = (
    r"D:\WaferRevive-AI\results\wafer_quality"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

SUMMARY_CSV = os.path.join(
    OUTPUT_DIR,
    "wafer_quality_score_002850.csv"
)

REPORT_TXT = os.path.join(
    OUTPUT_DIR,
    "wafer_quality_report_002850.txt"
)


# ============================================================
# STEP 1 - LOAD DEFECT DATA
# ============================================================

print()
print("1. Loading defect data...")

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
# STEP 2 - BASIC STATISTICS
# ============================================================

print()
print("2. Calculating wafer statistics...")

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

maximum_error = max(
    (
        d["Maximum_Error"]
        for d in defects
    ),
    default=0
)


# ============================================================
# STEP 3 - CALCULATE DEFECT PENALTY
# ============================================================

print()
print("3. Calculating defect penalty...")

# Each defect contributes a penalty.
# HIGH defects receive the largest penalty.

high_penalty = high_count * 12
medium_penalty = medium_count * 6
low_penalty = low_count * 2

defect_penalty = (
    high_penalty +
    medium_penalty +
    low_penalty
)


# ============================================================
# STEP 4 - CALCULATE ERROR PENALTY
# ============================================================

print()
print("4. Calculating restoration-error penalty...")

error_penalty = maximum_error * 20


# ============================================================
# STEP 5 - CALCULATE AREA PENALTY
# ============================================================

print()
print("5. Calculating defect-area penalty...")

# 65536 pixels = 256 x 256 image.
TOTAL_PIXELS = 256 * 256

area_percentage = (
    total_area /
    TOTAL_PIXELS
) * 100

area_penalty = area_percentage * 5


# ============================================================
# STEP 6 - FINAL QUALITY SCORE
# ============================================================

print()
print("6. Calculating final wafer quality score...")

raw_score = (
    100
    - defect_penalty
    - error_penalty
    - area_penalty
)

quality_score = max(
    0,
    min(
        100,
        raw_score
    )
)


# ============================================================
# STEP 7 - QUALITY GRADE
# ============================================================

print()
print("7. Assigning quality grade...")

if quality_score >= 90:

    quality_grade = "A"

elif quality_score >= 80:

    quality_grade = "B"

elif quality_score >= 70:

    quality_grade = "C"

elif quality_score >= 60:

    quality_grade = "D"

else:

    quality_grade = "F"


# ============================================================
# STEP 8 - FINAL QUALITY STATUS
# ============================================================

if high_count > 0:

    quality_status = "DEFECTIVE"

elif medium_count > 0:

    quality_status = "REVIEW REQUIRED"

elif low_count > 0:

    quality_status = "MINOR DEFECTS"

else:

    quality_status = "PASS"


# ============================================================
# STEP 9 - SAVE CSV
# ============================================================

print()
print("8. Saving wafer quality score...")

with open(
    SUMMARY_CSV,
    "w",
    newline=""
) as csv_file:

    writer = csv.writer(csv_file)

    writer.writerow([
        "Parameter",
        "Value"
    ])

    writer.writerow([
        "Quality_Score",
        "%.2f" % quality_score
    ])

    writer.writerow([
        "Quality_Grade",
        quality_grade
    ])

    writer.writerow([
        "Quality_Status",
        quality_status
    ])

    writer.writerow([
        "Total_Defects",
        total_defects
    ])

    writer.writerow([
        "High_Defects",
        high_count
    ])

    writer.writerow([
        "Medium_Defects",
        medium_count
    ])

    writer.writerow([
        "Low_Defects",
        low_count
    ])

    writer.writerow([
        "Total_Defect_Area",
        total_area
    ])

    writer.writerow([
        "Defect_Area_Percentage",
        "%.4f" % area_percentage
    ])

    writer.writerow([
        "Defect_Penalty",
        "%.4f" % defect_penalty
    ])

    writer.writerow([
        "Error_Penalty",
        "%.4f" % error_penalty
    ])

    writer.writerow([
        "Area_Penalty",
        "%.4f" % area_penalty
    ])

    writer.writerow([
        "Maximum_Error",
        "%.6f" % maximum_error
    ])


# ============================================================
# STEP 10 - SAVE HUMAN-READABLE REPORT
# ============================================================

print()
print("9. Creating wafer quality report...")

with open(
    REPORT_TXT,
    "w"
) as report:

    report.write(
        "WAFERREVIVE-AI\n"
    )

    report.write(
        "FINAL WAFER QUALITY SCORE REPORT\n"
    )

    report.write(
        "============================================================\n\n"
    )

    report.write(
        "QUALITY SCORE : %.2f / 100\n"
        % quality_score
    )

    report.write(
        "QUALITY GRADE : %s\n"
        % quality_grade
    )

    report.write(
        "QUALITY STATUS: %s\n\n"
        % quality_status
    )

    report.write(
        "INSPECTION STATISTICS\n"
    )

    report.write(
        "---------------------\n"
    )

    report.write(
        "Total defects          : %d\n"
        % total_defects
    )

    report.write(
        "HIGH defects           : %d\n"
        % high_count
    )

    report.write(
        "MEDIUM defects         : %d\n"
        % medium_count
    )

    report.write(
        "LOW defects            : %d\n"
        % low_count
    )

    report.write(
        "Total defect area      : %d pixels\n"
        % total_area
    )

    report.write(
        "Defect area percentage : %.4f%%\n"
        % area_percentage
    )

    report.write(
        "Maximum error          : %.6f\n\n"
        % maximum_error
    )

    report.write(
        "QUALITY PENALTIES\n"
    )

    report.write(
        "-----------------\n"
    )

    report.write(
        "Defect penalty : %.4f\n"
        % defect_penalty
    )

    report.write(
        "Error penalty  : %.4f\n"
        % error_penalty
    )

    report.write(
        "Area penalty   : %.4f\n\n"
        % area_penalty
    )

    report.write(
        "FINAL QUALITY SCORE\n"
    )

    report.write(
        "-------------------\n"
    )

    report.write(
        "%.2f / 100\n"
        % quality_score
    )

    report.write(
        "Grade: %s\n"
        % quality_grade
    )


# ============================================================
# STEP 11 - PRINT FINAL RESULT
# ============================================================

print()
print("============================================================")
print("STEP 28 - WAFER QUALITY RESULT")
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

print()
print(
    "Defect penalty:",
    "%.4f"
    % defect_penalty
)

print(
    "Error penalty :",
    "%.4f"
    % error_penalty
)

print(
    "Area penalty  :",
    "%.4f"
    % area_penalty
)

print()
print("Output files:")
print(SUMMARY_CSV)
print(REPORT_TXT)

print()
print("============================================================")
print("STEP 28 COMPLETED SUCCESSFULLY")
print("============================================================")